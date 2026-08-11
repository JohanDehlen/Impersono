import pytest

from impersono.core.benchmark import (
    BASELINE_ENGLISH_SUITE,
    BenchmarkCase,
    BenchmarkSuite,
)


def test_baseline_suite_has_stable_identity() -> None:
    assert BASELINE_ENGLISH_SUITE.suite_id == "baseline-en-v1"
    assert BASELINE_ENGLISH_SUITE.display_name == "Impersono English Baseline v1"


def test_baseline_suite_contains_expected_case_ids() -> None:
    assert BASELINE_ENGLISH_SUITE.case_ids() == (
        "short-neutral-001",
        "punctuation-001",
        "numbers-001",
        "names-001",
        "pacing-001",
        "longer-001",
    )


def test_baseline_suite_covers_core_benchmark_categories() -> None:
    tags = {
        tag
        for case in BASELINE_ENGLISH_SUITE.cases
        for tag in case.tags
    }

    assert {
        "clarity",
        "punctuation",
        "numbers",
        "pronunciation",
        "pacing",
        "prosody",
        "consistency",
        "naturalness",
    }.issubset(tags)


def test_suite_rejects_duplicate_case_ids() -> None:
    duplicate_a = BenchmarkCase(case_id="duplicate", text="First.")
    duplicate_b = BenchmarkCase(case_id="duplicate", text="Second.")

    with pytest.raises(ValueError, match="unique"):
        BenchmarkSuite(
            suite_id="duplicates",
            display_name="Duplicate Test",
            cases=(duplicate_a, duplicate_b),
        )


def test_suite_rejects_empty_case_collection() -> None:
    with pytest.raises(ValueError, match="at least one"):
        BenchmarkSuite(
            suite_id="empty",
            display_name="Empty",
            cases=(),
        )


def test_suite_get_case_returns_case_by_stable_id() -> None:
    case = BASELINE_ENGLISH_SUITE.get_case("numbers-001")

    assert case.language == "en"
    assert "numbers" in case.tags


def test_suite_get_case_rejects_unknown_id() -> None:
    with pytest.raises(KeyError, match="Unknown benchmark case_id"):
        BASELINE_ENGLISH_SUITE.get_case("missing")
