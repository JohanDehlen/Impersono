from __future__ import annotations

from impersonic.core.hardware import (
    GpuAccelerationStatus,
    GpuInfo,
    HardwareInfo,
    assess_hardware,
    detect_hardware,
    format_hardware_report,
)


def _hardware_info(
    *,
    gpus: tuple[GpuInfo, ...] = (),
    cuda_driver_available: bool = False,
) -> HardwareInfo:
    return HardwareInfo(
        operating_system="Windows",
        operating_system_version="11",
        machine_architecture="AMD64",
        python_version="3.12.10",
        cpu_model="Example CPU",
        logical_cpu_count=16,
        total_ram_bytes=32 * 1024**3,
        gpus=gpus,
        cuda_driver_available=cuda_driver_available,
    )


def test_detect_hardware_returns_structured_information() -> None:
    info = detect_hardware()

    assert isinstance(info, HardwareInfo)
    assert info.operating_system
    assert info.operating_system_version
    assert info.machine_architecture
    assert info.python_version
    assert info.cpu_model

    if info.logical_cpu_count is not None:
        assert info.logical_cpu_count > 0

    if info.total_ram_bytes is not None:
        assert info.total_ram_bytes > 0

    for gpu in info.gpus:
        assert gpu.name
        assert gpu.vendor
        if gpu.dedicated_vram_bytes is not None:
            assert gpu.dedicated_vram_bytes > 0


def test_format_hardware_report_uses_friendly_values() -> None:
    info = _hardware_info(
        gpus=(
            GpuInfo(
                name="Example GPU",
                vendor="AMD",
                dedicated_vram_bytes=8 * 1024**3,
            ),
        ),
    )

    report = format_hardware_report(info)

    assert "Hardware Status" in report
    assert "Operating system: Windows" in report
    assert "Architecture: AMD64" in report
    assert "Python: 3.12.10" in report
    assert "CPU: Example CPU" in report
    assert "Logical CPU cores: 16" in report
    assert "System RAM: 32.0 GB" in report
    assert "GPU 1: Example GPU" in report
    assert "GPU 1 vendor: AMD" in report
    assert "GPU 1 dedicated VRAM: 8.0 GB" in report
    assert "NVIDIA driver/CUDA tool: Not detected" in report
    assert "CPU generation path: Available" in report
    assert "compatible AI acceleration has not yet been confirmed" in report


def test_format_hardware_report_handles_unknown_values() -> None:
    info = HardwareInfo(
        operating_system="Windows",
        operating_system_version="11",
        machine_architecture="AMD64",
        python_version="3.12.10",
        cpu_model="Unknown",
        logical_cpu_count=None,
        total_ram_bytes=None,
    )

    report = format_hardware_report(info)

    assert "CPU: Unknown" in report
    assert "Logical CPU cores: Unknown" in report
    assert "System RAM: Unknown" in report
    assert "GPU: Not detected" in report
    assert "No GPU acceleration has been detected" in report


def test_assessment_is_conservative_for_non_cuda_gpu() -> None:
    info = _hardware_info(
        gpus=(
            GpuInfo(
                name="AMD Radeon",
                vendor="AMD",
                dedicated_vram_bytes=1024**3,
            ),
        )
    )

    assessment = assess_hardware(info)

    assert assessment.cpu_generation_available is True
    assert (
        assessment.gpu_acceleration_status
        is GpuAccelerationStatus.GPU_DETECTED_UNCONFIRMED
    )


def test_assessment_reports_cuda_driver_without_claiming_model_support() -> None:
    info = _hardware_info(
        gpus=(
            GpuInfo(
                name="NVIDIA Example",
                vendor="NVIDIA",
                dedicated_vram_bytes=12 * 1024**3,
            ),
        ),
        cuda_driver_available=True,
    )

    assessment = assess_hardware(info)

    assert (
        assessment.gpu_acceleration_status
        is GpuAccelerationStatus.CUDA_DRIVER_DETECTED
    )
