from datetime import datetime, timezone
from pathlib import Path

import pytest

from impersono.core.benchmark.local_vibevoice import (
    DEFAULT_BENCHMARK_SEED,
    build_parser,
    build_run_id,
    conditioned_suite,
    limit_suite,
)


def test_conditioned_suite_applies_reference_to_every_case() -> None:
    reference = Path("voices/reference.wav")

    suite = conditioned_suite(reference)

    assert len(suite.cases) == 6
    assert all(case.reference_voice == reference for case in suite.cases)
    assert suite.suite_id == "baseline-en-v1"


def test_limit_suite_preserves_stable_case_order() -> None:
    suite = conditioned_suite(Path("voice.wav"))

    limited = limit_suite(suite, 2)

    assert limited.case_ids() == (
        "short-neutral-001",
        "punctuation-001",
    )


def test_limit_suite_rejects_zero_cases() -> None:
    suite = conditioned_suite(Path("voice.wav"))

    with pytest.raises(ValueError, match="at least 1"):
        limit_suite(suite, 0)


def test_build_run_id_is_stable_for_supplied_utc_time() -> None:
    timestamp = datetime(2026, 8, 11, 10, 15, 30, tzinfo=timezone.utc)

    assert build_run_id(timestamp) == "vibevoice-cpu-20260811T101530Z"

def test_local_benchmark_parser_uses_fixed_seed_by_default() -> None:
    args = build_parser().parse_args([])

    assert DEFAULT_BENCHMARK_SEED == 12345
    assert args.seed == 12345
