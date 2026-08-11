"""Controlled local VibeVoice benchmark harness.

This module is intentionally opt-in. Running it without ``--run`` only prints
the plan; real model loading and generation happen only with explicit ``--run``.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from .orchestrator import run_benchmark_suite
from .run_serialization import save_benchmark_run
from .suite import BASELINE_ENGLISH_SUITE, BenchmarkSuite

DEFAULT_VIBEVOICE_ROOT = Path(r"C:\AI\VibeVoice")
DEFAULT_REFERENCE = DEFAULT_VIBEVOICE_ROOT / "demo" / "voices" / "en-Alice_woman.wav"
DEFAULT_OUTPUT_ROOT = Path("output") / "benchmarks"
DEFAULT_HF_CACHE = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--vibevoice--VibeVoice-1.5B"
)


def find_local_snapshot(cache_root: Path = DEFAULT_HF_CACHE) -> Path:
    """Return the newest locally cached VibeVoice 1.5B snapshot."""

    snapshots = Path(cache_root) / "snapshots"
    if not snapshots.is_dir():
        raise FileNotFoundError(f"VibeVoice snapshot directory not found: {snapshots}")

    candidates = sorted(
        (path for path in snapshots.iterdir() if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for candidate in candidates:
        if (candidate / "config.json").is_file():
            return candidate

    raise FileNotFoundError(
        f"No cached VibeVoice snapshot containing config.json found in: {snapshots}"
    )


def conditioned_suite(reference_voice: Path) -> BenchmarkSuite:
    """Return the fixed baseline suite with one shared reference voice."""

    reference_voice = Path(reference_voice)
    return BenchmarkSuite(
        suite_id=BASELINE_ENGLISH_SUITE.suite_id,
        display_name=BASELINE_ENGLISH_SUITE.display_name,
        cases=tuple(
            replace(case, reference_voice=reference_voice)
            for case in BASELINE_ENGLISH_SUITE.cases
        ),
    )


def limit_suite(suite: BenchmarkSuite, max_cases: int | None) -> BenchmarkSuite:
    """Return the first N cases while preserving stable suite order."""

    if max_cases is None:
        return suite
    if max_cases < 1:
        raise ValueError("max_cases must be at least 1.")
    return BenchmarkSuite(
        suite_id=suite.suite_id,
        display_name=suite.display_name,
        cases=suite.cases[:max_cases],
    )


def build_run_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.strftime("vibevoice-cpu-%Y%m%dT%H%M%SZ")


def print_plan(
    suite: BenchmarkSuite,
    *,
    model_path: Path,
    reference_voice: Path,
    output_dir: Path,
) -> None:
    print()
    print("# Impersono Local VibeVoice Benchmark Plan")
    print()
    print(f"Suite: {suite.suite_id}")
    print(f"Cases selected: {len(suite.cases)}")
    print(f"Model: {model_path}")
    print(f"Reference voice: {reference_voice}")
    print(f"Output directory: {output_dir}")
    print("Device: CPU")
    print("Inference steps: 10")
    print("CFG scale: 1.3")
    print("Output normalization: -16 dBFS RMS / -1 dBFS peak ceiling")
    print("Network: forced offline")
    print()
    print("Cases:")
    for index, case in enumerate(suite.cases, 1):
        print(f"  {index}. {case.case_id}: {case.text}")
    print()


def execute_local_vibevoice_benchmark(
    *,
    suite: BenchmarkSuite,
    model_path: Path,
    reference_voice: Path,
    output_root: Path,
    vibevoice_root: Path = DEFAULT_VIBEVOICE_ROOT,
    run_id: str | None = None,
):
    """Load VibeVoice once, run the selected cases, persist one run JSON."""

    model_path = Path(model_path)
    reference_voice = Path(reference_voice)
    vibevoice_root = Path(vibevoice_root)
    output_root = Path(output_root)

    if not model_path.is_dir():
        raise FileNotFoundError(f"Model snapshot not found: {model_path}")
    if not reference_voice.is_file():
        raise FileNotFoundError(f"Reference voice not found: {reference_voice}")
    if not vibevoice_root.is_dir():
        raise FileNotFoundError(f"VibeVoice root not found: {vibevoice_root}")

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"

    source_root = Path(__file__).resolve().parents[4]
    for path in (source_root, vibevoice_root):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)

    from ..inference.backends.vibevoice import VibeVoiceConfig, VibeVoiceEngine
    from ..inference.backends.vibevoice_runtime import NativeVibeVoiceRuntimeLoader

    run_id = run_id or build_run_id()
    run_output = output_root / run_id
    audio_output = run_output / "audio"
    result_path = run_output / "run.json"
    audio_output.mkdir(parents=True, exist_ok=True)

    engine = VibeVoiceEngine(
        VibeVoiceConfig(
            model_id=str(model_path),
            device="cpu",
            inference_steps=10,
            cfg_scale=1.3,
            normalize_output=True,
            target_rms_dbfs=-16.0,
            peak_ceiling_dbfs=-1.0,
        ),
        runtime_loader=NativeVibeVoiceRuntimeLoader(),
    )

    try:
        print(f"Loading VibeVoice model: {model_path}")
        engine.load_model(str(model_path))
        print("Model loaded. Starting benchmark cases...")

        run = run_benchmark_suite(
            engine,
            suite,
            run_id=run_id,
            model_id=str(model_path),
            output_dir=audio_output,
            options={"cfg_scale": 1.3},
            configuration={
                "device": "cpu",
                "precision": "float32",
                "attention": "sdpa",
                "inference_steps": 10,
                "cfg_scale": 1.3,
                "normalize_output": True,
                "target_rms_dbfs": -16.0,
                "peak_ceiling_dbfs": -1.0,
                "reference_voice": str(reference_voice),
            },
            metadata={
                "runtime": "local",
                "network": "offline",
            },
            clock=__import__("time").perf_counter,
        )

        save_benchmark_run(run, result_path)
        return run, result_path
    finally:
        print("Unloading model...")
        engine.unload_model()
        print("Model unloaded.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan or run the local Impersono VibeVoice benchmark."
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Actually load VibeVoice and generate audio. Without this flag, only show the plan.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=1,
        help="Number of baseline cases to select. Default: 1. Use 6 for the full suite.",
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=DEFAULT_REFERENCE,
        help="Reference voice WAV.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=None,
        help="Cached VibeVoice snapshot. If omitted, discover it from the local HF cache.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Local benchmark output root.",
    )
    parser.add_argument(
        "--vibevoice-root",
        type=Path,
        default=DEFAULT_VIBEVOICE_ROOT,
        help="Local VibeVoice repository root.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    model_path = args.model_path or find_local_snapshot()
    suite = limit_suite(conditioned_suite(args.reference), args.max_cases)

    print_plan(
        suite,
        model_path=model_path,
        reference_voice=args.reference,
        output_dir=args.output_root,
    )

    if not args.run:
        print("PLAN ONLY — no model was loaded and no audio was generated.")
        print("Re-run with --run when you are ready.")
        return 0

    run, result_path = execute_local_vibevoice_benchmark(
        suite=suite,
        model_path=model_path,
        reference_voice=args.reference,
        output_root=args.output_root,
        vibevoice_root=args.vibevoice_root,
    )

    print()
    print("BENCHMARK COMPLETE")
    print(f"Results: {run.succeeded_count} succeeded, {run.failed_count} failed")
    print(f"Run JSON: {result_path}")
    for result in run.results:
        print(
            f"  {result.case.case_id}: {result.status.value}; "
            f"generation={result.metrics.generation_seconds:.2f}s; "
            f"audio={result.metrics.audio_duration_seconds}"
        )
    return 0 if run.failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
