from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class Coordinates:
    """Position of the shot in the GUI coordinate system."""

    x: int
    y: int


@dataclass(frozen=True)
class Feedback:
    """Feedback instruction that Grupo 1 sends to hardware."""

    led: str
    duration_ms: int


@dataclass(frozen=True)
class Source:
    """Module that originated the message."""

    module: str


@dataclass(frozen=True)
class ShotResult:
    """Normalized shot result message for the integration pipeline."""

    version: str
    type: str
    shot_id: str
    timestamp: str
    source: Source
    result: str
    feedback: Feedback
    coordinates: Optional[Coordinates] = None
    metadata: Optional[Mapping[str, Any]] = None
