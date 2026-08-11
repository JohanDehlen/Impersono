"""Engine-independent benchmark data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Mapping


class BenchmarkStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    case_id: str
    text: str
    reference_voice: Path | None = None
    language: str | None = None
    notes: str | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("Benchmark case_id must not be empty.")
        if not self.text.strip():
            raise ValueError("Benchmark text must not be empty.")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("Benchmark tags must not contain empty values.")


@dataclass(frozen=True, slots=True)
class BenchmarkMetrics:
    generation_seconds: float | None = None
    audio_duration_seconds: float | None = None
    peak_memory_mb: float | None = None
    peak_vram_mb: float | None = None
    quality_scores: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, value in (
            ("generation_seconds", self.generation_seconds),
            ("audio_duration_seconds", self.audio_duration_seconds),
            ("peak_memory_mb", self.peak_memory_mb),
            ("peak_vram_mb", self.peak_vram_mb),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} must not be negative.")

        for name, score in self.quality_scores.items():
            if not name.strip():
                raise ValueError("Quality-score names must not be empty.")
            if not isinstance(score, (int, float)):
                raise TypeError("Quality scores must be numeric.")


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    case: BenchmarkCase
    status: BenchmarkStatus
    engine_id: str
    model_id: str
    output_path: Path | None = None
    metrics: BenchmarkMetrics = field(default_factory=BenchmarkMetrics)
    error_message: str | None = None
    run_id: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.engine_id.strip():
            raise ValueError("Benchmark engine_id must not be empty.")
        if not self.model_id.strip():
            raise ValueError("Benchmark model_id must not be empty.")

        if self.status is BenchmarkStatus.SUCCEEDED:
            if self.output_path is None:
                raise ValueError("Successful benchmark results require an output_path.")
            if self.error_message is not None:
                raise ValueError(
                    "Successful benchmark results must not contain an error_message."
                )

        if self.status is BenchmarkStatus.FAILED:
            if self.error_message is None or not self.error_message.strip():
                raise ValueError(
                    "Failed benchmark results require a non-empty error_message."
                )
