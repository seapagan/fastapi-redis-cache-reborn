"""Define some helpful type aliases."""

from collections.abc import Mapping
from inspect import Parameter
from typing import Union

import redis

from fastapi_redis_cache.enums import RedisStatus

ArgType = type[object]
SigParameters = Mapping[str, Parameter]

RedisConnectType = tuple[
    RedisStatus,
    Union[redis.client.Redis, None],  # type: ignore
]
