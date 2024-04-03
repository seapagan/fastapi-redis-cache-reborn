"""Dummy FastAPI app to test the cache decorator and functionality.

This is similar to the main.py file in the tests directory, but using a real
live Redis server instead of a fake one.
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Union

from fastapi import FastAPI, Request, Response

from fastapi_redis_cache import (
    FastApiRedisCache,
    cache,
    cache_one_hour,
    cache_one_minute,
    expires,
)

REDIS_SERVER_URL = "redis://127.0.0.1:"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    """Configure the cache and yield the app."""
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=os.environ.get("REDIS_URL", REDIS_SERVER_URL),
        prefix="myapi-cache",
        response_header="X-MyAPI-Cache",
        ignore_arg_types=[Request, Response],
    )
    yield


app = FastAPI(title="FastAPI Redis Cache Test App", lifespan=lifespan)


@app.get("/cache_never_expire")
@cache()
def cache_never_expire(
    request: Request, response: Response
) -> dict[str, Union[bool, str]]:
    """Route where the cache never expires (actually is one year)."""
    return {"success": True, "message": "this data can be cached indefinitely"}


@app.get("/cache_expires")
@cache(expire=timedelta(seconds=5), tag="test_tag_1")
async def cache_expires() -> dict[str, Union[bool, str]]:
    """Route where the cache expires after 5 seconds."""
    return {
        "success": True,
        "message": "this data should be cached for five seconds",
    }


@app.get("/cache_json_encoder")
@cache(tag="test_tag_1")
def cache_json_encoder() -> (
    dict[str, Union[bool, str, datetime, date, Decimal]]
):
    """Route that returns a dictionary with different data types.

    This has the default cache time of 1 year.
    """
    return {
        "success": True,
        "start_time": datetime(2021, 4, 20, 7, 17, 17, tzinfo=timezone.utc),
        "finish_by": date(2021, 4, 21),
        "final_calc": Decimal(3.14),
    }


@app.get("/cache_one_hour")
@cache_one_hour(tag="test_tag_2")
def partial_cache_one_hour(response: Response) -> dict[str, Union[bool, str]]:
    """Route where the cache expires after one hour."""
    return {
        "success": True,
        "message": "this data should be cached for one hour",
    }


@app.get("/cache_invalid_type", response_model=None)
@cache_one_minute()
def cache_invalid_type(request: Request, response: Response) -> logging.Logger:
    """Route that returns a type that cannot be cached."""
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger


@app.get("/cache_with_args/{user}")
@cache_one_hour(tag="user_tag")
def cache_with_args(user: int) -> dict[str, Union[bool, str]]:
    """Have a varying cache key based on the user argument."""
    return {
        "success": True,
        "message": f"this data is for user {user}",
    }


@app.put("/cache_with_args/{user}")
@expires(tag="user_tag")
def put_cache_with_args(user: int) -> dict[str, Union[bool, str]]:
    """Put request to change data for a specific user."""
    return {
        "success": True,
        "message": f"New data for User {user}",
    }
