"""Registry for engine-independent backend discovery and selection."""

from __future__ import annotations

from collections.abc import Iterable

from .engine import VoiceEngine


class DuplicateEngineError(ValueError):
    """Raised when two engines advertise the same stable engine id."""


class EngineNotFoundError(LookupError):
    """Raised when a requested engine id is not registered."""


class EngineRegistry:
    """Owns the set of voice-engine implementations available to Impersono.

    Application services can depend on this registry rather than importing
    concrete backends such as VibeVoice directly.
    """

    def __init__(self, engines: Iterable[VoiceEngine] = ()) -> None:
        self._engines: dict[str, VoiceEngine] = {}

        for engine in engines:
            self.register(engine)

    def register(self, engine: VoiceEngine) -> None:
        """Register one engine by its stable engine id."""

        engine_id = engine.identity.engine_id.strip()
        if not engine_id:
            raise ValueError("Engine identity must contain a non-empty engine_id.")

        if engine_id in self._engines:
            raise DuplicateEngineError(
                f"An engine with id '{engine_id}' is already registered."
            )

        self._engines[engine_id] = engine

    def unregister(self, engine_id: str) -> VoiceEngine:
        """Remove and return a registered engine."""

        try:
            return self._engines.pop(engine_id)
        except KeyError as exc:
            raise EngineNotFoundError(
                f"No voice engine is registered with id '{engine_id}'."
            ) from exc

    def get(self, engine_id: str) -> VoiceEngine:
        """Return the engine registered with ``engine_id``."""

        try:
            return self._engines[engine_id]
        except KeyError as exc:
            raise EngineNotFoundError(
                f"No voice engine is registered with id '{engine_id}'."
            ) from exc

    def list_engines(self) -> tuple[VoiceEngine, ...]:
        """Return registered engines in deterministic id order."""

        return tuple(self._engines[key] for key in sorted(self._engines))

    def __len__(self) -> int:
        return len(self._engines)

    def __contains__(self, engine_id: object) -> bool:
        return engine_id in self._engines
