"""VibeVoice backend boundary for Impersono.

Heavy VibeVoice/PyTorch imports remain isolated behind the runtime loader.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Protocol

from ..engine import ProgressCallback, VoiceEngine
from ..errors import EngineError, EngineNotReadyError, ModelLoadError
from ..models import (
    EngineCapabilities,
    EngineIdentity,
    EngineModel,
    EngineState,
    EngineStatus,
    GenerationRequest,
    GenerationResult,
)


@dataclass(frozen=True, slots=True)
class VibeVoiceConfig:
    model_id: str = "vibevoice/VibeVoice-1.5B"
    device: str = "cpu"
    inference_steps: int = 10
    cfg_scale: float = 1.3

    def __post_init__(self) -> None:
        if self.device not in {"cpu", "cuda", "mps"}:
            raise ValueError("VibeVoice device must be 'cpu', 'cuda', or 'mps'.")
        if self.inference_steps < 1:
            raise ValueError("VibeVoice inference_steps must be at least 1.")
        if self.cfg_scale <= 0:
            raise ValueError("VibeVoice cfg_scale must be greater than 0.")


@dataclass(frozen=True, slots=True)
class VibeVoiceDependencyStatus:
    vibevoice: bool
    torch: bool

    @property
    def available(self) -> bool:
        return self.vibevoice and self.torch

    @property
    def missing(self) -> tuple[str, ...]:
        missing: list[str] = []
        if not self.vibevoice:
            missing.append("vibevoice")
        if not self.torch:
            missing.append("torch")
        return tuple(missing)


def detect_vibevoice_dependencies() -> VibeVoiceDependencyStatus:
    return VibeVoiceDependencyStatus(
        vibevoice=find_spec("vibevoice") is not None,
        torch=find_spec("torch") is not None,
    )


class VibeVoiceRuntime(Protocol):
    model_id: str

    def generate_to_file(
        self,
        *,
        text: str,
        voice_reference: Path | None,
        output_path: Path,
        cfg_scale: float,
    ) -> float | None:
        ...

    def close(self) -> None:
        ...


class VibeVoiceRuntimeLoader(Protocol):
    def load(self, config: VibeVoiceConfig) -> VibeVoiceRuntime:
        ...


class VibeVoiceEngine(VoiceEngine):
    def __init__(
        self,
        config: VibeVoiceConfig | None = None,
        *,
        runtime_loader: VibeVoiceRuntimeLoader | None = None,
    ) -> None:
        self._config = config or VibeVoiceConfig()
        self._runtime_loader = runtime_loader
        self._runtime: VibeVoiceRuntime | None = None
        self._state = EngineState.UNLOADED
        self._message: str | None = None

    @property
    def identity(self) -> EngineIdentity:
        return EngineIdentity(
            engine_id="vibevoice",
            display_name="VibeVoice",
            engine_version="community-compatible",
        )

    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_voice_conditioning=True,
            supports_cancellation=False,
            supports_progress=False,
            supports_multi_speaker=True,
            supports_streaming=False,
        )

    @property
    def status(self) -> EngineStatus:
        return EngineStatus(
            state=self._state,
            loaded_model_id=(
                self._runtime.model_id if self._runtime is not None else None
            ),
            message=self._message,
        )

    @property
    def config(self) -> VibeVoiceConfig:
        return self._config

    def list_models(self) -> tuple[EngineModel, ...]:
        dependencies = detect_vibevoice_dependencies()
        loaded = (
            self._runtime is not None
            and self._runtime.model_id == self._config.model_id
        )
        return (
            EngineModel(
                model_id=self._config.model_id,
                display_name="VibeVoice 1.5B",
                is_available=dependencies.available,
                is_loaded=loaded,
            ),
        )

    def load_model(self, model_id: str) -> None:
        if model_id != self._config.model_id:
            raise ModelLoadError(
                f"VibeVoice backend is configured for '{self._config.model_id}', "
                f"not '{model_id}'."
            )

        dependencies = detect_vibevoice_dependencies()
        if not dependencies.available:
            missing = ", ".join(dependencies.missing)
            self._state = EngineState.ERROR
            self._message = (
                f"Missing optional VibeVoice runtime dependencies: {missing}."
            )
            raise ModelLoadError(self._message)

        if self._runtime_loader is None:
            self._state = EngineState.ERROR
            self._message = "VibeVoice runtime loader is not configured."
            raise ModelLoadError(self._message)

        self._state = EngineState.LOADING
        self._message = f"Loading {model_id} on {self._config.device}."

        try:
            runtime = self._runtime_loader.load(self._config)
        except Exception as exc:
            self._state = EngineState.ERROR
            self._message = f"Failed to load VibeVoice model '{model_id}': {exc}"
            raise ModelLoadError(self._message) from exc

        if runtime.model_id != model_id:
            try:
                runtime.close()
            finally:
                self._state = EngineState.ERROR
                self._message = (
                    "VibeVoice runtime loader returned an unexpected model: "
                    f"'{runtime.model_id}'."
                )
            raise ModelLoadError(self._message)

        self._runtime = runtime
        self._state = EngineState.READY
        self._message = None

    def unload_model(self) -> None:
        runtime = self._runtime
        self._runtime = None
        if runtime is not None:
            runtime.close()
        self._state = EngineState.UNLOADED
        self._message = None

    def generate(
        self,
        request: GenerationRequest,
        progress: ProgressCallback | None = None,
    ) -> GenerationResult:
        if self._runtime is None or self._state is not EngineState.READY:
            raise EngineNotReadyError(
                "VibeVoice generation requires a successfully loaded model."
            )

        text = request.text.strip()
        if not text:
            raise ValueError("VibeVoice generation text must not be empty.")

        output_path = request.output_path or Path("output") / "vibevoice_generated.wav"

        cfg_scale_raw = request.options.get("cfg_scale", self._config.cfg_scale)
        try:
            cfg_scale = float(cfg_scale_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("VibeVoice cfg_scale must be numeric.") from exc
        if cfg_scale <= 0:
            raise ValueError("VibeVoice cfg_scale must be greater than 0.")

        self._state = EngineState.GENERATING
        self._message = "Generating speech with VibeVoice."

        try:
            duration = self._runtime.generate_to_file(
                text=text,
                voice_reference=request.voice_reference,
                output_path=output_path,
                cfg_scale=cfg_scale,
            )
        except Exception as exc:
            self._state = EngineState.ERROR
            self._message = f"VibeVoice generation failed: {exc}"
            raise EngineError(self._message) from exc

        self._state = EngineState.READY
        self._message = None

        return GenerationResult(
            audio_path=output_path,
            engine_id=self.identity.engine_id,
            model_id=self._runtime.model_id,
            duration_seconds=duration,
        )

    def cancel(self) -> None:
        return None
