import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .exceptions import SerializationError


def _drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _drop_none(item)
            for key, item in value.items()
            if item is not None
        }
    if isinstance(value, list):
        return [_drop_none(item) for item in value]
    return value


def serialize_message(message: Any) -> str:
    """Serialize a middleware dataclass to compact UTF-8 compatible JSON."""
    if not is_dataclass(message):
        raise SerializationError("message must be a middleware dataclass instance")

    try:
        payload = _drop_none(asdict(message))
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as error:
        raise SerializationError(f"could not serialize message: {error}") from error


def deserialize_message(json_message: str) -> dict:
    """Deserialize a JSON string to a dictionary."""
    if not isinstance(json_message, str):
        raise SerializationError("json_message must be a string")

    try:
        data = json.loads(json_message)
    except json.JSONDecodeError as error:
        raise SerializationError(f"malformed JSON: {error.msg}") from error

    if not isinstance(data, dict):
        raise SerializationError("json_message must decode to an object")

    return data
