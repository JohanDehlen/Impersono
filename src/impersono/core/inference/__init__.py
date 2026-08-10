"""Engine-independent inference contracts for Impersono."""

from .engine import VoiceEngine
from .errors import (
    EngineError,
    EngineNotReadyError,
    GenerationCancelledError,
    ModelLoadError,
)
from .models import (
    EngineCapabilities,
    EngineIdentity,
    EngineModel,
    EngineState,
    EngineStatus,
    GenerationRequest,
    GenerationResult,
)
from .registry import (
    DuplicateEngineError,
    EngineNotFoundError,
    EngineRegistry,
)

__all__ = [
    "DuplicateEngineError",
    "EngineCapabilities",
    "EngineError",
    "EngineIdentity",
    "EngineModel",
    "EngineNotFoundError",
    "EngineNotReadyError",
    "EngineRegistry",
    "EngineState",
    "EngineStatus",
    "GenerationCancelledError",
    "GenerationRequest",
    "GenerationResult",
    "ModelLoadError",
    "VoiceEngine",
]
