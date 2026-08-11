from datetime import datetime, timezone
from pathlib import Path

import pytest

from impersono.core.benchmark import (
    BenchmarkCase,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkRun,
    BenchmarkStatus,
)


def result(
    case_id: str,
    *,
    run_id: str = "run-001",
    engine_id: str = "vibevoice",
    model_id: str = "vibevoice/VibeVoice-1.5B",
    status: BenchmarkStatus = BenchmarkStatus.SUCCEEDED,
) -> BenchmarkResult:
    return BenchmarkResult(
        case=BenchmarkCase(case_id=case_id, text="Hello"),
        status=status,
        engine_id=engine_id,
        model_id=model_id,
        output_path=Path(f"{case_id}.wav") if status is BenchmarkStatus.SUCCEEDED else None,
        metrics=BenchmarkMetrics(generation_seconds=1.0),
        error_message="failed" if status is BenchmarkStatus.FAILED else None,
        run_id=run_id,
    )


def sample_run() -> BenchmarkRun:
    return BenchmarkRun(
        run_id="run-001",
        suite_id="baseline-en-v1",
        engine_id="vibevoice",
        model_id="vibevoice/VibeVoice-1.5B",
        started_at=datetime(2026, 8, 11, 9, 30, tzinfo=timezone.utc),
        results=(
            result("case-001"),
            result("case-002", status=BenchmarkStatus.FAILED),
        ),
        configuration={"device": "cpu", "cfg_scale": 1.3},
        metadata={"machine": "primary-windows-dev"},
    )


def test_run_counts_successes_and_failures() -> None:
    run = sample_run()

    assert run.total_count == 2
    assert run.succeeded_count == 1
    assert run.failed_count == 1


def test_run_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        BenchmarkRun(
            run_id="run-001",
            suite_id="suite",
            engine_id="vibevoice",
            model_id="model",
            started_at=datetime(2026, 8, 11, 9, 30),
            results=(),
        )


def test_run_rejects_result_with_mismatched_run_id() -> None:
    with pytest.raises(ValueError, match="run_id"):
        BenchmarkRun(
            run_id="run-001",
            suite_id="suite",
            engine_id="vibevoice",
            model_id="vibevoice/VibeVoice-1.5B",
            started_at=datetime.now(timezone.utc),
            results=(result("case", run_id="other"),),
        )


def test_run_rejects_result_with_mismatched_engine_or_model() -> None:
    with pytest.raises(ValueError, match="engine_id"):
        BenchmarkRun(
            run_id="run-001",
            suite_id="suite",
            engine_id="vibevoice",
            model_id="vibevoice/VibeVoice-1.5B",
            started_at=datetime.now(timezone.utc),
            results=(result("case", engine_id="other"),),
        )

    with pytest.raises(ValueError, match="model_id"):
        BenchmarkRun(
            run_id="run-001",
            suite_id="suite",
            engine_id="vibevoice",
            model_id="vibevoice/VibeVoice-1.5B",
            started_at=datetime.now(timezone.utc),
            results=(result("case", model_id="other"),),
        )


def test_run_rejects_duplicate_case_ids() -> None:
    with pytest.raises(ValueError, match="unique"):
        BenchmarkRun(
            run_id="run-001",
            suite_id="suite",
            engine_id="vibevoice",
            model_id="vibevoice/VibeVoice-1.5B",
            started_at=datetime.now(timezone.utc),
            results=(result("case"), result("case")),
        )


def test_empty_run_factory_uses_supplied_identity() -> None:
    started = datetime(2026, 8, 11, 9, 30, tzinfo=timezone.utc)

    run = BenchmarkRun.empty(
        run_id="run-empty",
        suite_id="baseline-en-v1",
        engine_id="vibevoice",
        model_id="model",
        started_at=started,
        configuration={"device": "cpu"},
    )

    assert run.started_at == started
    assert run.results == ()
    assert run.configuration == {"device": "cpu"}
