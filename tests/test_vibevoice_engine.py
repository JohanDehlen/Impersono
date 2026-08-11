from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from impersono.core.inference import EngineError, EngineState, GenerationRequest, ModelLoadError
from impersono.core.inference.backends.vibevoice import (
    VibeVoiceConfig,
    VibeVoiceDependencyStatus,
    VibeVoiceEngine,
)


@dataclass
class FakeRuntime:
    model_id: str
    closed: bool = False
    generated: list[dict[str, object]] | None = None

    def generate_to_file(self, *, text, voice_reference, output_path, cfg_scale):
        if self.generated is None:
            self.generated = []
        self.generated.append({
            "text": text,
            "voice_reference": voice_reference,
            "output_path": output_path,
            "cfg_scale": cfg_scale,
        })
        return 2.5

    def close(self) -> None:
        self.closed = True


class FakeLoader:
    def __init__(self) -> None:
        self.loaded_config = None
        self.runtime = FakeRuntime("vibevoice/VibeVoice-1.5B")

    def load(self, config):
        self.loaded_config = config
        return self.runtime


def available(monkeypatch):
    monkeypatch.setattr(
        "impersono.core.inference.backends.vibevoice.detect_vibevoice_dependencies",
        lambda: VibeVoiceDependencyStatus(vibevoice=True, torch=True),
    )


def test_vibevoice_config_defaults_match_inspected_cpu_prototype():
    config = VibeVoiceConfig()
    assert config.model_id == "vibevoice/VibeVoice-1.5B"
    assert config.device == "cpu"
    assert config.inference_steps == 10
    assert config.cfg_scale == 1.3


def test_vibevoice_engine_exposes_conservative_capabilities():
    engine = VibeVoiceEngine()
    assert engine.identity.engine_id == "vibevoice"
    assert engine.capabilities.supports_voice_conditioning is True
    assert engine.capabilities.supports_multi_speaker is True
    assert engine.capabilities.supports_cancellation is False
    assert engine.capabilities.supports_streaming is False
    assert engine.status.state is EngineState.UNLOADED


def test_dependency_status_lists_missing_packages():
    status = VibeVoiceDependencyStatus(vibevoice=False, torch=True)
    assert status.available is False
    assert status.missing == ("vibevoice",)


def test_load_model_uses_injected_runtime_boundary(monkeypatch):
    available(monkeypatch)
    loader = FakeLoader()
    engine = VibeVoiceEngine(runtime_loader=loader)
    engine.load_model("vibevoice/VibeVoice-1.5B")
    assert loader.loaded_config == engine.config
    assert engine.status.state is EngineState.READY
    assert engine.status.loaded_model_id == "vibevoice/VibeVoice-1.5B"
    assert engine.list_models()[0].is_loaded is True
    engine.unload_model()
    assert loader.runtime.closed is True
    assert engine.status.state is EngineState.UNLOADED


def test_load_model_reports_missing_optional_dependencies(monkeypatch):
    monkeypatch.setattr(
        "impersono.core.inference.backends.vibevoice.detect_vibevoice_dependencies",
        lambda: VibeVoiceDependencyStatus(vibevoice=False, torch=False),
    )
    engine = VibeVoiceEngine()
    with pytest.raises(ModelLoadError, match="vibevoice, torch"):
        engine.load_model("vibevoice/VibeVoice-1.5B")
    assert engine.status.state is EngineState.ERROR


def test_generate_calls_runtime_and_returns_generation_result(monkeypatch):
    available(monkeypatch)
    loader = FakeLoader()
    engine = VibeVoiceEngine(runtime_loader=loader)
    engine.load_model("vibevoice/VibeVoice-1.5B")
    result = engine.generate(GenerationRequest(
        text="Hello from Impersono.",
        voice_reference=Path("voice.wav"),
        output_path=Path("result.wav"),
        options={"cfg_scale": 1.5},
    ))
    assert result.audio_path == Path("result.wav")
    assert result.engine_id == "vibevoice"
    assert result.model_id == "vibevoice/VibeVoice-1.5B"
    assert result.duration_seconds == 2.5
    assert loader.runtime.generated[0]["cfg_scale"] == 1.5
    assert engine.status.state is EngineState.READY


def test_generate_uses_default_output_and_cfg_scale(monkeypatch):
    available(monkeypatch)
    loader = FakeLoader()
    engine = VibeVoiceEngine(runtime_loader=loader)
    engine.load_model("vibevoice/VibeVoice-1.5B")
    result = engine.generate(GenerationRequest(text="Hello"))
    assert result.audio_path == Path("output") / "vibevoice_generated.wav"
    assert loader.runtime.generated[0]["cfg_scale"] == 1.3


def test_generation_failure_sets_error_state(monkeypatch):
    available(monkeypatch)

    class FailingRuntime(FakeRuntime):
        def generate_to_file(self, **kwargs):
            raise RuntimeError("boom")

    class FailingLoader:
        def load(self, config):
            return FailingRuntime(config.model_id)

    engine = VibeVoiceEngine(runtime_loader=FailingLoader())
    engine.load_model("vibevoice/VibeVoice-1.5B")
    with pytest.raises(EngineError, match="boom"):
        engine.generate(GenerationRequest(text="Hello"))
    assert engine.status.state is EngineState.ERROR


def test_generate_rejects_empty_text(monkeypatch):
    available(monkeypatch)
    engine = VibeVoiceEngine(runtime_loader=FakeLoader())
    engine.load_model("vibevoice/VibeVoice-1.5B")
    with pytest.raises(ValueError, match="must not be empty"):
        engine.generate(GenerationRequest(text="   "))
