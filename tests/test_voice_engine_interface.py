from __future__ import annotations

from pathlib import Path

import pytest

from impersono.core.inference import (
    EngineCapabilities,
    EngineIdentity,
    EngineModel,
    EngineState,
    EngineStatus,
    GenerationRequest,
    GenerationResult,
    VoiceEngine,
)


class FakeVoiceEngine(VoiceEngine):
    def __init__(self) -> None:
        self._loaded_model: str | None = None
        self._state = EngineState.UNLOADED
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

    @property
    def status(self) -> EngineStatus:
        return EngineStatus(
            state=self._state,
            loaded_model_id=self._loaded_model,
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

        self._state = EngineState.LOADING
        self._loaded_model = model_id
        self._state = EngineState.READY

    def unload_model(self) -> None:
        self._loaded_model = None
        self._state = EngineState.UNLOADED

    def generate(
        self,
        request: GenerationRequest,
        progress=None,
    ) -> GenerationResult:
        if self._loaded_model is None:
            raise RuntimeError("model not loaded")

        self._state = EngineState.GENERATING

        if progress is not None:
            progress(0.0, "Starting")
            progress(1.0, "Complete")

        result = GenerationResult(
            audio_path=request.output_path or Path("output.wav"),
            engine_id=self.identity.engine_id,
            model_id=self._loaded_model,
        )
        self._state = EngineState.READY
        return result

    def cancel(self) -> None:
        self.cancel_requested = True
        self._state = EngineState.CANCELLING


def test_voice_engine_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        VoiceEngine()


def test_fake_engine_satisfies_contract() -> None:
    engine = FakeVoiceEngine()

    assert engine.identity.engine_id == "fake"
    assert engine.capabilities.supports_voice_conditioning is True
    assert engine.status.state is EngineState.UNLOADED
    assert engine.status.loaded_model_id is None
    assert engine.list_models()[0].is_loaded is False

    engine.load_model("fake/model-1")
    assert engine.status.state is EngineState.READY
    assert engine.status.loaded_model_id == "fake/model-1"
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
    assert engine.status.state is EngineState.READY

    engine.cancel()
    assert engine.cancel_requested is True
    assert engine.status.state is EngineState.CANCELLING

    engine.unload_model()
    assert engine.status.state is EngineState.UNLOADED
    assert engine.status.loaded_model_id is None
    assert engine.list_models()[0].is_loaded is False


def test_engine_status_can_describe_error_without_backend_details() -> None:
    status = EngineStatus(
        state=EngineState.ERROR,
        loaded_model_id="fake/model-1",
        message="Model failed during generation.",
    )

    assert status.state is EngineState.ERROR
    assert status.loaded_model_id == "fake/model-1"
    assert status.message == "Model failed during generation."


def test_generation_request_keeps_engine_specific_options_generic() -> None:
    request = GenerationRequest(
        text="Test",
        options={"temperature": 0.7},
    )

    assert request.text == "Test"
    assert request.options["temperature"] == 0.7
