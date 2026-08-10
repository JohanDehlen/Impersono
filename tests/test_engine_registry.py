from __future__ import annotations

from pathlib import Path

import pytest

from impersono.core.inference import (
    DuplicateEngineError,
    EngineCapabilities,
    EngineIdentity,
    EngineModel,
    EngineNotFoundError,
    EngineRegistry,
    EngineState,
    EngineStatus,
    GenerationRequest,
    GenerationResult,
    VoiceEngine,
)


class RegistryTestEngine(VoiceEngine):
    def __init__(self, engine_id: str, display_name: str) -> None:
        self._identity = EngineIdentity(
            engine_id=engine_id,
            display_name=display_name,
            engine_version="1.0",
        )

    @property
    def identity(self) -> EngineIdentity:
        return self._identity

    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_voice_conditioning=False,
            supports_cancellation=False,
            supports_progress=False,
        )

    @property
    def status(self) -> EngineStatus:
        return EngineStatus(state=EngineState.UNLOADED)

    def list_models(self) -> tuple[EngineModel, ...]:
        return ()

    def load_model(self, model_id: str) -> None:
        return None

    def unload_model(self) -> None:
        return None

    def generate(
        self,
        request: GenerationRequest,
        progress=None,
    ) -> GenerationResult:
        return GenerationResult(
            audio_path=request.output_path or Path("output.wav"),
            engine_id=self.identity.engine_id,
            model_id="test-model",
        )

    def cancel(self) -> None:
        return None


def test_registry_registers_and_retrieves_engines() -> None:
    first = RegistryTestEngine("alpha", "Alpha")
    second = RegistryTestEngine("beta", "Beta")

    registry = EngineRegistry([second, first])

    assert len(registry) == 2
    assert "alpha" in registry
    assert registry.get("alpha") is first
    assert registry.list_engines() == (first, second)


def test_registry_rejects_duplicate_engine_ids() -> None:
    registry = EngineRegistry([RegistryTestEngine("same", "First")])

    with pytest.raises(DuplicateEngineError, match="same"):
        registry.register(RegistryTestEngine("same", "Second"))


def test_registry_rejects_blank_engine_id() -> None:
    registry = EngineRegistry()

    with pytest.raises(ValueError, match="non-empty"):
        registry.register(RegistryTestEngine("   ", "Blank"))


def test_registry_reports_missing_engine() -> None:
    registry = EngineRegistry()

    with pytest.raises(EngineNotFoundError, match="missing"):
        registry.get("missing")


def test_registry_can_unregister_engine() -> None:
    engine = RegistryTestEngine("remove-me", "Remove Me")
    registry = EngineRegistry([engine])

    removed = registry.unregister("remove-me")

    assert removed is engine
    assert len(registry) == 0
    assert "remove-me" not in registry
