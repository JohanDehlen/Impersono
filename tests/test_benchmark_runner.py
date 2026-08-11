from __future__ import annotations

from pathlib import Path

from impersono.core.benchmark import BenchmarkCase, BenchmarkStatus, run_benchmark_case
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
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.requests: list[GenerationRequest] = []

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
        return None

    def unload_model(self) -> None:
        return None

    def generate(self, request: GenerationRequest, progress=None) -> GenerationResult:
        self.requests.append(request)
        if self.fail:
            raise RuntimeError("simulated generation failure")
        return GenerationResult(
            audio_path=request.output_path,
            engine_id="fake",
            model_id="fake/model",
            duration_seconds=2.75,
        )

    def cancel(self) -> None:
        return None


class FakeClock:
    def __init__(self, values: list[float]) -> None:
        self._values = iter(values)

    def __call__(self) -> float:
        return next(self._values)


def test_runner_records_successful_generation_measurements(tmp_path: Path) -> None:
    engine = FakeEngine()
    case = BenchmarkCase(
        case_id="short-en-001",
        text="Hello from Impersono.",
        reference_voice=Path("voices/alice.wav"),
    )

    result = run_benchmark_case(
        engine,
        case,
        model_id="fake/model",
        output_dir=tmp_path,
        options={"cfg_scale": 1.3},
        run_id="run-001",
        metadata={"device": "cpu"},
        clock=FakeClock([10.0, 12.5]),
    )

    assert result.status is BenchmarkStatus.SUCCEEDED
    assert result.engine_id == "fake"
    assert result.model_id == "fake/model"
    assert result.output_path == tmp_path / "short-en-001.wav"
    assert result.metrics.generation_seconds == 2.5
    assert result.metrics.audio_duration_seconds == 2.75
    assert result.run_id == "run-001"
    assert result.metadata == {"device": "cpu"}

    request = engine.requests[0]
    assert request.text == "Hello from Impersono."
    assert request.voice_reference == Path("voices/alice.wav")
    assert request.output_path == tmp_path / "short-en-001.wav"
    assert request.options == {"cfg_scale": 1.3}


def test_runner_records_generation_failure_instead_of_raising(tmp_path: Path) -> None:
    engine = FakeEngine(fail=True)
    case = BenchmarkCase(case_id="failure-001", text="Hello")

    result = run_benchmark_case(
        engine,
        case,
        model_id="fake/model",
        output_dir=tmp_path,
        clock=FakeClock([5.0, 5.75]),
    )

    assert result.status is BenchmarkStatus.FAILED
    assert result.output_path is None
    assert result.metrics.generation_seconds == 0.75
    assert result.metrics.audio_duration_seconds is None
    assert result.error_message == "RuntimeError: simulated generation failure"


def test_runner_does_not_load_or_unload_engine(tmp_path: Path) -> None:
    class LifecycleEngine(FakeEngine):
        def __init__(self) -> None:
            super().__init__()
            self.load_calls = 0
            self.unload_calls = 0

        def load_model(self, model_id: str) -> None:
            self.load_calls += 1

        def unload_model(self) -> None:
            self.unload_calls += 1

    engine = LifecycleEngine()

    run_benchmark_case(
        engine,
        BenchmarkCase(case_id="case", text="Hello"),
        model_id="fake/model",
        output_dir=tmp_path,
        clock=FakeClock([1.0, 2.0]),
    )

    assert engine.load_calls == 0
    assert engine.unload_calls == 0


def test_runner_rejects_empty_model_id(tmp_path: Path) -> None:
    engine = FakeEngine()

    try:
        run_benchmark_case(
            engine,
            BenchmarkCase(case_id="case", text="Hello"),
            model_id=" ",
            output_dir=tmp_path,
        )
    except ValueError as exc:
        assert "model_id" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty model_id")
