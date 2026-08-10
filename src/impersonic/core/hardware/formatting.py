"""User-facing formatting for hardware discovery results."""

from __future__ import annotations

from .capabilities import GpuAccelerationStatus, assess_hardware
from .models import GpuInfo, HardwareInfo


def _format_bytes_as_gb(value: int | None) -> str:
    if value is None:
        return "Unknown"

    gibibytes = value / (1024**3)
    return f"{gibibytes:.1f} GB"


def _format_gpu(gpu: GpuInfo, index: int) -> list[str]:
    return [
        f"GPU {index}: {gpu.name}",
        f"GPU {index} vendor: {gpu.vendor}",
        f"GPU {index} dedicated VRAM: {_format_bytes_as_gb(gpu.dedicated_vram_bytes)}",
    ]


def _format_gpu_capability(status: GpuAccelerationStatus) -> str:
    if status is GpuAccelerationStatus.CUDA_DRIVER_DETECTED:
        return (
            "NVIDIA CUDA driver tooling detected; model/runtime compatibility "
            "still requires verification."
        )
    if status is GpuAccelerationStatus.GPU_DETECTED_UNCONFIRMED:
        return (
            "GPU detected, but compatible AI acceleration has not yet been confirmed."
        )
    return "No GPU acceleration has been detected."


def format_hardware_report(info: HardwareInfo) -> str:
    """Return a readable summary without exposing implementation details."""

    cpu_count = (
        str(info.logical_cpu_count)
        if info.logical_cpu_count is not None
        else "Unknown"
    )
    capabilities = assess_hardware(info)

    lines = [
        "Hardware Status",
        "",
        f"Operating system: {info.operating_system}",
        f"OS version: {info.operating_system_version}",
        f"Architecture: {info.machine_architecture}",
        f"Python: {info.python_version}",
        f"CPU: {info.cpu_model}",
        f"Logical CPU cores: {cpu_count}",
        f"System RAM: {_format_bytes_as_gb(info.total_ram_bytes)}",
        "",
    ]

    if info.gpus:
        for index, gpu in enumerate(info.gpus, start=1):
            lines.extend(_format_gpu(gpu, index))
    else:
        lines.append("GPU: Not detected")

    lines.extend(
        [
            "",
            (
                "NVIDIA driver/CUDA tool: Detected"
                if info.cuda_driver_available
                else "NVIDIA driver/CUDA tool: Not detected"
            ),
            "",
            "Local generation assessment:",
            "CPU generation path: Available",
            f"GPU acceleration: {_format_gpu_capability(capabilities.gpu_acceleration_status)}",
        ]
    )

    return "\n".join(lines)
