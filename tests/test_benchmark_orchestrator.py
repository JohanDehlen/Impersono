from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from impersono.core.benchmark import (
    BenchmarkCase,
    BenchmarkStatus,
    BenchmarkSuite,
    run_benchmark_suite,
)
from impersono.core.inference import (
    EngineCapabilities,
    EngineIdentity,
    EngineModel,
    EngineState,
    EngineStatus,
    GenerationRequest,
    GenerationResult,
    VoiceEngine,
)


class FakeEngine(VoiceEngine):
    def __init__(self, *, fail_case_text: str | None = None) -> None:
        self.fail_case_text = fail_case_text
        self.requests: list[GenerationRequest] = []
        self.load_calls = 0
        self.unload_calls = 0

    @property
    def identity(self) -> EngineIdentity:
        return EngineIdentity("fake", "Fake Engine", "test")

    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_voice_conditioning=True,
            supports_cancellation=False,
            supports_progress=False,
        )

    @property
    def status(self) -> EngineStatus:
        return EngineStatus(EngineState.READY, loaded_model_id="fake/model")

    def list_models(self) -> tuple[EngineModel, ...]:
        return ()

    def load_model(self, model_id: str) -> None:
        self.load_calls += 1

    def unload_model(self) -> None:
        self.unload_calls += 1

    def generate(self, request: GenerationRequest, progress=None) -> GenerationResult:
        self.requests.append(request)
        if request.text == self.fail_case_text:
            raise RuntimeError("simulated case failure")
        return GenerationResult(
            audio_path=request.output_path,
            engine_id="fake",
            model_id="fake/model",
            duration_seconds=2.0,
        )

    def cancel(self) -> None:
        return None


class FakeClock:
    def __init__(self, values: list[float]) -> None:
        self._values = iter(values)

    def __call__(self) -> float:
        return next(self._values)


SUITE = BenchmarkSuite(
    suite_id="test-suite-v1",
    display_name="Test Suite",
    cases=(
        BenchmarkCase(case_id="case-001", text="First."),
        BenchmarkCase(case_id="case-002", text="Second."),
        BenchmarkCase(case_id="case-003", text="Third."),
    ),
)


def fixed_started_at() -> datetime:
    return datetime(2026, 8, 11, 10, 0, tzinfo=timezone.utc)


def test_suite_runner_executes_cases_in_stable_order(tmp_path: Path) -> None:
    engine = FakeEngine()

    run = run_benchmark_suite(
        engine,
        SUITE,
        run_id="run-001",
        model_id="fake/model",
        output_dir=tmp_path,
        options={"cfg_scale": 1.3},
        configuration={"device": "cpu"},
        metadata={"machine": "test"},
        clock=FakeClock([0.0, 1.0, 1.0, 3.0, 3.0, 6.0]),
        started_at_factory=fixed_started_at,
    )

    assert [request.text for request in engine.requests] == [
        "First.",
        "Second.",
        "Third.",
    ]
    assert [result.case.case_id for result in run.results] == [
        "case-001",
        "case-002",
        "case-003",
    ]
    assert [result.metrics.generation_seconds for result in run.results] == [
        1.0,
        2.0,
        3.0,
    ]
    assert run.run_id == "run-001"
    assert run.suite_id == "test-suite-v1"
    assert run.started_at == fixed_started_at()
    assert run.configuration == {"device": "cpu"}
    assert run.metadata == {"machine": "test"}
    assert run.succeeded_count == 3
    assert run.failed_count == 0


def test_suite_runner_keeps_failed_case_and_continues(tmp_path: Path) -> None:
    engine = FakeEngine(fail_case_text="Second.")

    run = run_benchmark_suite(
        engine,
        SUITE,
        run_id="run-002",
        model_id="fake/model",
        output_dir=tmp_path,
        clock=FakeClock([0.0, 1.0, 1.0, 1.5, 1.5, 3.0]),
        started_at_factory=fixed_started_at,
    )

    assert run.total_count == 3
    assert run.succeeded_count == 2
    assert run.failed_count == 1
    assert run.results[1].status is BenchmarkStatus.FAILED
    assert "simulated case failure" in run.results[1].error_message
    assert len(engine.requests) == 3


def test_suite_runner_does_not_manage_model_lifecycle(tmp_path: Path) -> None:
    engine = FakeEngine()

    run_benchmark_suite(
        engine,
        SUITE,
        run_id="run-003",
        model_id="fake/model",
        output_dir=tmp_path,
        clock=FakeClock([0, 1, 1, 2, 2, 3]),
        started_at_factory=fixed_started_at,
    )

    assert engine.load_calls == 0
    assert engine.unload_calls == 0


def test_suite_runner_assigns_same_run_id_to_every_result(tmp_path: Path) -> None:
    engine = FakeEngine()

    run = run_benchmark_suite(
        engine,
        SUITE,
        run_id="shared-run",
        model_id="fake/model",
        output_dir=tmp_path,
        clock=FakeClock([0, 1, 1, 2, 2, 3]),
        started_at_factory=fixed_started_at,
    )

    assert {result.run_id for result in run.results} == {"shared-run"}


def test_suite_runner_rejects_naive_started_at(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        run_benchmark_suite(
            FakeEngine(),
            SUITE,
            run_id="run",
            model_id="fake/model",
            output_dir=tmp_path,
            clock=FakeClock([0, 1, 1, 2, 2, 3]),
            started_at_factory=lambda: datetime(2026, 8, 11, 10, 0),
        )
