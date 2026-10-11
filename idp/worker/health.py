import socket
import time
import urllib.error
import urllib.request

from docker.models.containers import Container


class HealthError(Exception):
    pass


def wait_ready(c: Container, url: str, deadline_s: int,
               interval: float = 0.5, attempt_timeout: float = 2.0) -> None:
    deadline = time.monotonic() + deadline_s
    last = "no attempt"
    while True:
        c.reload()
        if c.status in ("exited", "dead"):
            raise HealthError(f"container exited with code {c.attrs['State']['ExitCode']}")
        try:
            with urllib.request.urlopen(url, timeout=attempt_timeout):
                return
        except urllib.error.HTTPError as e:
            if e.code < 500:
                return
            last = f"HTTP {e.code}"
        except (urllib.error.URLError, ConnectionError, socket.timeout, TimeoutError) as e:
            last = f"{type(e).__name__}: {getattr(e, 'reason', e)}"
        if time.monotonic() >= deadline:
            raise HealthError(f"not ready after {deadline_s}s, last error: {last}")
        time.sleep(interval)