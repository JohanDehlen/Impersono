"""Benchmark models and persistence helpers for Impersono."""

from .models import BenchmarkCase, BenchmarkMetrics, BenchmarkResult, BenchmarkStatus
from .runner import run_benchmark_case
from .suite import BASELINE_ENGLISH_SUITE, BenchmarkSuite
from .serialization import (
    BENCHMARK_SCHEMA_VERSION,
    benchmark_result_from_dict,
    benchmark_result_to_dict,
    load_benchmark_result,
    save_benchmark_result,
)

__all__ = [
    "BENCHMARK_SCHEMA_VERSION",
    "BenchmarkCase",
    "BenchmarkMetrics",
    "BenchmarkResult",
    "BenchmarkStatus",
    "BenchmarkSuite",
    "BASELINE_ENGLISH_SUITE",
    "benchmark_result_from_dict",
    "benchmark_result_to_dict",
    "load_benchmark_result",
    "save_benchmark_result",
    "run_benchmark_case",
]
