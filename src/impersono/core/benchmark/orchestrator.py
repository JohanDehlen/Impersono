"""Whole-suite benchmark execution orchestration."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path

from ..inference import VoiceEngine
from .run_models import BenchmarkRun
from .runner import Clock, run_benchmark_case
from .suite import BenchmarkSuite

StartedAtFactory = Callable[[], datetime]


def run_benchmark_suite(
    engine: VoiceEngine,
    suite: BenchmarkSuite,
    *,
    run_id: str,
    model_id: str,
    output_dir: Path,
    options: Mapping[str, object] | None = None,
    configuration: Mapping[str, object] | None = None,
    metadata: Mapping[str, object] | None = None,
    clock: Clock,
    started_at_factory: StartedAtFactory = lambda: datetime.now(timezone.utc),
) -> BenchmarkRun:
    """Execute every case in order and assemble one validated benchmark run.

    The engine must already be prepared by the caller. Model loading and
    unloading remain outside this function so generation timing stays separate
    from model lifecycle timing.
    """

    if not run_id.strip():
        raise ValueError("Benchmark run_id must not be empty.")
    if not model_id.strip():
        raise ValueError("Benchmark model_id must not be empty.")

    started_at = started_at_factory()
    if started_at.tzinfo is None or started_at.utcoffset() is None:
        raise ValueError("Benchmark started_at must be timezone-aware.")

    engine_id = engine.identity.engine_id
    results = tuple(
        run_benchmark_case(
            engine,
            case,
            model_id=model_id,
            output_dir=Path(output_dir),
            options=options,
            run_id=run_id,
            metadata=metadata,
            clock=clock,
        )
        for case in suite.cases
    )

    return BenchmarkRun(
        run_id=run_id,
        suite_id=suite.suite_id,
        engine_id=engine_id,
        model_id=model_id,
        started_at=started_at,
        results=results,
        configuration=dict(configuration or {}),
        metadata=dict(metadata or {}),
    )
