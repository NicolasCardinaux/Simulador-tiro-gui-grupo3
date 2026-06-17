from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4

from .constants import (
    ALLOWED_RESULTS,
    DEFAULT_LED_DURATION_MS,
    LED_GREEN,
    LED_RED,
    MAX_COORDINATE_VALUE,
    MAX_LED_DURATION_MS,
    MESSAGE_TYPE_SHOT_RESULT,
    MIN_COORDINATE_VALUE,
    MIN_LED_DURATION_MS,
    PROTOCOL_VERSION,
    RESULT_HIT,
    SOURCE_MODULE_GUI,
)
from .exceptions import MessageValidationError
from .models import Coordinates, Feedback, ShotResult, Source


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_result(result: str) -> None:
    if result not in ALLOWED_RESULTS:
        raise MessageValidationError("result must be 'hit' or 'miss'")


def _validate_duration(duration_ms: int) -> None:
    if isinstance(duration_ms, bool) or not isinstance(duration_ms, int):
        raise MessageValidationError("duration_ms must be an integer")
    if not MIN_LED_DURATION_MS <= duration_ms <= MAX_LED_DURATION_MS:
        raise MessageValidationError(
            f"duration_ms must be between {MIN_LED_DURATION_MS} and {MAX_LED_DURATION_MS}"
        )


def _validate_coordinate_value(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MessageValidationError(f"{name} must be an integer")
    if not MIN_COORDINATE_VALUE <= value <= MAX_COORDINATE_VALUE:
        raise MessageValidationError(
            f"{name} must be between {MIN_COORDINATE_VALUE} and {MAX_COORDINATE_VALUE}"
        )


def _build_coordinates(x: Optional[int], y: Optional[int]) -> Optional[Coordinates]:
    if (x is None) != (y is None):
        raise MessageValidationError("x and y must be provided together")

    if x is None and y is None:
        return None

    _validate_coordinate_value("x", x)
    _validate_coordinate_value("y", y)
    return Coordinates(x=x, y=y)


def _validate_metadata(metadata: Optional[Mapping[str, Any]]) -> None:
    if metadata is not None and not isinstance(metadata, Mapping):
        raise MessageValidationError("metadata must be an object")


def build_shot_result(
    result: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    duration_ms: int = DEFAULT_LED_DURATION_MS,
    metadata: Optional[Mapping[str, Any]] = None,
    source_module: str = SOURCE_MODULE_GUI,
) -> ShotResult:
    """Build a normalized shot result from already extracted values."""
    _validate_result(result)
    _validate_duration(duration_ms)
    _validate_metadata(metadata)

    coordinates = _build_coordinates(x, y)
    feedback = Feedback(
        led=LED_GREEN if result == RESULT_HIT else LED_RED,
        duration_ms=duration_ms,
    )

    return ShotResult(
        version=PROTOCOL_VERSION,
        type=MESSAGE_TYPE_SHOT_RESULT,
        shot_id=str(uuid4()),
        timestamp=_utc_timestamp(),
        source=Source(module=source_module),
        result=result,
        feedback=feedback,
        coordinates=coordinates,
        metadata=metadata,
    )


def build_shot_result_from_raw(raw_data: dict) -> ShotResult:
    """Build a shot result from the raw dictionary produced by Grupo 3."""
    if not isinstance(raw_data, dict):
        raise MessageValidationError("raw_data must be a dictionary")
    if "result" not in raw_data:
        raise MessageValidationError("raw_data must include result")

    return build_shot_result(
        result=raw_data["result"],
        x=raw_data.get("x"),
        y=raw_data.get("y"),
        duration_ms=raw_data.get("duration_ms", DEFAULT_LED_DURATION_MS),
        metadata=raw_data.get("metadata"),
    )
