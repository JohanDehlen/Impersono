"""Engine-independent data passed across Impersono's inference boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Mapping


class EngineState(str, Enum):
    """High-level lifecycle state exposed by a voice engine."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    GENERATING = "generating"
    CANCELLING = "cancelling"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class EngineIdentity:
    """Stable identity exposed by a voice engine implementation."""

    engine_id: str
    display_name: str
    engine_version: str


@dataclass(frozen=True, slots=True)
class EngineCapabilities:
    """Features an engine implementation can truthfully advertise."""

    supports_voice_conditioning: bool
    supports_cancellation: bool
    supports_progress: bool
    supports_multi_speaker: bool = False
    supports_streaming: bool = False


@dataclass(frozen=True, slots=True)
class EngineModel:
    """One model known to an engine."""

    model_id: str
    display_name: str
    is_available: bool
    is_loaded: bool = False


@dataclass(frozen=True, slots=True)
class EngineStatus:
    """Current engine lifecycle snapshot.

    ``loaded_model_id`` is intentionally independent of ``EngineModel`` so
    callers can inspect current state without requiring a model-list refresh.
    """

    state: EngineState
    loaded_model_id: str | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Model-independent speech generation input.

    Engine-specific controls belong in ``options`` until they earn a stable
    Impersono-level abstraction.
    """

    text: str
    voice_reference: Path | None = None
    output_path: Path | None = None
    options: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Successful generation output returned by an engine."""

    audio_path: Path
    engine_id: str
    model_id: str
    duration_seconds: float | None = None
