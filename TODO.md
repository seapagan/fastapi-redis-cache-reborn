# TODO List

## Existing Issues

These below are from Issues or PRs in the original repository.

- Add ability to manually expire a cache entry
  (<https://github.com/a-luna/fastapi-redis-cache/issues/63>)
- Add support for caching non-FastAPI functions
  (<https://github.com/a-luna/fastapi-redis-cache/pull/66>)
- Take a look at other issues in the original repository to see if any need to
  be added here.

## New Ideas

- add an option to the init function to disable logging of cache hits and
  misses. or only display these messages if a certain ENV variable is set/unset?
- add an option to have a separate logging file for cache hits and misses?
- remove creating a test Redis from `redis.py`. This should not be done in the
  production logic, but set up in the test logic.
- remove the FakeRedis from the `_connect_` function. This should be set up in
  the test logic not production code.
- catch invalid cache type exceptions and raise a more informative error
  message.
- configure the log time display format in the `Cache` class. Make it
  totally configurable through an optional parameter and/or detect and use the
  preferred local time format.
- catch invalid cache type exceptions and just return a normal response
  instead of raising Internal Server (500) error
