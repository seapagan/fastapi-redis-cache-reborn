"""Define the FastApiRedisCache class for caching API responses in Redis."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Optional,
    Union,
)

import tzlocal

from fastapi_redis_cache.enums import RedisEvent, RedisStatus
from fastapi_redis_cache.key_gen import get_cache_key
from fastapi_redis_cache.redis import redis_connect
from fastapi_redis_cache.util import serialize_json

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request, Response
    from redis import client

DEFAULT_RESPONSE_HEADER = "X-FastAPI-Cache"
ALLOWED_HTTP_TYPES = ["GET"]
LOG_TIMESTAMP = "%m/%d/%Y %H:%M:%S %Z"
HTTP_TIME = "%a, %d %b %Y %H:%M:%S GMT"

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MetaSingleton(type):
    """Metaclass for creating singleton classes.

    These are classes that allow only a single instance to be created.
    (seapagan): Not happy about my type-hinting here, will re-visit later.
    """

    _instances: ClassVar[dict[type[Any], Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Return the instance of the class.

        if it already exists then return that,otherwise create it and return.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class FastApiRedisCache(metaclass=MetaSingleton):
    """Communicates with Redis server to cache API response data."""

    host_url: str
    prefix: str = ""
    response_header: str = ""
    status: RedisStatus = RedisStatus.NONE
    redis: client.Redis | None = None  # type: ignore

    @property
    def connected(self) -> bool:
        """Return True if the Redis client is connected to a server."""
        return self.status == RedisStatus.CONNECTED

    @property
    def not_connected(self) -> bool:
        """Return True if the Redis client is not connected to a server."""
        return not self.connected

    def init(
        self,
        host_url: str,
        prefix: str = "",
        response_header: Optional[str] = None,
        ignore_arg_types: Optional[list[type[object]]] = None,
    ) -> None:
        """Connect to a Redis database using `host_url` and configure cache.

        Args:
            host_url (str): URL for a Redis database.
            prefix (str, optional): Prefix to add to every cache key stored in
                the Redis database. Defaults to None.
            response_header (str, optional): Name of the custom header field
                used to identify cache hits/misses. Defaults to None.
            ignore_arg_types (list[Type[object]], optional): Each argument to
                the API endpoint function is used to compose the cache key. If
                there are any arguments that have no effect on the response
                (such as a `Request` or `Response` object), including their type
                in this list will ignore those arguments when the key is
                created. Defaults to None.
        """
        self.host_url = host_url
        self.prefix = prefix
        self.response_header = response_header or DEFAULT_RESPONSE_HEADER
        self.ignore_arg_types = ignore_arg_types or []
        self._connect()

    def _connect(self) -> None:
        self.log(
            RedisEvent.CONNECT_BEGIN,
            msg="Attempting to connect to Redis server...",
        )
        self.status, self.redis = redis_connect(self.host_url)
        if self.status == RedisStatus.CONNECTED:
            self.log(
                RedisEvent.CONNECT_SUCCESS,
                msg="Redis client is connected to server.",
            )
        if self.status == RedisStatus.AUTH_ERROR:  # pragma: no cover
            self.log(
                RedisEvent.CONNECT_FAIL,
                msg=(
                    "Unable to connect to redis server due to authentication "
                    "error."
                ),
            )
        if self.status == RedisStatus.CONN_ERROR:  # pragma: no cover
            self.log(
                RedisEvent.CONNECT_FAIL,
                msg="Redis server did not respond to PING message.",
            )

    def request_is_not_cacheable(self, request: Request) -> bool:
        """Return True if the request is not cacheable."""
        return bool(request) and (
            request.method not in ALLOWED_HTTP_TYPES
            or any(
                directive in request.headers.get("Cache-Control", "")
                for directive in ["no-store", "no-cache"]
            )
        )

    def get_cache_key(
        self,
        tag: str | None,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Return a key to use for caching the response of a function."""
        return get_cache_key(
            self.prefix, tag, self.ignore_arg_types, func, *args, **kwargs
        )

    def add_key_to_tag_set(self, tag: str, key: str) -> None:
        """Add a key to a set of keys associated with a tag.

        Searching for keys to invalidate is faster when they are grouped by tag
        as it reduces the number of keys to search through.

        However, keys are not removed from the tag set when they expire so will
        need to handle possibly stale keys when invalidating.
        """
        if self.redis:
            self.redis.sadd(tag, key)

    def get_tagged_keys(self, tag: str) -> set[str]:
        """Return a set of keys associated with a tag."""
        return self.redis.smembers(tag) if self.redis else set()

    def check_cache(self, key: str) -> tuple[int, str]:
        """Check if `key` is in the cache and return its TTL and value."""
        if not self.redis:
            # This should not get here if self.redis is still None, but is added
            # to satisfy mypy until I can refactor the code to fix this.
            return (0, "")

        pipe = self.redis.pipeline()
        ttl, in_cache = pipe.ttl(key).get(key).execute()
        if in_cache:
            self.log(RedisEvent.KEY_FOUND_IN_CACHE, key=key)
        return (ttl, in_cache)

    def requested_resource_not_modified(
        self, request: Request, cached_data: str
    ) -> bool:
        """Return True if the requested resource has not been modified."""
        if not request or "If-None-Match" not in request.headers:
            return False
        check_etags = [
            etag.strip()
            for etag in request.headers["If-None-Match"].split(",")
            if etag
        ]
        if len(check_etags) == 1 and check_etags[0] == "*":
            return True
        return self.get_etag(cached_data) in check_etags

    def add_to_cache(self, key: str, value: Any, expire: int) -> bool:
        """Add `value` to the cache using `key` and set an expiration time."""
        # quick hack to satisfy mypy until I can refactor the code to fix this
        if not self.redis:
            return False

        response_data = None
        try:
            response_data = serialize_json(value)
        except TypeError:
            message = f"Object of type {type(value)} is not JSON-serializable"
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, msg=message, key=key)
            return False
        cached = self.redis.set(name=key, value=response_data, ex=expire)
        if not cached:
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, key=key, value=value)
            return False

        self.log(RedisEvent.KEY_ADDED_TO_CACHE, key=key)
        return cached

    def set_response_headers(
        self,
        response: Response,
        cache_hit: bool,  # noqa: FBT001
        response_data: dict[str, Any] | None = None,
        ttl: float | None = None,
    ) -> None:
        """Set headers for the response to indicate cache status and TTL."""
        response.headers[self.response_header] = "Hit" if cache_hit else "Miss"
        expires_at = datetime.now(tz=timezone.utc) + timedelta(
            seconds=ttl or 0.0
        )
        response.headers["Expires"] = expires_at.strftime(HTTP_TIME)
        response.headers["Cache-Control"] = f"max-age={ttl}"
        if response_data:
            response.headers["ETag"] = self.get_etag(response_data)
            if "last_modified" in response_data:
                response.headers["Last-Modified"] = response_data[
                    "last_modified"
                ]

    def log(
        self,
        event: RedisEvent,
        msg: Optional[str] = None,
        key: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        """Log `RedisEvent` using the configured `Logger` object."""
        message = f" {self.get_log_time()} | {event.name}"
        if msg:
            message += f": {msg}"
        if key:
            message += f": key={key}"
        if value:  # pragma: no cover
            message += f", value={value}"
        logger.info(message)

    @staticmethod
    def get_etag(cached_data: Union[str, bytes, dict[str, Any]]) -> str:
        """Return the etag."""
        if isinstance(cached_data, bytes):
            cached_data = cached_data.decode()
        if not isinstance(cached_data, str):
            cached_data = serialize_json(cached_data)
        return f"W/{hash(cached_data)}"

    @staticmethod
    def get_log_time() -> str:
        """Get a timestamp to include with a log message."""
        local_tz = tzlocal.get_localzone()
        return datetime.now(local_tz).strftime(LOG_TIMESTAMP)
