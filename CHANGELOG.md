# Changelog

This is an auto-generated log of all the changes that have been made to the
project since the first release, with the latest changes at the top.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.3.1](https://github.com/seapagan/fastapi-redis-cache-reborn/releases/tag/0.3.1) (June 21, 2024)

**Closed Issues**

- Bug when trying to create FastApiRedisCache() object ([#94](https://github.com/seapagan/fastapi-redis-cache-reborn/issues/94)) by [seapagan](https://github.com/seapagan)

**Bug Fixes**

- Modify the way the local TZ is detected ([#100](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/100)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Add a basic documentation site ([#84](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/84)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump urllib3 from 2.2.1 to 2.2.2 ([#99](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/99)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump mkdocs-material from 9.5.25 to 9.5.27 ([#98](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/98)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump redis from 5.0.4 to 5.0.6 ([#97](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/97)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump ruff from 0.4.7 to 0.4.9 ([#96](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/96)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pydantic from 2.7.1 to 2.7.4 ([#95](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/95)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 25.4.0 to 25.8.0 ([#92](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/92)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest-asyncio from 0.21.1 to 0.23.7 ([#90](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/90)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 8.2.1 to 8.2.2 ([#89](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/89)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pygments from 2.17.2 to 2.18.0 ([#88](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/88)) by [dependabot[bot]](https://github.com/apps/dependabot)

[`Full Changelog`](https://github.com/seapagan/fastapi-redis-cache-reborn/compare/0.3.0...0.3.1) | [`Diff`](https://github.com/seapagan/fastapi-redis-cache-reborn/compare/0.3.0...0.3.1.diff) | [`Patch`](https://github.com/seapagan/fastapi-redis-cache-reborn/compare/0.3.0...0.3.1.patch)

## [0.3.0](https://github.com/seapagan/fastapi-redis-cache-reborn/releases/tag/0.3.0) (June 04, 2024)

**_'It's Alive!!!!'_**


This is the first release of the project since the fork from the original. It
includes some changes and fixes but otherise is the same functionality as the
original, though with modernized dependencies and tooling.


**New Features**

- Update docker file to use `redis/redis-stack` ([#20](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/20)) by [seapagan](https://github.com/seapagan)
- Add a 'tag' parameter to the 'cache' decorator for future functionality ([#16](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/16)) by [seapagan](https://github.com/seapagan)
- Run mypy as a GitHub Action ([#10](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/10)) by [seapagan](https://github.com/seapagan)
- Support more object types ([#9](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/9)) by [seapagan](https://github.com/seapagan)

**Bug Fixes**

- FIX content-length header gets incorrectly set to 0 by default ([#8](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/8)) by [seapagan](https://github.com/seapagan)

**Refactoring**

- Fix Linting and Typing issues ([#5](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/5)) by [seapagan](https://github.com/seapagan)
- Migrate tooling and libraries ([#3](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/3)) by [seapagan](https://github.com/seapagan)

**Documentation**

- Add a changelog generator to the project ([#13](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/13)) by [seapagan](https://github.com/seapagan)
- Add Python 'Trove' classifiers to the project ([#12](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/12)) by [seapagan](https://github.com/seapagan)
- Rename project and update README ([#11](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/11)) by [seapagan](https://github.com/seapagan)

**Dependency Updates**

- Bump requests from 2.31.0 to 2.32.2 ([#82](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/82)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump jinja2 from 3.1.3 to 3.1.4 ([#81](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/81)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump faker from 24.14.0 to 25.4.0 ([#80](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/80)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump ruff from 0.4.2 to 0.4.7 ([#79](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/79)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pymarkdownlnt from 0.9.18 to 0.9.20 ([#78](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/78)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pytest from 8.1.2 to 8.2.1 ([#73](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/73)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump fakeredis from 2.22.0 to 2.23.2 ([#72](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/72)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pre-commit from 3.7.0 to 3.7.1 ([#70](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/70)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump pyfakefs from 5.4.1 to 5.5.0 ([#69](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/69)) by [dependabot[bot]](https://github.com/apps/dependabot)
- Bump jinja2 from 3.1.3 to 3.1.4 ([#63](https://github.com/seapagan/fastapi-redis-cache-reborn/pull/63)) by [dependabot[bot]](https://github.com/apps/dependabot)
- *and 35 more dependency updates*

---
*This changelog was generated using [github-changelog-md](http://changelog.seapagan.net/) by [Seapagan](https://github.com/seapagan)*
