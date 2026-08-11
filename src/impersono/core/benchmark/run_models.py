"""Run-level records for groups of Impersono benchmark results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping

from .models import BenchmarkResult, BenchmarkStatus


@dataclass(frozen=True, slots=True)
class BenchmarkRun:
    """One identifiable execution of a benchmark suite."""

    run_id: str
    suite_id: str
    engine_id: str
    model_id: str
    started_at: datetime
    results: tuple[BenchmarkResult, ...]
    configuration: Mapping[str, object] = field(default_factory=dict)
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, value in (
            ("run_id", self.run_id),
            ("suite_id", self.suite_id),
            ("engine_id", self.engine_id),
            ("model_id", self.model_id),
        ):
            if not value.strip():
                raise ValueError(f"Benchmark {name} must not be empty.")

        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("Benchmark started_at must be timezone-aware.")

        case_ids = [result.case.case_id for result in self.results]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("Benchmark run case IDs must be unique.")

        for result in self.results:
            if result.run_id != self.run_id:
                raise ValueError(
                    "Benchmark result run_id must match the containing run."
                )
            if result.engine_id != self.engine_id:
                raise ValueError(
                    "Benchmark result engine_id must match the containing run."
                )
            if result.model_id != self.model_id:
                raise ValueError(
                    "Benchmark result model_id must match the containing run."
                )

    @property
    def succeeded_count(self) -> int:
        return sum(
            result.status is BenchmarkStatus.SUCCEEDED for result in self.results
        )

    @property
    def failed_count(self) -> int:
        return sum(
            result.status is BenchmarkStatus.FAILED for result in self.results
        )

    @property
    def total_count(self) -> int:
        return len(self.results)

    @classmethod
    def empty(
        cls,
        *,
        run_id: str,
        suite_id: str,
        engine_id: str,
        model_id: str,
        configuration: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        started_at: datetime | None = None,
    ) -> "BenchmarkRun":
        return cls(
            run_id=run_id,
            suite_id=suite_id,
            engine_id=engine_id,
            model_id=model_id,
            started_at=started_at or datetime.now(timezone.utc),
            results=(),
            configuration=dict(configuration or {}),
            metadata=dict(metadata or {}),
        )
