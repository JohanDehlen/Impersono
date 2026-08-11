from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from impersono.core.inference.backends.vibevoice_runtime import NativeVibeVoiceRuntime


class FakeTensor:
    def __init__(self, size=48000):
        self.shape = (size,)
        self.to_calls = []

    def to(self, device):
        self.to_calls.append(device)
        return self


class FakeProcessor:
    def __init__(self):
        self.tokenizer = object()
        self.calls = []
        self.saved = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return {"input_ids": FakeTensor(10), "metadata": "keep"}

    def save_audio(self, speech, *, output_path):
        self.saved.append((speech, output_path))


class FakeGenerationModel:
    def __init__(self, speech=None):
        self.speech = speech if speech is not None else FakeTensor()
        self.calls = []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(speech_outputs=[self.speech])


class FakeTorch:
    @staticmethod
    def is_tensor(value):
        return isinstance(value, FakeTensor)


def make_runtime(processor=None, model=None):
    return NativeVibeVoiceRuntime(
        model_id="model",
        processor=processor or FakeProcessor(),
        model=model or FakeGenerationModel(),
        torch_module=FakeTorch(),
        device="cpu",
        torch_dtype_name="float32",
        attention_implementation="sdpa",
    )


def test_runtime_generation_matches_inspected_single_speaker_path(tmp_path):
    processor = FakeProcessor()
    model = FakeGenerationModel(FakeTensor(48000))
    runtime = make_runtime(processor, model)
    reference = tmp_path / "voice.wav"
    reference.write_bytes(b"fake")
    output = tmp_path / "result.wav"

    duration = runtime.generate_to_file(
        text="Hello there.",
        voice_reference=reference,
        output_path=output,
        cfg_scale=1.3,
    )

    assert processor.calls[0]["text"] == ["Speaker 0: Hello there."]
    assert processor.calls[0]["voice_samples"] == [[str(reference)]]
    assert model.calls[0]["cfg_scale"] == 1.3
    assert model.calls[0]["generation_config"] == {"do_sample": False}
    assert model.calls[0]["is_prefill"] is True
    assert processor.saved == [(model.speech, str(output))]
    assert duration == 2.0


def test_runtime_generation_without_reference_disables_prefill(tmp_path):
    processor = FakeProcessor()
    model = FakeGenerationModel()
    runtime = make_runtime(processor, model)
    runtime.generate_to_file(
        text="Speaker 0: Hello.",
        voice_reference=None,
        output_path=tmp_path / "result.wav",
        cfg_scale=1.3,
    )
    assert processor.calls[0]["voice_samples"] is None
    assert model.calls[0]["is_prefill"] is False


def test_runtime_generation_rejects_missing_reference(tmp_path):
    runtime = make_runtime()
    with pytest.raises(FileNotFoundError, match="Voice reference"):
        runtime.generate_to_file(
            text="Hello",
            voice_reference=tmp_path / "missing.wav",
            output_path=tmp_path / "result.wav",
            cfg_scale=1.3,
        )


def test_runtime_generation_rejects_missing_speech_output(tmp_path):
    class NoSpeechModel(FakeGenerationModel):
        def generate(self, **kwargs):
            return SimpleNamespace(speech_outputs=[])

    runtime = make_runtime(model=NoSpeechModel())
    with pytest.raises(RuntimeError, match="no speech audio"):
        runtime.generate_to_file(
            text="Hello",
            voice_reference=None,
            output_path=tmp_path / "result.wav",
            cfg_scale=1.3,
        )
