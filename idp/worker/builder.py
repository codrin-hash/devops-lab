import subprocess
from pathlib import Path

import docker
from docker.errors import ImageNotFound

from common.config import settings


class BuildError(Exception):
    pass


def image_exists(client: docker.DockerClient, tag: str) -> bool:
    try:
        client.images.get(tag)
        return True
    except ImageNotFound:
        return False


def build(client: docker.DockerClient, context: Path, tag: str) -> bool:
    """Build the image. Returns False if an image with this tag already exists (D3)."""
    if image_exists(client, tag):
        return False
    if not (context / "Dockerfile").is_file():
        raise BuildError("no Dockerfile in repository root")
    try:
        p = subprocess.run(
            ["docker", "build", "--tag", tag, "--label", "idp.managed=true", "--progress=plain", str(context)],
            capture_output=True, text=True, timeout=settings.build_timeout,
        )
    except subprocess.TimeoutExpired:
        raise BuildError(f"build timed out after {settings.build_timeout}s")
    if p.returncode != 0:
        raise BuildError(p.stderr[-2000:])  # BuildKit writes progress and errors to stderr
    return True