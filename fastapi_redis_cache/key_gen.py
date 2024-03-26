"""Helper functions for generating cache keys."""

from __future__ import annotations

from inspect import Signature, signature
from typing import TYPE_CHECKING, Any, Callable

from fastapi import Request, Response

if TYPE_CHECKING:  # pragma: no cover
    from collections import OrderedDict

    from fastapi_redis_cache.types import ArgType, SigParameters

ALWAYS_IGNORE_ARG_TYPES = [Response, Request]


def get_cache_key(  # noqa: D417
    prefix: str,
    tag: str | None,
    ignore_arg_types: list[ArgType],
    func: Callable[..., Any],
    *args: list[Any],
    **kwargs: dict[Any, Any],
) -> str:
    """Generate a key to uniquely identify the function and values of arguments.

    Args:
        prefix (`str`): Customizable namespace value that will prefix all cache
            keys.
        tag (`str`): Customizable tag value that will be inserted into the
            cache key. This can be used to group related keys together or to
            help expire a key in other routes.
        ignore_arg_types (`list[ArgType]`): Each argument to the API endpoint
            function is used to compose the cache key by calling `str(arg)`. If
            there are any keys that should not be used in this way (i.e.,
            because their value has no effect on the response, such as a
            `Request` or `Response` object) you can remove them from the cache
            key by including their type as a list item in ignore_key_types.
        func (`Callable`): Path operation function for an API endpoint.

    Returns:
        `str`: Unique identifier for `func`, `*args` and `**kwargs` that can be
            used as a Redis key to retrieve cached API response data.
    """
    if not ignore_arg_types:
        ignore_arg_types = []
    ignore_arg_types.extend(ALWAYS_IGNORE_ARG_TYPES)
    ignore_arg_types = list(set(ignore_arg_types))
    prefix = f"{prefix}:" if prefix else ""
    tag_string = f"::{tag}" if tag else ""

    sig = signature(func)
    sig_params = sig.parameters
    func_args = get_func_args(sig, *args, **kwargs)
    args_str = get_args_str(sig_params, func_args, ignore_arg_types)
    return f"{prefix}{func.__module__}.{func.__name__}({args_str}){tag_string}"


def get_func_args(
    sig: Signature, *args: list[Any], **kwargs: dict[Any, Any]
) -> OrderedDict[str, Any]:
    """Return a dict object containing name and value of function arguments."""
    func_args = sig.bind(*args, **kwargs)
    func_args.apply_defaults()
    return func_args.arguments


def get_args_str(
    sig_params: SigParameters,
    func_args: OrderedDict[str, Any],
    ignore_arg_types: list[ArgType],
) -> str:
    """Return a string with name and value of all args.

    Ignores those whose type is included in `ignore_arg_types`
    """
    return ",".join(
        f"{arg}={val}"
        for arg, val in func_args.items()
        if sig_params[arg].annotation not in ignore_arg_types
    )
