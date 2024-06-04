# fastapi-redis-cache-reborn <!-- omit in toc -->

![PyPI - Version](https://img.shields.io/pypi/v/fastapi-redis-cache-reborn)
![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/fastapi-redis-cache-reborn)
[![Tests](https://github.com/seapagan/fastapi-redis-cache-reborn/actions/workflows/tests.yml/badge.svg)](https://github.com/seapagan/fastapi-redis-cache-reborn/actions/workflows/tests.yml)
[![Linting](https://github.com/seapagan/fastapi-redis-cache-reborn/actions/workflows/ruff.yml/badge.svg)](https://github.com/seapagan/fastapi-redis-cache-reborn/actions/workflows/ruff.yml)
[![Type Checking](https://github.com/seapagan/fastapi-redis-cache-reborn/actions/workflows/mypy.yml/badge.svg)](https://github.com/seapagan/fastapi-redis-cache-reborn/actions/workflows/mypy.yml)
![PyPI - License](https://img.shields.io/pypi/l/fastapi-redis-cache-reborn?color=%25234DC71F)
![PyPI - Downloads](https://img.shields.io/pypi/dm/fastapi-redis-cache-reborn?color=%234DC71F)

- [Documentation Site](#documentation-site)
- [Migrating from `fastapi-redis-cache`](#migrating-from-fastapi-redis-cache)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Redis Server](#redis-server)
  - [Initialize Redis in your FastAPI application](#initialize-redis-in-your-fastapi-application)
  - [`@cache` Decorator](#cache-decorator)
    - [Pre-defined Lifetimes](#pre-defined-lifetimes)
- [Questions/Contributions](#questionscontributions)

## Documentation Site

There is now a documentation site at
<https://seapagan.github.io/fastapi-redis-cache-reborn/> that is generated from
the `docs` folder in this repository. The site is built using
[MkDocs](https://www.mkdocs.org/) and the [Material for
MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. The documentation
is a work in progress, but I will be adding more content as time goes on, and
cutting down the README file to be more concise.

## Migrating from `fastapi-redis-cache`

This project is a continuation of
[fastapi-redis-cache](https://github.com/a-luna/fastapi-redis-cache) which seems
to no longer be maintained and had fallen behind in both `Redis` and `FastAPI`
versions. I decided to split this as a separate repository rather than a fork,
since the original project has had no activity for a over three years.

Right now the code is basically the same as the original project, but I have
updated the Package management system to use `Poetry`, the dependencies and the
CI/CD pipeline, and added type-hinting. I've also merged some open PRs from the
original project that fixed some issues.

See the [TODO File](TODO.md) file for a list of things I plan to do in the near
future.

The package still has the same interface and classes as the original. You will
still import the package as `fastapi_redis_cache` in your code, the name has
only changed on PyPI to avoid conflicts with the original package. This is to
make it transparent to migrate to this version.

However, it is important to make sure that the old package is uninstalled before
installing this one. The package name has changed, but the module name is still
`fastapi_redis_cache`. **The best way is to remove your old virtual environment
and run `pip install` or `poetry install` again**.

## Features

- Cache response data for async and non-async path operation functions.
- Lifetime of cached data is configured separately for each API endpoint.
- Requests with `Cache-Control` header containing `no-cache` or `no-store` are
  handled correctly (all caching behavior is disabled).
- Requests with `If-None-Match` header will receive a response with status `304
  NOT MODIFIED` if `ETag` for requested resource matches header value.

## Installation

if you are using `poetry` (recommended):

```bash
poetry add fastapi-redis-cache-reborn
```

Otherwise you can use `pip`:

```bash
pip install fastapi-redis-cache-reborn
```

## Usage

### Redis Server

You will need access to a Redis server. If you don't have one running locally,
you can use `Docker` or even a cloud service like
[Redis Cloud](https://redis.com/cloud/overview/) or [AWS
ElastiCache](https://aws.amazon.com/elasticache/redis/).

There is a `docker-compose-redis-only.yml` file in the root of this repository
that you can use to start a Redis server locally. Just run:

```bash
docker compose -f docker-compose-redis-only.yml up -d
```

This will spin up a Redis server on `localhost:6379`, without any password,
running in the background. You can stop it with:

```bash
docker compose -f docker-compose-redis-only.yml down
```

The image is based on
[redis/redis-stack](https://redis.io/docs/install/install-stack/docker/) so also
includes [RedisInsight](https://redis.io/docs/connect/insight/) running on port
`8001` that you can use to inspect the Redis server.

**Note that this is a development server and should not be used in production.**

### Initialize Redis in your FastAPI application

Create a `FastApiRedisCache` instance when your application starts by defining a
['lifespan' event handler](<https://fastapi.tiangolo.com/advanced/events/>) as
shown below. Replace the `REDIS_SERVER_URL` with the address and port of your
own Redis server.

```python {linenos=table}
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi_redis_cache import FastApiRedisCache, cache
from sqlalchemy.orm import Session

REDIS_SERVER_URL = "redis://127.0.0.1:6379"

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=os.environ.get("REDIS_URL", REDIS_SERVER_URL),
        prefix="myapi-cache",
        response_header="X-MyAPI-Cache",
        ignore_arg_types=[Request, Response, Session]
    )
    yield

app = FastAPI(title="FastAPI Redis Cache Example",lifespan=lifespan)

# routes and more code

```

After creating the instance, you must call the `init` method. The only required
argument for this method is the URL for the Redis database (`host_url`). All
other arguments are optional:

- `host_url` (`str`) &mdash; Redis database URL. (_**Required**_)
- `prefix` (`str`) &mdash; Prefix to add to every cache key stored in the Redis
  database. (_Optional_, defaults to `None`)
- `response_header` (`str`) &mdash; Name of the custom header field used to
  identify cache hits/misses. (_Optional_, defaults to `X-FastAPI-Cache`)
- `ignore_arg_types` (`List[Type[object]]`) &mdash; Cache keys are created (in
  part) by combining the name and value of each argument used to invoke a path
  operation function. If any of the arguments have no effect on the response
  (such as a `Request` or `Response` object), including their type in this list
  will ignore those arguments when the key is created. (_Optional_, defaults to
  `[Request, Response]`)
  - The example shown here includes the `sqlalchemy.orm.Session` type, if your
    project uses SQLAlchemy as a dependency ([as demonstrated in the FastAPI
    docs](https://fastapi.tiangolo.com/tutorial/sql-databases/)), you should
    include `Session` in `ignore_arg_types` in order for cache keys to be
    created correctly ([More info][cache-keys]).

### `@cache` Decorator

Decorating a path function with `@cache` enables caching for the endpoint.
**Response data is only cached for `GET` operations**, decorating path functions
for other HTTP method types will have no effect. If no arguments are provided,
responses will be set to expire after one year, which, historically, is the
correct way to mark data that "never expires".

```python
# WILL NOT be cached
@app.get("/data_no_cache")
def get_data():
    return {"success": True, "message": "this data is not cacheable, for... you know, reasons"}

# Will be cached for one year
@app.get("/immutable_data")
@cache()
async def get_immutable_data():
    return {"success": True, "message": "this data can be cached indefinitely"}
```

Response data for the API endpoint at `/immutable_data` will be cached by the
Redis server. Log messages are written to standard output whenever a response is
added to or retrieved from the cache.

In most situations, response data must expire in a much shorter period of time
than one year. Using the `expire` parameter, You can specify the number of
seconds before data is deleted:

```python
# Will be cached for thirty seconds
@app.get("/dynamic_data")
@cache(expire=30)
def get_dynamic_data(request: Request, response: Response):
    return {"success": True, "message": "this data should only be cached temporarily"}
```

> [!NOTE]
> `expire` can be either an `int` value or `timedelta` object. When
> the TTL is very short (like the example above) this results in a decorator
> that is expressive and requires minimal effort to parse visually. For
> durations an hour or longer (e.g., `@cache(expire=86400)`), IMHO, using a
> `timedelta` object is much easier to grok
> (`@cache(expire=timedelta(days=1))`).

#### Pre-defined Lifetimes

The decorators listed below define several common durations and can be used in
place of the `@cache` decorator:

- `@cache_one_minute`
- `@cache_one_hour`
- `@cache_one_day`
- `@cache_one_week`
- `@cache_one_month`
- `@cache_one_year`

For example, instead of `@cache(expire=timedelta(days=1))`, you could use:

```python
from fastapi_redis_cache import cache_one_day

@app.get("/cache_one_day")
@cache_one_day()
def partial_cache_one_day(response: Response):
    return {"success": True, "message": "this data should be cached for 24 hours"}
```

If a duration that you would like to use throughout your project is missing from
the list, you can easily create your own:

```python
from functools import partial, update_wrapper
from fastapi_redis_cache import cache

ONE_HOUR_IN_SECONDS = 3600

cache_two_hours = partial(cache, expire=ONE_HOUR_IN_SECONDS * 2)
update_wrapper(cache_two_hours, cache)
```

Then, simply import `cache_two_hours` and use it to decorate your API endpoint
path functions:

```python
@app.get("/cache_two_hours")
@cache_two_hours()
def partial_cache_two_hours(response: Response):
    return {"success": True, "message": "this data should be cached for two hours"}
```

> [!TIP]
> Please read the full documentation on the [website][website] for more
> information on the `@cache` decorator and the pre-defined lifetimes.
> There is also a section on [cache keys][cache-keys] that explains how the
> cache keys are generated and how to use them properly.

## Questions/Contributions

If you have any questions, please open an issue. Any suggestions and
contributions are absolutely welcome. This is still a very small and young
project, I plan on adding a feature roadmap and further documentation in the
near future.

[website]: https://seapagan.github.io/fastapi-redis-cache-reborn/
[cache-keys]: https://seapagan.github.io/fastapi-redis-cache-reborn/usage/#cache-keys
