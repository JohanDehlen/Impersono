"""Native loader/runtime for the inspected VibeVoice implementation."""

from __future__ import annotations

import gc
import random
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
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

    def generate_to_file(
        self,
        *,
        text: str,
        voice_reference: Path | None,
        output_path: Path,
        cfg_scale: float,
        seed: int | None = None,
    ) -> float | None:
        if self._closed or self.processor is None or self.model is None:
            raise RuntimeError("VibeVoice runtime is closed.")

        torch = self.torch_module
        if torch is None:
            raise RuntimeError("VibeVoice torch runtime is unavailable.")

        if seed is not None:
            random.seed(seed)
            try:
                numpy = import_module("numpy")
            except ImportError:
                numpy = None
            if numpy is not None:
                numpy.random.seed(seed)
            torch.manual_seed(seed)
            cuda = getattr(torch, "cuda", None)
            if cuda is not None:
                is_available = getattr(cuda, "is_available", None)
                manual_seed_all = getattr(cuda, "manual_seed_all", None)
                if (
                    callable(is_available)
                    and is_available()
                    and callable(manual_seed_all)
                ):
                    manual_seed_all(seed)

        formatted_text = text.replace("’", "'").strip()
        if not formatted_text.lower().startswith("speaker "):
            formatted_text = f"Speaker 0: {formatted_text}"

        voice_samples = None
        if voice_reference is not None:
            reference = Path(voice_reference)
            if not reference.is_file():
                raise FileNotFoundError(
                    f"Voice reference file not found: {reference}"
                )
            voice_samples = [[str(reference)]]

        inputs = self.processor(
            text=[formatted_text],
            voice_samples=voice_samples,
            padding=True,
            return_tensors="pt",
            return_attention_mask=True,
        )

        target_device = self.device if self.device != "cpu" else "cpu"
        for key, value in inputs.items():
            if torch.is_tensor(value):
                inputs[key] = value.to(target_device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=None,
            cfg_scale=cfg_scale,
            tokenizer=self.processor.tokenizer,
            generation_config={"do_sample": False},
            verbose=False,
            is_prefill=voice_reference is not None,
        )

        speech_outputs = getattr(outputs, "speech_outputs", None)
        if not speech_outputs or speech_outputs[0] is None:
            raise RuntimeError("VibeVoice returned no speech audio.")

        speech = speech_outputs[0]
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.processor.save_audio(speech, output_path=str(output_path))

        sample_count = (
            speech.shape[-1]
            if hasattr(speech, "shape") and len(speech.shape) > 0
            else len(speech)
        )
        return float(sample_count) / 24000.0

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
