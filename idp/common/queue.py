import redis

from common.config import settings

QUEUE = "idp:queue"
PROCESSING = "idp:processing"

r = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue(deployment_id: str) -> None:
    r.lpush(QUEUE, deployment_id)


def dequeue(timeout: int = 1) -> str | None:
    # the id moves to 'PROCESSING' and stays there until ack().
    # if the worker dies before ack, the id is not lost, but nobody recovers it yet (GAP-001).
    return r.blmove(QUEUE, PROCESSING, timeout, "RIGHT", "LEFT")


def ack(deployment_id: str) -> None:
    r.lrem(PROCESSING, 1, deployment_id)