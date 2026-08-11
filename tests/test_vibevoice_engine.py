from __future__ import annotations

from dataclasses import dataclass

import pytest

from impersono.core.inference import EngineState, ModelLoadError
from impersono.core.inference.backends.vibevoice import (
    VibeVoiceConfig,
    VibeVoiceDependencyStatus,
    VibeVoiceEngine,
)


@dataclass
class FakeRuntime:
    model_id: str
    closed: bool = False

    def close(self) -> None:
        self.closed = True


class FakeLoader:
    def __init__(self) -> None:
        self.loaded_config: VibeVoiceConfig | None = None
        self.runtime = FakeRuntime("vibevoice/VibeVoice-1.5B")

    def load(self, config: VibeVoiceConfig) -> FakeRuntime:
        self.loaded_config = config
        return self.runtime


def test_vibevoice_config_defaults_match_inspected_cpu_prototype() -> None:
    config = VibeVoiceConfig()

    assert config.model_id == "vibevoice/VibeVoice-1.5B"
    assert config.device == "cpu"
    assert config.inference_steps == 10
    assert config.cfg_scale == 1.3


def test_vibevoice_engine_exposes_conservative_capabilities() -> None:
    engine = VibeVoiceEngine()

    assert engine.identity.engine_id == "vibevoice"
    assert engine.capabilities.supports_voice_conditioning is True
    assert engine.capabilities.supports_multi_speaker is True
    assert engine.capabilities.supports_cancellation is False
    assert engine.capabilities.supports_streaming is False
    assert engine.status.state is EngineState.UNLOADED


def test_dependency_status_lists_missing_packages() -> None:
    status = VibeVoiceDependencyStatus(vibevoice=False, torch=True)

    assert status.available is False
    assert status.missing == ("vibevoice",)


def test_load_model_uses_injected_runtime_boundary(monkeypatch) -> None:
    monkeypatch.setattr(
        "impersono.core.inference.backends.vibevoice.detect_vibevoice_dependencies",
        lambda: VibeVoiceDependencyStatus(vibevoice=True, torch=True),
    )
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
    assert engine.status.loaded_model_id is None


def test_load_model_reports_missing_optional_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(
        "impersono.core.inference.backends.vibevoice.detect_vibevoice_dependencies",
        lambda: VibeVoiceDependencyStatus(vibevoice=False, torch=False),
    )
    engine = VibeVoiceEngine()

    with pytest.raises(ModelLoadError, match="vibevoice, torch"):
        engine.load_model("vibevoice/VibeVoice-1.5B")

    assert engine.status.state is EngineState.ERROR


def test_generation_is_not_claimed_before_runtime_path_is_implemented(monkeypatch) -> None:
    monkeypatch.setattr(
        "impersono.core.inference.backends.vibevoice.detect_vibevoice_dependencies",
        lambda: VibeVoiceDependencyStatus(vibevoice=True, torch=True),
    )
    engine = VibeVoiceEngine(runtime_loader=FakeLoader())
    engine.load_model("vibevoice/VibeVoice-1.5B")

    from impersono.core.inference import GenerationRequest

    with pytest.raises(NotImplementedError, match="intentionally deferred"):
        engine.generate(GenerationRequest(text="Hello"))
