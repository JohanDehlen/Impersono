"""Conservative interpretation of raw hardware facts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import HardwareInfo


class GpuAccelerationStatus(str, Enum):
    """Current confidence about local GPU acceleration availability."""

    CUDA_DRIVER_DETECTED = "cuda_driver_detected"
    GPU_DETECTED_UNCONFIRMED = "gpu_detected_unconfirmed"
    NO_GPU_DETECTED = "no_gpu_detected"


@dataclass(frozen=True, slots=True)
class HardwareCapabilities:
    """Model-independent capabilities inferred from raw hardware facts."""

    cpu_generation_available: bool
    gpu_acceleration_status: GpuAccelerationStatus


def assess_hardware(info: HardwareInfo) -> HardwareCapabilities:
    """Interpret hardware conservatively without claiming model compatibility."""

    if info.cuda_driver_available:
        gpu_status = GpuAccelerationStatus.CUDA_DRIVER_DETECTED
    elif info.gpus:
        gpu_status = GpuAccelerationStatus.GPU_DETECTED_UNCONFIRMED
    else:
        gpu_status = GpuAccelerationStatus.NO_GPU_DETECTED

    return HardwareCapabilities(
        cpu_generation_available=True,
        gpu_acceleration_status=gpu_status,
    )
