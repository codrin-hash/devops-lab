import logging
import os
import shutil
import subprocess
import uuid
from pathlib import Path
import signal
import threading

from common import queue
from common.config import settings
from common.db import SessionLocal
from common.models import App, Deployment, DeployStatus

log = logging.getLogger("worker")
WORKSPACE = Path(settings.workspace_dir)
CLONE_TIMEOUT = 120

# never block waiting for credentials
# not existing/private repo falls through
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def set_status(dep_id: uuid.UUID, status: DeployStatus, **fields) -> None:
    with SessionLocal() as s:
        dep = s.get(Deployment, dep_id)
        dep.status = status
        for k, v in fields.items():
            setattr(dep, k, v)
        s.commit()
    log.info("deployment %s -> %s", dep_id, status.value)


def clone(repo_url: str, branch: str, dest: Path) -> str:
    if dest.exists():
        shutil.rmtree(dest)  # at-least-once delivery(a retried job may find a partial clone)
    subprocess.run(
        ["git", "clone", "--depth=1", f"--branch={branch}", "--", repo_url, str(dest)],
        check=True, capture_output=True, text=True, timeout=CLONE_TIMEOUT, env=GIT_ENV,
    )
    out = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True, env=GIT_ENV,
    )
    return out.stdout.strip()


def process(dep_id: uuid.UUID) -> None:
    with SessionLocal() as s:
        dep = s.get(Deployment, dep_id)
        if dep is None:
            log.warning("deployment %s not found, dropping", dep_id)
            return
        app = s.get(App, dep.app_id)
        repo_url, branch = app.repo_url, app.branch

    set_status(dep_id, DeployStatus.cloning)
    try:
        sha = clone(repo_url, branch, WORKSPACE / str(dep_id))
    except subprocess.CalledProcessError as e:
        set_status(dep_id, DeployStatus.failed, error=(e.stderr or "")[-2000:])
        return
    except subprocess.TimeoutExpired:
        set_status(dep_id, DeployStatus.failed, error=f"clone timed out after {CLONE_TIMEOUT}s")
        return

    # IDP-3: build + run, until then the pipeline stops here.
    set_status(dep_id, DeployStatus.building, commit_sha=sha)

stop = threading.Event()


def _request_stop(signum, _frame) -> None:
    log.info("received %s, finishing current job then exiting", signal.Signals(signum).name)
    stop.set()

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    signal.signal(signal.SIGTERM, _request_stop)
    signal.signal(signal.SIGINT, _request_stop)
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    log.info("worker started, workspace=%s", WORKSPACE)
    while not stop.is_set():
        job = queue.dequeue()
        if job is None:
            continue
        log.info("picked %s", job)
        try:
            process(uuid.UUID(job))
        except Exception as e:
            log.exception("deployment %s crashed", job)
            try:
                set_status(uuid.UUID(job), DeployStatus.failed, error=f"{type(e).__name__}: {e}"[:2000])
            except Exception:
                log.exception("could not mark %s as failed", job)
        finally:
            queue.ack(job)
    log.info("worker stopped")


if __name__ == "__main__":
    main()