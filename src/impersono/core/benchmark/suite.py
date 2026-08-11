"""Stable benchmark case collections for Impersono quality testing."""

from __future__ import annotations

from dataclasses import dataclass

from .models import BenchmarkCase


@dataclass(frozen=True, slots=True)
class BenchmarkSuite:
    """Named collection of repeatable benchmark cases."""

    suite_id: str
    display_name: str
    cases: tuple[BenchmarkCase, ...]

    def __post_init__(self) -> None:
        if not self.suite_id.strip():
            raise ValueError("Benchmark suite_id must not be empty.")
        if not self.display_name.strip():
            raise ValueError("Benchmark display_name must not be empty.")
        if not self.cases:
            raise ValueError("Benchmark suites must contain at least one case.")

        case_ids = [case.case_id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("Benchmark case IDs must be unique within a suite.")

    def case_ids(self) -> tuple[str, ...]:
        return tuple(case.case_id for case in self.cases)

    def get_case(self, case_id: str) -> BenchmarkCase:
        for case in self.cases:
            if case.case_id == case_id:
                return case
        raise KeyError(f"Unknown benchmark case_id: {case_id}")


BASELINE_ENGLISH_SUITE = BenchmarkSuite(
    suite_id="baseline-en-v1",
    display_name="Impersono English Baseline v1",
    cases=(
        BenchmarkCase(
            case_id="short-neutral-001",
            text="The small lantern glowed beside the quiet window.",
            language="en",
            notes="Short neutral sentence for basic clarity and naturalness.",
            tags=("short", "neutral", "clarity"),
        ),
        BenchmarkCase(
            case_id="punctuation-001",
            text=(
                "Wait—did you hear that? No, not the clock; "
                "the sound came from upstairs."
            ),
            language="en",
            notes="Tests pauses, question intonation, dash handling, and semicolon pacing.",
            tags=("punctuation", "prosody", "pacing"),
        ),
        BenchmarkCase(
            case_id="numbers-001",
            text=(
                "The invoice total is 1,247 dollars and 35 cents, "
                "due on October 14, 2026."
            ),
            language="en",
            notes="Tests numbers, currency, and date pronunciation.",
            tags=("numbers", "dates", "pronunciation"),
        ),
        BenchmarkCase(
            case_id="names-001",
            text=(
                "Amelia met Joaquin, Siobhan, and Nguyen near the museum "
                "before their evening reservation."
            ),
            language="en",
            notes="Tests a small set of potentially difficult proper names.",
            tags=("names", "pronunciation"),
        ),
        BenchmarkCase(
            case_id="pacing-001",
            text=(
                "At first, the room was silent. Then a chair moved. "
                "A moment later, someone laughed softly in the hallway."
            ),
            language="en",
            notes="Tests sentence-to-sentence pacing and short dramatic pauses.",
            tags=("pacing", "prosody"),
        ),
        BenchmarkCase(
            case_id="longer-001",
            text=(
                "By the time the train reached the coast, the morning fog had "
                "lifted from the fields and the sea was visible beyond the old "
                "stone houses. Passengers who had spent most of the journey "
                "reading began to look up, gather their bags, and watch the "
                "bright line of water grow wider through the windows."
            ),
            language="en",
            notes="Longer paragraph for consistency, pacing, and sustained naturalness.",
            tags=("longer", "consistency", "pacing", "naturalness"),
        ),
    ),
)
