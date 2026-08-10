from __future__ import annotations

from pathlib import Path

import pytest

from impersono.core.inference import (
    EngineCapabilities,
    EngineIdentity,
    EngineModel,
    GenerationRequest,
    GenerationResult,
    VoiceEngine,
)


class FakeVoiceEngine(VoiceEngine):
    def __init__(self) -> None:
        self._loaded_model: str | None = None
        self.cancel_requested = False

    @property
    def identity(self) -> EngineIdentity:
        return EngineIdentity(
            engine_id="fake",
            display_name="Fake Voice Engine",
            engine_version="1.0",
        )

    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_voice_conditioning=True,
            supports_cancellation=True,
            supports_progress=True,
        )

    def list_models(self) -> tuple[EngineModel, ...]:
        return (
            EngineModel(
                model_id="fake/model-1",
                display_name="Fake Model 1",
                is_available=True,
                is_loaded=self._loaded_model == "fake/model-1",
            ),
        )

    def load_model(self, model_id: str) -> None:
        if model_id != "fake/model-1":
            raise ValueError(model_id)
        self._loaded_model = model_id

    def unload_model(self) -> None:
        self._loaded_model = None

    def generate(
        self,
        request: GenerationRequest,
        progress=None,
    ) -> GenerationResult:
        if self._loaded_model is None:
            raise RuntimeError("model not loaded")

        if progress is not None:
            progress(0.0, "Starting")
            progress(1.0, "Complete")

        return GenerationResult(
            audio_path=request.output_path or Path("output.wav"),
            engine_id=self.identity.engine_id,
            model_id=self._loaded_model,
        )

    def cancel(self) -> None:
        self.cancel_requested = True


def test_voice_engine_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        VoiceEngine()


def test_fake_engine_satisfies_contract() -> None:
    engine = FakeVoiceEngine()

    assert engine.identity.engine_id == "fake"
    assert engine.capabilities.supports_voice_conditioning is True
    assert engine.list_models()[0].is_loaded is False

    engine.load_model("fake/model-1")
    assert engine.list_models()[0].is_loaded is True

    progress_events: list[tuple[float, str | None]] = []
    result = engine.generate(
        GenerationRequest(
            text="Hello from Impersono.",
            output_path=Path("example.wav"),
        ),
        progress=lambda value, message: progress_events.append((value, message)),
    )

    assert result.audio_path == Path("example.wav")
    assert result.engine_id == "fake"
    assert result.model_id == "fake/model-1"
    assert progress_events == [(0.0, "Starting"), (1.0, "Complete")]

    engine.cancel()
    assert engine.cancel_requested is True

    engine.unload_model()
    assert engine.list_models()[0].is_loaded is False


def test_generation_request_keeps_engine_specific_options_generic() -> None:
    request = GenerationRequest(
        text="Test",
        options={"temperature": 0.7},
    )

    assert request.text == "Test"
    assert request.options["temperature"] == 0.7
