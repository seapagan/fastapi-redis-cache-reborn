# FastAPI-Redis-Cache-Reborn

## Introduction

A simple and robust caching solution for FastAPI that interprets request header
values and creates proper response header values (powered by Redis)

This project is a continuation of
[fastapi-redis-cache](https://github.com/a-luna/fastapi-redis-cache){:target="_blank"}
which seems to no longer be maintained and had fallen behind in both Redis and
FastAPI versions. I decided to split this as a separate repository rather than a
fork, since the original project has had no activity for a over three years.

Right now the code is basically the same as the original project, but I have
updated the Package management system to use Poetry, the dependencies and the
CI/CD pipeline, and added type-hinting. I've also merged some open PRs from the
original project that fixed some issues.

See the TODO File file for a list of things I plan to do in the near future.

The package still has the same interface and classes as the original. You will
still import the package as `fastapi_redis_cache` in your code, the name has only
changed on PyPI to avoid conflicts with the original package. This is to make it
transparent to migrate to this version.

!!! warning "Important"
    It is important to make sure that the old package is uninstalled before
    installing this one. The package name has changed, but the module name is
    still `fastapi_redis_cache`. **The best way is to remove your old virtual
    environment and run `poetry install` or `pip install` again**.

## Features

- Cache response data for async and non-async path operation functions.
- Lifetime of cached data is configured separately for each API endpoint.
- Requests with `Cache-Control` header containing `no-cache` or `no-store` are
  handled correctly (all caching behavior is disabled).
- Requests with `If-None-Match` header will receive a response with status `304 NOT
  MODIFIED` if ETag for requested resource matches header value.
