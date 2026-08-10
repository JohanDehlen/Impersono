from __future__ import annotations

from impersonic.core.hardware.compatibility import (
    CompatibilityStatus,
    VIBEVOICE_1_5B_MODEL_STORAGE_GB,
    assess_vibevoice_1_5b,
)
from impersonic.core.hardware.compatibility_formatting import (
    format_model_compatibility,
)
from impersonic.core.hardware.models import GpuInfo, HardwareInfo


def _info(
    *,
    gpus: tuple[GpuInfo, ...] = (),
    cuda_driver_available: bool = False,
) -> HardwareInfo:
    return HardwareInfo(
        operating_system="Windows",
        operating_system_version="10.0.26100",
        machine_architecture="AMD64",
        python_version="3.12.10",
        cpu_model="Example CPU",
        logical_cpu_count=8,
        total_ram_bytes=16 * 1024**3,
        gpus=gpus,
        cuda_driver_available=cuda_driver_available,
    )


def test_vibevoice_profile_keeps_storage_separate_from_runtime_memory() -> None:
    assessment = assess_vibevoice_1_5b(_info())

    assert VIBEVOICE_1_5B_MODEL_STORAGE_GB == 5.41
    assert assessment.model_storage_gb == 5.41
    assert assessment.weight_dtype == "BF16"
    assert assessment.cpu_status is CompatibilityStatus.KNOWN_PATH


def test_amd_gpu_remains_unconfirmed() -> None:
    assessment = assess_vibevoice_1_5b(
        _info(
            gpus=(
                GpuInfo(
                    name="AMD Radeon HD 7000 series",
                    vendor="AMD",
                    dedicated_vram_bytes=1024**3,
                ),
            )
        )
    )

    assert assessment.gpu_status is CompatibilityStatus.UNCONFIRMED
    assert "AMD" in assessment.gpu_reason


def test_nvidia_with_driver_is_candidate_not_guaranteed() -> None:
    assessment = assess_vibevoice_1_5b(
        _info(
            gpus=(
                GpuInfo(
                    name="NVIDIA Example",
                    vendor="NVIDIA",
                    dedicated_vram_bytes=12 * 1024**3,
                ),
            ),
            cuda_driver_available=True,
        )
    )

    assert assessment.gpu_status is CompatibilityStatus.CANDIDATE
    assert "must still verify" in assessment.gpu_reason


def test_no_gpu_reports_not_available() -> None:
    assessment = assess_vibevoice_1_5b(_info())

    assert assessment.gpu_status is CompatibilityStatus.NOT_AVAILABLE


def test_compatibility_report_avoids_false_memory_thresholds() -> None:
    assessment = assess_vibevoice_1_5b(
        _info(
            gpus=(
                GpuInfo(
                    name="AMD Radeon HD 7000 series",
                    vendor="AMD",
                    dedicated_vram_bytes=1024**3,
                ),
            )
        )
    )

    report = format_model_compatibility(assessment)

    assert "VibeVoice 1.5B Compatibility" in report
    assert "Model files: approximately 5.41 GB" in report
    assert "Weight precision: BF16" in report
    assert "CPU path: Known execution path" in report
    assert "GPU path: Unconfirmed" in report
    assert "not a RAM or VRAM requirement" in report
