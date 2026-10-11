import logging
import time
import uuid

import docker
from docker.errors import NotFound
from docker.models.containers import Container

from common.config import settings

log = logging.getLogger("worker.runner")


def container_name(app_name: str, dep_id: uuid.UUID) -> str:
    return f"idp-{app_name}-{str(dep_id)[:8]}"


def start(client: docker.DockerClient, *, app_id: uuid.UUID, app_name: str,
          dep_id: uuid.UUID, image: str) -> Container:
    return client.containers.run(
        image,
        name=container_name(app_name, dep_id),
        detach=True,
        environment={"PORT": str(settings.app_port)},
        ports={f"{settings.app_port}/tcp": None},  # Docker picks a free host port
        network=settings.apps_network,
        labels={
            "idp.managed": "true",
            "idp.app_id": str(app_id),
            "idp.deployment_id": str(dep_id),
        },
        init=True,
        mem_limit=settings.app_mem_limit,
        nano_cpus=settings.app_nano_cpus,
        pids_limit=settings.app_pids_limit,
        restart_policy={"Name": "no"},
    )


def host_port(c: Container) -> int:
    c.reload()
    bindings = c.ports.get(f"{settings.app_port}/tcp") or []
    if not bindings:
        raise RuntimeError("no host port published")
    return int(bindings[0]["HostPort"])


def logs_tail(c: Container, lines: int = 30) -> str:
    try:
        return c.logs(tail=lines).decode(errors="replace")
    except NotFound:
        return ""


def remove(c: Container) -> None:
    try:
        c.remove(force=True)
    except NotFound:
        pass


def stop_and_remove(client: docker.DockerClient, container_id: str, timeout: int = 10) -> None:
    try:
        c = client.containers.get(container_id)
    except NotFound:
        log.warning("container %s already gone", container_id[:12])
        return
    t0 = time.monotonic()
    c.stop(timeout=timeout)  # SIGTERM, SIGKILL after timeout
    log.info("stopped %s in %.2fs", c.name, time.monotonic() - t0)
    c.remove()