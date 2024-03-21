"""Test suite for the FastAPI-Cache package."""

import datetime
import json
import re
import time
from decimal import Decimal

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from fastapi_redis_cache.client import HTTP_TIME
from fastapi_redis_cache.util import ONE_HOUR_IN_SECONDS, deserialize_json
from tests.main import app

client = TestClient(app)
MAX_AGE_REGEX = re.compile(r"max-age=(?P<ttl>\d+)")

EXPIRE_TIME = 5


def test_cache_never_expire() -> None:
    """Test the initial and next requests to the /cache_never_expire endpoint.

    The FastAPI-Cache header field should equal "Miss"
    """
    response = client.get("/cache_never_expire")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data can be cached indefinitely",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Miss"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers

    # Send request to same endpoint,
    # X-FastAPI-Cache header field should now equal "Hit"
    response = client.get("/cache_never_expire")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data can be cached indefinitely",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Hit"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers


def test_cache_expires() -> None:
    """Test the initial and next requests to the /cache_expires endpoint."""
    # Store time when response data was added to cache
    added_at_utc = datetime.datetime.now(tz=datetime.timezone.utc)

    # Initial request, X-FastAPI-Cache header field should equal "Miss"
    response = client.get("/cache_expires")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data should be cached for five seconds",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Miss"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers

    # Store eTag value from response header
    check_etag = response.headers["etag"]

    # Send request, X-FastAPI-Cache header field should now equal "Hit"
    response = client.get("/cache_expires")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data should be cached for five seconds",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Hit"

    # Verify eTag value matches the value stored from the initial response
    assert "etag" in response.headers
    assert response.headers["etag"] == check_etag

    # Store 'max-age' value of 'cache-control' header field
    assert "cache-control" in response.headers
    match = MAX_AGE_REGEX.search(response.headers.get("cache-control"))
    assert match
    ttl = int(match.groupdict()["ttl"])
    assert ttl <= EXPIRE_TIME

    # Store value of 'expires' header field
    assert "expires" in response.headers
    expire_at_utc = datetime.datetime.strptime(
        response.headers["expires"], HTTP_TIME
    ).replace(tzinfo=datetime.timezone.utc)

    # Wait until expire time has passed
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    while expire_at_utc > now:
        time.sleep(1)
        now = datetime.datetime.now(tz=datetime.timezone.utc)

    # Wait one additional second to ensure redis has deleted the expired
    # response data
    time.sleep(1)
    second_request_utc = datetime.datetime.now(tz=datetime.timezone.utc)

    # Verify that the time elapsed since the data was added to the cache is
    # greater than the ttl value
    elapsed = (second_request_utc - added_at_utc).total_seconds()
    assert elapsed > ttl

    # Send request, X-FastAPI-Cache header field should equal "Miss" since the
    # cached value has been evicted
    response = client.get("/cache_expires")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data should be cached for five seconds",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Miss"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers

    # Check eTag value again. Since data is the same, the value should still
    # match
    assert response.headers["etag"] == check_etag


def test_cache_json_encoder() -> None:
    """Test the custom JSON encoder and object_hook functions."""
    # In order to verify that our custom BetterJsonEncoder is working correctly,
    # the  /cache_json_encoder endpoint returns a dict containing
    # datetime.datetime, datetime.date and decimal.Decimal objects.
    response = client.get("/cache_json_encoder")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {
        "success": True,
        "start_time": {
            "_spec_type": "<class 'datetime.datetime'>",
            "val": "04/20/2021 07:17:17 AM +0000",
        },
        "finish_by": {
            "_spec_type": "<class 'datetime.date'>",
            "val": "04/21/2021",
        },
        "final_calc": {
            "_spec_type": "<class 'decimal.Decimal'>",
            "val": "3.140000000000000124344978758017532527446746826171875",
        },
    }

    # To verify that our custom object_hook function which deserializes types
    # that are not typically JSON-serializable is working correctly, we test it
    # with the serialized values sent in the response.
    json_dict = deserialize_json(json.dumps(response_json))
    assert json_dict["start_time"] == datetime.datetime(
        2021, 4, 20, 7, 17, 17, tzinfo=datetime.timezone.utc
    )
    assert json_dict["finish_by"] == datetime.datetime(2021, 4, 21)  # noqa: DTZ001
    assert json_dict["final_calc"] == Decimal(3.14)


def test_cache_control_no_cache() -> None:
    """Test the cache-control header field containing "no-cache"."""
    # Simple test that verifies if a request is recieved with the cache-control
    # header field containing "no-cache", no caching behavior is performed
    response = client.get(
        "/cache_never_expire", headers={"cache-control": "no-cache"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data can be cached indefinitely",
    }
    assert "x-fastapi-cache" not in response.headers
    assert "cache-control" not in response.headers
    assert "expires" not in response.headers
    assert "etag" not in response.headers


def test_cache_control_no_store() -> None:
    """Test the cache-control header field containing 'no-store'."""
    # Simple test that verifies if a request is recieved with the cache-control
    # header field containing "no-store", no caching behavior is performed
    response = client.get(
        "/cache_never_expire", headers={"cache-control": "no-store"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data can be cached indefinitely",
    }
    assert "x-fastapi-cache" not in response.headers
    assert "cache-control" not in response.headers
    assert "expires" not in response.headers
    assert "etag" not in response.headers


def test_if_none_match() -> None:
    """Test the If-None-Match header field."""
    # Initial request, response data is added to cache
    response = client.get("/cache_never_expire")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data can be cached indefinitely",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Miss"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers

    # Store correct eTag value from response header
    etag = response.headers["etag"]
    # Create another eTag value that is different from the correct value
    invalid_etag = "W/-5480454928453453778"

    # Send request to same endpoint where If-None-Match header contains both
    # valid and invalid eTag values
    response = client.get(
        "/cache_never_expire",
        headers={"if-none-match": f"{etag}, {invalid_etag}"},
    )
    assert response.status_code == status.HTTP_304_NOT_MODIFIED
    assert not response.content
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Hit"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers

    # Send request to same endpoint where If-None-Match header contains just the
    # wildcard (*) character
    response = client.get("/cache_never_expire", headers={"if-none-match": "*"})
    assert response.status_code == status.HTTP_304_NOT_MODIFIED
    assert not response.content
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Hit"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers

    # Send request to same endpoint where If-None-Match header contains only the
    # invalid eTag value
    response = client.get(
        "/cache_never_expire", headers={"if-none-match": invalid_etag}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data can be cached indefinitely",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Hit"
    assert "cache-control" in response.headers
    assert "expires" in response.headers
    assert "etag" in response.headers


def test_partial_cache_one_hour() -> None:
    """Test the @cache_for_one_hour decorator."""
    # Simple test that verifies that the @cache_for_one_hour partial function
    # version of the @cache decorator is working correctly.
    response = client.get("/cache_one_hour")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "this data should be cached for one hour",
    }
    assert "x-fastapi-cache" in response.headers
    assert response.headers["x-fastapi-cache"] == "Miss"
    assert "cache-control" in response.headers
    match = MAX_AGE_REGEX.search(response.headers.get("cache-control"))
    assert match
    assert int(match.groupdict()["ttl"]) == ONE_HOUR_IN_SECONDS
    assert "expires" in response.headers
    assert "etag" in response.headers


def test_cache_invalid_type() -> None:
    """Test when a value that is not JSON-serializable is returned."""
    with pytest.raises(ValueError):  # noqa: PT011
        _ = client.get("/cache_invalid_type")

    # note: I removed all the other assertions from this test, since after the
    # excepion is raised, the response is not returned and in fact none of the
    # assertions are actually executed.
