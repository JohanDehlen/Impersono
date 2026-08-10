"""CPU model discovery with Windows-first standard-library support."""

from __future__ import annotations

import json
import os
import platform
import subprocess


def _detect_windows_cpu_model() -> str | None:
    command = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        (
            "Get-CimInstance Win32_Processor | "
            "Select-Object -First 1 -ExpandProperty Name | "
            "ConvertTo-Json -Compress"
        ),
    ]

    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if completed.returncode != 0 or not completed.stdout.strip():
        return None

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, str):
        return None

    value = " ".join(payload.split())
    return value or None


def detect_cpu_model() -> str:
    """Return the most useful CPU model string available."""

    if os.name == "nt":
        detected = _detect_windows_cpu_model()
        if detected:
            return detected

    fallback = " ".join((platform.processor() or "").split())
    return fallback or "Unknown"
