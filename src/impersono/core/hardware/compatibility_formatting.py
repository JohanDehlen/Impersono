"""User-facing formatting for model compatibility guidance."""

from __future__ import annotations

from .compatibility import CompatibilityStatus, ModelCompatibility


def _status_label(status: CompatibilityStatus) -> str:
    labels = {
        CompatibilityStatus.KNOWN_PATH: "Known execution path",
        CompatibilityStatus.CANDIDATE: "Candidate - verification required",
        CompatibilityStatus.UNCONFIRMED: "Unconfirmed",
        CompatibilityStatus.NOT_AVAILABLE: "Not available",
    }
    return labels[status]


def format_model_compatibility(assessment: ModelCompatibility) -> str:
    """Return readable, conservative model compatibility guidance."""

    lines = [
        f"{assessment.display_name} Compatibility",
        "",
        f"Model: {assessment.model_id}",
        f"Model files: approximately {assessment.model_storage_gb:.2f} GB",
        f"Weight precision: {assessment.weight_dtype}",
        "",
        f"CPU path: {_status_label(assessment.cpu_status)}",
        f"GPU path: {_status_label(assessment.gpu_status)}",
        f"GPU note: {assessment.gpu_reason}",
        "",
        (
            "Note: model file size is not a RAM or VRAM requirement. Runtime "
            "memory usage must be measured separately before Impersono makes "
            "a model-fit recommendation."
        ),
    ]
    return "\n".join(lines)
