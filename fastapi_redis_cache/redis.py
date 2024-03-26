"""Helper function to connect to Redis and return a Redis client instance."""

import os

import redis
from fakeredis import FakeRedis

from fastapi_redis_cache.enums import RedisStatus
from fastapi_redis_cache.types import RedisConnectType


def redis_connect(host_url: str) -> RedisConnectType:
    """Attempt to connect to `host_url`.

    Return a Redis client instance if successful.
    """
    return (
        _connect(host_url)
        if os.environ.get("CACHE_ENV") != "TEST"
        else _connect_fake()
    )


def _connect(host_url: str) -> RedisConnectType:
    """Connect and return a Redis client instance."""
    try:
        redis_client = redis.from_url(host_url)
        if redis_client.ping():
            return (RedisStatus.CONNECTED, redis_client)
    except redis.AuthenticationError:
        return (RedisStatus.AUTH_ERROR, None)
    except redis.ConnectionError:
        return (RedisStatus.CONN_ERROR, None)
    else:
        return (RedisStatus.CONN_ERROR, None)


def _connect_fake() -> tuple[RedisStatus, FakeRedis]:
    """Return a FakeRedis instance for testing purposes."""
    return (RedisStatus.CONNECTED, FakeRedis())
