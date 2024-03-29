"""Initialize the fastapi_redis_cache package."""

from fastapi_redis_cache.cache import (
    cache,
    cache_one_day,
    cache_one_hour,
    cache_one_minute,
    cache_one_month,
    cache_one_week,
    cache_one_year,
)
from fastapi_redis_cache.client import FastApiRedisCache

__all__ = [
    "cache",
    "cache_one_day",
    "cache_one_hour",
    "cache_one_minute",
    "cache_one_month",
    "cache_one_week",
    "cache_one_year",
    "FastApiRedisCache",
]
