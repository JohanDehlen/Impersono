import json
from pathlib import Path

import pytest

from impersono.core.benchmark import (
    BENCHMARK_SCHEMA_VERSION,
    BenchmarkCase,
    BenchmarkMetrics,
    BenchmarkResult,
    BenchmarkStatus,
    benchmark_result_from_dict,
    benchmark_result_to_dict,
    load_benchmark_result,
    save_benchmark_result,
)


def sample_result() -> BenchmarkResult:
    return BenchmarkResult(
        case=BenchmarkCase(
            case_id="short-en-001",
            text="Hello from Impersono.",
            reference_voice=Path("voices/alice.wav"),
            language="en",
            tags=("short", "voice-clone"),
        ),
        status=BenchmarkStatus.SUCCEEDED,
        engine_id="vibevoice",
        model_id="vibevoice/VibeVoice-1.5B",
        output_path=Path("output/short-en-001.wav"),
        metrics=BenchmarkMetrics(
            generation_seconds=12.5,
            audio_duration_seconds=3.2,
            peak_memory_mb=4096.0,
            quality_scores={"voice_similarity": 4.5},
        ),
        run_id="run-001",
        metadata={"device": "cpu", "cfg_scale": 1.3},
    )


def test_benchmark_result_round_trips_through_dictionary() -> None:
    result = sample_result()

    assert benchmark_result_from_dict(benchmark_result_to_dict(result)) == result


def test_benchmark_dictionary_has_explicit_schema_version() -> None:
    data = benchmark_result_to_dict(sample_result())

    assert data["schema_version"] == BENCHMARK_SCHEMA_VERSION
    assert data["metrics"]["quality_scores"]["voice_similarity"] == 4.5


def test_save_and_load_benchmark_result_json(tmp_path: Path) -> None:
    path = tmp_path / "results" / "case.json"
    result = sample_result()

    save_benchmark_result(result, path)

    assert load_benchmark_result(path) == result
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == 1


def test_unknown_schema_version_is_rejected() -> None:
    data = benchmark_result_to_dict(sample_result())
    data["schema_version"] = 999

    with pytest.raises(ValueError, match="Unsupported benchmark schema_version"):
        benchmark_result_from_dict(data)
