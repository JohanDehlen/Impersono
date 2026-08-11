from __future__ import annotations
from types import SimpleNamespace
import pytest
from impersono.core.inference.backends.vibevoice import VibeVoiceConfig
from impersono.core.inference.backends.vibevoice_runtime import NativeVibeVoiceRuntimeLoader

class FakeProcessorClass:
    calls = []
    @classmethod
    def from_pretrained(cls, model_id):
        cls.calls.append(model_id)
        return SimpleNamespace(model_id=model_id)

class FakeModel:
    def __init__(self):
        self.to_calls = []
        self.eval_calls = 0
        self.ddpm_steps = []
    def to(self, device):
        self.to_calls.append(device)
        return self
    def eval(self):
        self.eval_calls += 1
        return self
    def set_ddpm_inference_steps(self, *, num_steps):
        self.ddpm_steps.append(num_steps)

class FakeModelClass:
    calls = []
    failures_remaining = 0
    instances = []
    @classmethod
    def from_pretrained(cls, model_id, **kwargs):
        cls.calls.append({"model_id": model_id, **kwargs})
        if cls.failures_remaining:
            cls.failures_remaining -= 1
            raise RuntimeError("simulated load failure")
        model = FakeModel()
        cls.instances.append(model)
        return model

class FakeCuda:
    def __init__(self, available=False):
        self.available = available
        self.empty_cache_calls = 0
    def is_available(self):
        return self.available
    def empty_cache(self):
        self.empty_cache_calls += 1

def build_importer(cuda_available=False):
    FakeProcessorClass.calls = []
    FakeModelClass.calls = []
    FakeModelClass.failures_remaining = 0
    FakeModelClass.instances = []
    cuda = FakeCuda(cuda_available)
    torch = SimpleNamespace(float32="FLOAT32", bfloat16="BFLOAT16", cuda=cuda)
    modules = {
        "torch": torch,
        "vibevoice.processor.vibevoice_processor": SimpleNamespace(VibeVoiceProcessor=FakeProcessorClass),
        "vibevoice.modular.modeling_vibevoice_inference": SimpleNamespace(
            VibeVoiceForConditionalGenerationInference=FakeModelClass
        ),
    }
    return (lambda name: modules[name]), cuda

def test_cpu_loader_matches_inspected_path():
    importer, _ = build_importer()
    runtime = NativeVibeVoiceRuntimeLoader(module_importer=importer).load(
        VibeVoiceConfig(device="cpu", inference_steps=10)
    )
    assert FakeProcessorClass.calls == ["vibevoice/VibeVoice-1.5B"]
    assert FakeModelClass.calls == [{
        "model_id": "vibevoice/VibeVoice-1.5B",
        "torch_dtype": "FLOAT32",
        "device_map": "cpu",
        "attn_implementation": "sdpa",
    }]
    model = FakeModelClass.instances[0]
    assert model.to_calls == []
    assert model.eval_calls == 1
    assert model.ddpm_steps == [10]
    assert runtime.torch_dtype_name == "float32"
    assert runtime.attention_implementation == "sdpa"

def test_cuda_loader_prefers_bfloat16_flash_attention():
    importer, _ = build_importer()
    runtime = NativeVibeVoiceRuntimeLoader(module_importer=importer).load(
        VibeVoiceConfig(device="cuda", inference_steps=7)
    )
    assert FakeModelClass.calls[0]["torch_dtype"] == "BFLOAT16"
    assert FakeModelClass.calls[0]["device_map"] == "cuda"
    assert FakeModelClass.calls[0]["attn_implementation"] == "flash_attention_2"
    assert FakeModelClass.instances[0].ddpm_steps == [7]
    assert runtime.attention_implementation == "flash_attention_2"

def test_cuda_loader_falls_back_to_sdpa():
    importer, _ = build_importer()
    FakeModelClass.failures_remaining = 1
    runtime = NativeVibeVoiceRuntimeLoader(module_importer=importer).load(
        VibeVoiceConfig(device="cuda")
    )
    assert len(FakeModelClass.calls) == 2
    assert FakeModelClass.calls[1]["attn_implementation"] == "sdpa"
    assert runtime.attention_implementation == "sdpa"

def test_mps_loader_moves_model_after_load():
    importer, _ = build_importer()
    runtime = NativeVibeVoiceRuntimeLoader(module_importer=importer).load(
        VibeVoiceConfig(device="mps")
    )
    assert FakeModelClass.calls[0]["device_map"] is None
    assert FakeModelClass.instances[0].to_calls == ["mps"]
    assert runtime.device == "mps"

def test_runtime_close_releases_objects_and_cuda_cache():
    importer, cuda = build_importer(True)
    runtime = NativeVibeVoiceRuntimeLoader(module_importer=importer).load(
        VibeVoiceConfig(device="cuda")
    )
    runtime.close()
    runtime.close()
    assert runtime.processor is None
    assert runtime.model is None
    assert runtime.torch_module is None
    assert cuda.empty_cache_calls == 1

def test_cpu_load_failure_is_not_retried():
    importer, _ = build_importer()
    FakeModelClass.failures_remaining = 1
    with pytest.raises(RuntimeError, match="simulated load failure"):
        NativeVibeVoiceRuntimeLoader(module_importer=importer).load(
            VibeVoiceConfig(device="cpu")
        )
    assert len(FakeModelClass.calls) == 1
