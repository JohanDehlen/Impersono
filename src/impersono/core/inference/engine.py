"""Abstract voice-engine contract used by Impersono core services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from .models import (
    EngineCapabilities,
    EngineIdentity,
    EngineModel,
    EngineStatus,
    GenerationRequest,
    GenerationResult,
)

ProgressCallback = Callable[[float, str | None], None]


class VoiceEngine(ABC):
    """Common boundary implemented by local or future remote voice engines.

    The interface intentionally avoids framework-specific objects so callers do
    not need to know whether a backend uses PyTorch, ONNX, a subprocess, or a
    future service.
    """

    @property
    @abstractmethod
    def identity(self) -> EngineIdentity:
        """Return stable engine identity information."""

    @property
    @abstractmethod
    def capabilities(self) -> EngineCapabilities:
        """Return features this engine implementation actually supports."""

    @property
    @abstractmethod
    def status(self) -> EngineStatus:
        """Return the engine's current lifecycle state."""

    @abstractmethod
    def list_models(self) -> tuple[EngineModel, ...]:
        """Return models known to this engine."""

    @abstractmethod
    def load_model(self, model_id: str) -> None:
        """Load or activate a model for later generation."""

    @abstractmethod
    def unload_model(self) -> None:
        """Release the currently loaded model and associated resources."""

    @abstractmethod
    def generate(
        self,
        request: GenerationRequest,
        progress: ProgressCallback | None = None,
    ) -> GenerationResult:
        """Generate speech for one request.

        Implementations may call ``progress`` with a normalized value from 0.0
        through 1.0 and an optional human-readable status message.
        """

    @abstractmethod
    def cancel(self) -> None:
        """Request cancellation of current generation when supported."""
