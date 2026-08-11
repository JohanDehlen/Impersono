import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from impersono.core.benchmark import (
    BENCHMARK_RUN_SCHEMA_VERSION,
    BenchmarkCase,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkRun,
    BenchmarkStatus,
    benchmark_run_from_dict,
    benchmark_run_to_dict,
    load_benchmark_run,
    save_benchmark_run,
)


def sample_run() -> BenchmarkRun:
    result = BenchmarkResult(
        case=BenchmarkCase(case_id="case-001", text="Hello"),
        status=BenchmarkStatus.SUCCEEDED,
        engine_id="vibevoice",
        model_id="vibevoice/VibeVoice-1.5B",
        output_path=Path("output/case-001.wav"),
        metrics=BenchmarkMetrics(
            generation_seconds=12.5,
            audio_duration_seconds=3.0,
        ),
        run_id="run-001",
    )

    return BenchmarkRun(
        run_id="run-001",
        suite_id="baseline-en-v1",
        engine_id="vibevoice",
        model_id="vibevoice/VibeVoice-1.5B",
        started_at=datetime(2026, 8, 11, 9, 30, tzinfo=timezone.utc),
        results=(result,),
        configuration={"device": "cpu", "cfg_scale": 1.3},
        metadata={"notes": "controlled run"},
    )


def test_run_round_trips_through_dictionary() -> None:
    run = sample_run()

    assert benchmark_run_from_dict(benchmark_run_to_dict(run)) == run


def test_run_dictionary_contains_summary_and_configuration() -> None:
    data = benchmark_run_to_dict(sample_run())

    assert data["schema_version"] == BENCHMARK_RUN_SCHEMA_VERSION
    assert data["configuration"]["cfg_scale"] == 1.3
    assert data["summary"] == {
        "total": 1,
        "succeeded": 1,
        "failed": 0,
    }


def test_save_and_load_complete_run(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    run = sample_run()

    save_benchmark_run(run, path)

    assert load_benchmark_run(path) == run
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert parsed["run_id"] == "run-001"
    assert parsed["results"][0]["case"]["case_id"] == "case-001"


def test_unknown_run_schema_version_is_rejected() -> None:
    data = benchmark_run_to_dict(sample_run())
    data["schema_version"] = 999

    with pytest.raises(ValueError, match="Unsupported benchmark run schema_version"):
        benchmark_run_from_dict(data)
