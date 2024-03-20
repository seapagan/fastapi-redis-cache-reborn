"""Define utility functions for the fastapi_redis_cache package."""

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Union
from uuid import UUID

from dateutil import parser
from pydantic import BaseModel

DATETIME_AWARE = "%m/%d/%Y %I:%M:%S %p %z"
DATE_ONLY = "%m/%d/%Y"

ONE_HOUR_IN_SECONDS = 3600
ONE_DAY_IN_SECONDS = ONE_HOUR_IN_SECONDS * 24
ONE_WEEK_IN_SECONDS = ONE_DAY_IN_SECONDS * 7
ONE_MONTH_IN_SECONDS = ONE_DAY_IN_SECONDS * 30
ONE_YEAR_IN_SECONDS = ONE_DAY_IN_SECONDS * 365

SERIALIZE_OBJ_MAP = {
    str(datetime): parser.parse,
    str(date): parser.parse,
    str(Decimal): Decimal,
}


class BetterJsonEncoder(json.JSONEncoder):
    """Subclass the JSONEncoder to handle more types."""

    def default(self, obj: Any) -> Union[dict[str, str], Any]:  # noqa: ANN401
        """Return a serializable object for the JSONEncoder to use.

        This is re-written from the original code to handle more types, and not
        end up with a mass of if-else and return statements.
        """

        def handle_datetime() -> dict[str, str]:
            return {
                "val": obj.strftime(DATETIME_AWARE),
                "_spec_type": str(datetime),
            }

        def handle_date() -> dict[str, str]:
            return {"val": obj.strftime(DATE_ONLY), "_spec_type": str(date)}

        def handle_decimal() -> dict[str, str]:
            return {"val": str(obj), "_spec_type": str(Decimal)}

        def handle_basemodel() -> Any:  # noqa: ANN401
            """Handle a Pydantic BaseModel object."""
            return obj.model_dump()

        def handle_uuid() -> str:
            return str(obj)

        def handle_enum() -> str:
            return str(obj.value)

        type_mapping = {
            datetime: handle_datetime,
            date: handle_date,
            Decimal: handle_decimal,
            BaseModel: handle_basemodel,
            UUID: handle_uuid,
            Enum: handle_enum,
        }

        for obj_type, handler in type_mapping.items():
            if isinstance(obj, obj_type):
                return handler()

        return super().default(obj)


def object_hook(obj: Any) -> Any:  # noqa: ANN401
    """Hook for the JSONDecoder to handle custom types."""
    if "_spec_type" not in obj:
        return obj
    _spec_type = obj["_spec_type"]
    if _spec_type not in SERIALIZE_OBJ_MAP:
        msg = f'"{obj["val"]}" (type: {_spec_type}) is not JSON serializable'
        raise TypeError(msg)
    return SERIALIZE_OBJ_MAP[_spec_type](obj["val"])  # type: ignore


def serialize_json(json_dict: dict[str, Any]) -> str:
    """Serialize a dictionary to a JSON string."""
    return json.dumps(json_dict, cls=BetterJsonEncoder)


def deserialize_json(json_str: str) -> Any:  # noqa: ANN401
    """Deserialize a JSON string to a dictionary."""
    return json.loads(json_str, object_hook=object_hook)
