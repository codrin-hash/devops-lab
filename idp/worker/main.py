import logging
import os
import shutil
import signal
import subprocess
import threading
import uuid
from pathlib import Path

import docker
from sqlalchemy import select

from common import queue
from common.config import settings
from common.db import SessionLocal
from common.models import App, Deployment, DeployStatus
from worker import builder, health, runner

log = logging.getLogger("worker")
WORKSPACE = Path(settings.workspace_dir)
CLONE_TIMEOUT = 120
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}  # never block waiting for credentials

stop = threading.Event()
docker_client: docker.DockerClient | None = None


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
        shutil.rmtree(dest)  # at-least-once delivery: a retried job may find a partial clone
    subprocess.run(
        ["git", "clone", "--depth=1", f"--branch={branch}", "--", repo_url, str(dest)],
        check=True, capture_output=True, text=True, timeout=CLONE_TIMEOUT, env=GIT_ENV,
    )
    out = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True, env=GIT_ENV,
    )
    return out.stdout.strip()


def promote(dep_id: uuid.UUID, app_id: uuid.UUID, container_id: str, port: int) -> list[str]:
    """One commit marks the new deployment running and the previous ones stopped."""
    with SessionLocal() as s:
        previous = s.scalars(
            select(Deployment)
            .where(Deployment.app_id == app_id,
                   Deployment.status == DeployStatus.running,
                   Deployment.id != dep_id)
            .with_for_update()
        ).all()
        old_ids = [d.container_id for d in previous if d.container_id]
        for d in previous:
            d.status = DeployStatus.stopped
        dep = s.get(Deployment, dep_id)
        dep.status, dep.container_id, dep.host_port = DeployStatus.running, container_id, port
        s.commit()
    log.info("deployment %s -> running on :%d, superseded %d", dep_id, port, len(old_ids))
    return old_ids


def process(dep_id: uuid.UUID) -> None:
    with SessionLocal() as s:
        dep = s.get(Deployment, dep_id)
        if dep is None:
            log.warning("deployment %s not found, dropping", dep_id)
            return
        app = s.get(App, dep.app_id)
        app_id, app_name, repo_url, branch = app.id, app.name, app.repo_url, app.branch

    workdir = WORKSPACE / str(dep_id)
    try:
        set_status(dep_id, DeployStatus.cloning)
        try:
            sha = clone(repo_url, branch, workdir)
        except subprocess.CalledProcessError as e:
            set_status(dep_id, DeployStatus.failed, error=(e.stderr or "")[-2000:])
            return
        except subprocess.TimeoutExpired:
            set_status(dep_id, DeployStatus.failed, error=f"clone timed out after {CLONE_TIMEOUT}s")
            return

        tag = f"idp/{app_name}:{sha}"
        set_status(dep_id, DeployStatus.building, commit_sha=sha, image=tag)
        try:
            built = builder.build(docker_client, workdir, tag)
        except builder.BuildError as e:
            set_status(dep_id, DeployStatus.failed, error=str(e))
            return
        log.info("%s %s", "built" if built else "reusing existing image", tag)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)  # workspace is not kept after build

    set_status(dep_id, DeployStatus.starting)
    c = runner.start(docker_client, app_id=app_id, app_name=app_name, dep_id=dep_id, image=tag)
    try:
        port = runner.host_port(c)
        health.wait_ready(c, f"http://{c.name}:{settings.app_port}/", settings.health_timeout)
    except Exception as e:
        tail = runner.logs_tail(c)
        runner.remove(c)
        set_status(dep_id, DeployStatus.failed,
                   error=f"{str(e)[:500]}\n--- last log lines ---\n{tail[-1500:]}")
        return

    for old in promote(dep_id, app_id, c.id, port):
        runner.stop_and_remove(docker_client, old)


def _request_stop(signum, _frame) -> None:
    log.info("received %s, finishing current job then exiting", signal.Signals(signum).name)
    stop.set()


def main() -> None:
    global docker_client
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    signal.signal(signal.SIGTERM, _request_stop)
    signal.signal(signal.SIGINT, _request_stop)
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    docker_client = docker.from_env()
    log.info("docker engine %s", docker_client.version()["Version"])
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