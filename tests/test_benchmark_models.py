from pathlib import Path

import pytest

from impersono.core.benchmark import (
    BenchmarkCase,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkStatus,
)


def test_benchmark_case_preserves_repeatable_inputs() -> None:
    case = BenchmarkCase(
        case_id="short-en-001",
        text="Hello from Impersono.",
        reference_voice=Path("voices/reference.wav"),
        language="en",
        notes="Short baseline sentence.",
        tags=("short", "baseline"),
    )

    assert case.case_id == "short-en-001"
    assert case.reference_voice == Path("voices/reference.wav")
    assert case.tags == ("short", "baseline")


def test_benchmark_case_rejects_empty_identity_or_text() -> None:
    with pytest.raises(ValueError, match="case_id"):
        BenchmarkCase(case_id=" ", text="Hello")

    with pytest.raises(ValueError, match="text"):
        BenchmarkCase(case_id="case", text=" ")


def test_benchmark_metrics_allow_unmeasured_values() -> None:
    metrics = BenchmarkMetrics()

    assert metrics.generation_seconds is None
    assert metrics.peak_memory_mb is None
    assert metrics.quality_scores == {}


def test_benchmark_metrics_reject_negative_measurements() -> None:
    with pytest.raises(ValueError, match="generation_seconds"):
        BenchmarkMetrics(generation_seconds=-0.1)


def test_success_result_requires_output() -> None:
    case = BenchmarkCase(case_id="case", text="Hello")

    with pytest.raises(ValueError, match="output_path"):
        BenchmarkResult(
            case=case,
            status=BenchmarkStatus.SUCCEEDED,
            engine_id="vibevoice",
            model_id="model",
        )


def test_failed_result_requires_error_message() -> None:
    case = BenchmarkCase(case_id="case", text="Hello")

    with pytest.raises(ValueError, match="error_message"):
        BenchmarkResult(
            case=case,
            status=BenchmarkStatus.FAILED,
            engine_id="vibevoice",
            model_id="model",
        )
