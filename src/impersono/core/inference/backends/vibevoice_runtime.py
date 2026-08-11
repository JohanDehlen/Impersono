"""Native loader for the inspected VibeVoice runtime."""
from __future__ import annotations
import gc
from dataclasses import dataclass
from importlib import import_module
from typing import Callable, Protocol

class VibeVoiceLoadConfig(Protocol):
    model_id: str
    device: str
    inference_steps: int
    cfg_scale: float

@dataclass(slots=True)
class NativeVibeVoiceRuntime:
    model_id: str
    processor: object | None
    model: object | None
    torch_module: object | None
    device: str
    torch_dtype_name: str
    attention_implementation: str
    _closed: bool = False

    def close(self) -> None:
        if self._closed:
            return
        self.processor = None
        self.model = None
        torch_module = self.torch_module
        self.torch_module = None
        if torch_module is not None:
            cuda = getattr(torch_module, "cuda", None)
            if cuda is not None:
                is_available = getattr(cuda, "is_available", None)
                empty_cache = getattr(cuda, "empty_cache", None)
                try:
                    if callable(is_available) and is_available() and callable(empty_cache):
                        empty_cache()
                except Exception:
                    pass
        gc.collect()
        self._closed = True

class NativeVibeVoiceRuntimeLoader:
    def __init__(self, *, module_importer: Callable[[str], object] = import_module) -> None:
        self._import_module = module_importer

    def load(self, config: VibeVoiceLoadConfig) -> NativeVibeVoiceRuntime:
        torch = self._import_module("torch")
        processor_module = self._import_module("vibevoice.processor.vibevoice_processor")
        model_module = self._import_module("vibevoice.modular.modeling_vibevoice_inference")
        processor_class = getattr(processor_module, "VibeVoiceProcessor")
        model_class = getattr(model_module, "VibeVoiceForConditionalGenerationInference")
        processor = processor_class.from_pretrained(config.model_id)

        if config.device == "cuda":
            dtype = getattr(torch, "bfloat16")
            dtype_name = "bfloat16"
            primary_attention = "flash_attention_2"
            device_map = "cuda"
        elif config.device == "mps":
            dtype = getattr(torch, "float32")
            dtype_name = "float32"
            primary_attention = "sdpa"
            device_map = None
        else:
            dtype = getattr(torch, "float32")
            dtype_name = "float32"
            primary_attention = "sdpa"
            device_map = "cpu"

        try:
            model = model_class.from_pretrained(
                config.model_id,
                torch_dtype=dtype,
                device_map=device_map,
                attn_implementation=primary_attention,
            )
            attention = primary_attention
        except Exception:
            if primary_attention != "flash_attention_2":
                raise
            model = model_class.from_pretrained(
                config.model_id,
                torch_dtype=dtype,
                device_map="cuda",
                attn_implementation="sdpa",
            )
            attention = "sdpa"

        if config.device == "mps":
            model.to("mps")

        model.eval()
        model.set_ddpm_inference_steps(num_steps=config.inference_steps)

        return NativeVibeVoiceRuntime(
            model_id=config.model_id,
            processor=processor,
            model=model,
            torch_module=torch,
            device=config.device,
            torch_dtype_name=dtype_name,
            attention_implementation=attention,
        )
