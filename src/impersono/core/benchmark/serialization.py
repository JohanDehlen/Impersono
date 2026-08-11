"""JSON persistence for Impersono benchmark results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .models import BenchmarkCase, BenchmarkMetrics, BenchmarkResult, BenchmarkStatus

BENCHMARK_SCHEMA_VERSION = 1


def benchmark_result_to_dict(result: BenchmarkResult) -> dict[str, Any]:
    return {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "case": {
            "case_id": result.case.case_id,
            "text": result.case.text,
            "reference_voice": (
                str(result.case.reference_voice)
                if result.case.reference_voice is not None
                else None
            ),
            "language": result.case.language,
            "notes": result.case.notes,
            "tags": list(result.case.tags),
        },
        "status": result.status.value,
        "engine_id": result.engine_id,
        "model_id": result.model_id,
        "output_path": (
            str(result.output_path) if result.output_path is not None else None
        ),
        "metrics": {
            "generation_seconds": result.metrics.generation_seconds,
            "audio_duration_seconds": result.metrics.audio_duration_seconds,
            "peak_memory_mb": result.metrics.peak_memory_mb,
            "peak_vram_mb": result.metrics.peak_vram_mb,
            "quality_scores": dict(result.metrics.quality_scores),
        },
        "error_message": result.error_message,
        "run_id": result.run_id,
        "metadata": dict(result.metadata),
    }


def benchmark_result_from_dict(data: Mapping[str, Any]) -> BenchmarkResult:
    version = data.get("schema_version")
    if version != BENCHMARK_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported benchmark schema_version: {version!r}. "
            f"Expected {BENCHMARK_SCHEMA_VERSION}."
        )

    case_data = data["case"]
    metrics_data = data["metrics"]
    reference_raw = case_data.get("reference_voice")
    output_raw = data.get("output_path")

    return BenchmarkResult(
        case=BenchmarkCase(
            case_id=str(case_data["case_id"]),
            text=str(case_data["text"]),
            reference_voice=Path(reference_raw) if reference_raw is not None else None,
            language=case_data.get("language"),
            notes=case_data.get("notes"),
            tags=tuple(case_data.get("tags", ())),
        ),
        status=BenchmarkStatus(data["status"]),
        engine_id=str(data["engine_id"]),
        model_id=str(data["model_id"]),
        output_path=Path(output_raw) if output_raw is not None else None,
        metrics=BenchmarkMetrics(
            generation_seconds=metrics_data.get("generation_seconds"),
            audio_duration_seconds=metrics_data.get("audio_duration_seconds"),
            peak_memory_mb=metrics_data.get("peak_memory_mb"),
            peak_vram_mb=metrics_data.get("peak_vram_mb"),
            quality_scores=dict(metrics_data.get("quality_scores", {})),
        ),
        error_message=data.get("error_message"),
        run_id=data.get("run_id"),
        metadata=dict(data.get("metadata", {})),
    )


def save_benchmark_result(result: BenchmarkResult, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            benchmark_result_to_dict(result),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def load_benchmark_result(path: Path) -> BenchmarkResult:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Benchmark result JSON must contain an object.")
    return benchmark_result_from_dict(data)
