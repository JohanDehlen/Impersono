"""Execution helpers for repeatable Impersono benchmark cases."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from pathlib import Path

from ..inference import GenerationRequest, VoiceEngine
from .models import BenchmarkCase, BenchmarkMetrics, BenchmarkResult, BenchmarkStatus

Clock = Callable[[], float]


def run_benchmark_case(
    engine: VoiceEngine,
    case: BenchmarkCase,
    *,
    model_id: str,
    output_dir: Path,
    options: Mapping[str, object] | None = None,
    run_id: str | None = None,
    metadata: Mapping[str, object] | None = None,
    clock: Clock = time.perf_counter,
) -> BenchmarkResult:
    """Run one case against an already-prepared engine and record measured facts.

    The runner deliberately does not load or unload models. Benchmark setup and
    lifecycle policy remain explicit so loading time can be measured separately
    in later slices without silently mixing it into generation time.
    """

    if not model_id.strip():
        raise ValueError("Benchmark model_id must not be empty.")

    output_dir = Path(output_dir)
    output_path = output_dir / f"{case.case_id}.wav"

    request = GenerationRequest(
        text=case.text,
        voice_reference=case.reference_voice,
        output_path=output_path,
        options=dict(options or {}),
    )

    started = clock()
    try:
        generation = engine.generate(request)
    except Exception as exc:
        elapsed = max(0.0, clock() - started)
        return BenchmarkResult(
            case=case,
            status=BenchmarkStatus.FAILED,
            engine_id=engine.identity.engine_id,
            model_id=model_id,
            metrics=BenchmarkMetrics(generation_seconds=elapsed),
            error_message=f"{type(exc).__name__}: {exc}",
            run_id=run_id,
            metadata=dict(metadata or {}),
        )

    elapsed = max(0.0, clock() - started)

    return BenchmarkResult(
        case=case,
        status=BenchmarkStatus.SUCCEEDED,
        engine_id=generation.engine_id,
        model_id=generation.model_id,
        output_path=generation.audio_path,
        metrics=BenchmarkMetrics(
            generation_seconds=elapsed,
            audio_duration_seconds=generation.duration_seconds,
        ),
        run_id=run_id,
        metadata=dict(metadata or {}),
    )
