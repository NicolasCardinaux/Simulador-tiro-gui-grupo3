import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

from .constants import LED_GREEN, LED_RED, MESSAGE_TYPE_SHOT_RESULT, RESULT_HIT
from .exceptions import MessageValidationError, SerializationError, UnsupportedMessageTypeError
from .serializer import deserialize_message


SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
SCHEMA_REGISTRY = {
    MESSAGE_TYPE_SHOT_RESULT: SCHEMA_DIR / "shot_result.schema.json",
}


def _load_schema(message_type: str) -> dict[str, Any]:
    schema_path = SCHEMA_REGISTRY.get(message_type)
    if schema_path is None:
        raise UnsupportedMessageTypeError(f"unsupported message type: {message_type}")

    try:
        with schema_path.open("r", encoding="utf-8") as file:
            schema = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise MessageValidationError(f"could not load JSON schema: {error}") from error

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise MessageValidationError(f"invalid JSON schema: {error.message}") from error

    return schema


def validate_message(json_message: str) -> dict:
    """Validate a JSON message and return the decoded dictionary."""
    try:
        data = deserialize_message(json_message)
    except SerializationError as error:
        raise MessageValidationError(str(error)) from error

    message_type = data.get("type")
    if not isinstance(message_type, str):
        raise MessageValidationError("message type is required")

    schema = _load_schema(message_type)
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
    except ValidationError as error:
        location = ".".join(str(part) for part in error.absolute_path)
        field = location or "message"
        raise MessageValidationError(f"error in '{field}': {error.message}") from error

    expected_led = LED_GREEN if data["result"] == RESULT_HIT else LED_RED
    if data["feedback"]["led"] != expected_led:
        raise MessageValidationError("feedback.led is not coherent with result")

    return data
