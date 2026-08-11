"""JSON persistence for complete Impersono benchmark runs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from .run_models import BenchmarkRun
from .serialization import benchmark_result_from_dict, benchmark_result_to_dict

BENCHMARK_RUN_SCHEMA_VERSION = 1


def benchmark_run_to_dict(run: BenchmarkRun) -> dict[str, Any]:
    return {
        "schema_version": BENCHMARK_RUN_SCHEMA_VERSION,
        "run_id": run.run_id,
        "suite_id": run.suite_id,
        "engine_id": run.engine_id,
        "model_id": run.model_id,
        "started_at": run.started_at.isoformat(),
        "configuration": dict(run.configuration),
        "metadata": dict(run.metadata),
        "results": [
            benchmark_result_to_dict(result)
            for result in run.results
        ],
        "summary": {
            "total": run.total_count,
            "succeeded": run.succeeded_count,
            "failed": run.failed_count,
        },
    }


def benchmark_run_from_dict(data: Mapping[str, Any]) -> BenchmarkRun:
    version = data.get("schema_version")
    if version != BENCHMARK_RUN_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported benchmark run schema_version: {version!r}. "
            f"Expected {BENCHMARK_RUN_SCHEMA_VERSION}."
        )

    started_at = datetime.fromisoformat(str(data["started_at"]))

    return BenchmarkRun(
        run_id=str(data["run_id"]),
        suite_id=str(data["suite_id"]),
        engine_id=str(data["engine_id"]),
        model_id=str(data["model_id"]),
        started_at=started_at,
        results=tuple(
            benchmark_result_from_dict(item)
            for item in data.get("results", ())
        ),
        configuration=dict(data.get("configuration", {})),
        metadata=dict(data.get("metadata", {})),
    )


def save_benchmark_run(run: BenchmarkRun, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            benchmark_run_to_dict(run),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def load_benchmark_run(path: Path) -> BenchmarkRun:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Benchmark run JSON must contain an object.")
    return benchmark_run_from_dict(data)
