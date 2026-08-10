"""Model-specific compatibility guidance built on raw hardware facts.

This module deliberately separates measured hardware facts from model/runtime
compatibility assumptions. Compatibility guidance must remain conservative
until a runtime has actually been verified on the target backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import HardwareInfo


class CompatibilityStatus(str, Enum):
    """Confidence level for a particular local execution path."""

    KNOWN_PATH = "known_path"
    CANDIDATE = "candidate"
    UNCONFIRMED = "unconfirmed"
    NOT_AVAILABLE = "not_available"


@dataclass(frozen=True, slots=True)
class ModelCompatibility:
    """Compatibility guidance for one voice model/runtime profile."""

    model_id: str
    display_name: str
    model_storage_gb: float
    weight_dtype: str
    cpu_status: CompatibilityStatus
    gpu_status: CompatibilityStatus
    gpu_reason: str


VIBEVOICE_1_5B_MODEL_ID = "vibevoice/VibeVoice-1.5B"
VIBEVOICE_1_5B_DISPLAY_NAME = "VibeVoice 1.5B"
VIBEVOICE_1_5B_MODEL_STORAGE_GB = 5.41
VIBEVOICE_1_5B_WEIGHT_DTYPE = "BF16"


def assess_vibevoice_1_5b(info: HardwareInfo) -> ModelCompatibility:
    """Return conservative VibeVoice 1.5B guidance.

    The project has a known-good CPU-only VibeVoice 1.5B reference environment,
    so CPU is recorded as a known execution path. GPU guidance is intentionally
    more cautious: NVIDIA driver tooling makes CUDA a candidate, while other
    detected GPUs remain unconfirmed until the actual inference runtime proves
    compatibility.
    """

    if info.cuda_driver_available and any(
        gpu.vendor == "NVIDIA" for gpu in info.gpus
    ):
        gpu_status = CompatibilityStatus.CANDIDATE
        gpu_reason = (
            "NVIDIA GPU and driver tooling detected. CUDA is a candidate, but "
            "the Impersonic inference runtime must still verify model and VRAM "
            "compatibility."
        )
    elif info.gpus:
        gpu_status = CompatibilityStatus.UNCONFIRMED
        vendors = ", ".join(dict.fromkeys(gpu.vendor for gpu in info.gpus))
        gpu_reason = (
            f"Detected GPU vendor(s): {vendors}. Compatible acceleration for "
            "the VibeVoice reference runtime has not yet been verified on this "
            "machine."
        )
    else:
        gpu_status = CompatibilityStatus.NOT_AVAILABLE
        gpu_reason = "No GPU was detected; use the CPU path unless hardware changes."

    return ModelCompatibility(
        model_id=VIBEVOICE_1_5B_MODEL_ID,
        display_name=VIBEVOICE_1_5B_DISPLAY_NAME,
        model_storage_gb=VIBEVOICE_1_5B_MODEL_STORAGE_GB,
        weight_dtype=VIBEVOICE_1_5B_WEIGHT_DTYPE,
        cpu_status=CompatibilityStatus.KNOWN_PATH,
        gpu_status=gpu_status,
        gpu_reason=gpu_reason,
    )
