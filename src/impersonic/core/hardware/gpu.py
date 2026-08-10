"""Graphics-adapter discovery with Windows-first standard-library support."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

from .models import GpuInfo


def _vendor_from_gpu(name: str, pnp_device_id: str) -> str:
    text = f"{name} {pnp_device_id}".lower()

    if "ven_10de" in text or "nvidia" in text:
        return "NVIDIA"
    if "ven_1002" in text or "amd" in text or "radeon" in text:
        return "AMD"
    if "ven_8086" in text or "intel" in text:
        return "Intel"
    if "qualcomm" in text:
        return "Qualcomm"
    return "Unknown"


def _safe_vram(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None

    return number if number > 0 else None


def _normalise_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    return []


def _detect_windows_gpus() -> tuple[GpuInfo, ...]:
    command = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        (
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,AdapterRAM,PNPDeviceID | "
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
        return ()

    if completed.returncode != 0 or not completed.stdout.strip():
        return ()

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return ()

    gpus: list[GpuInfo] = []
    for row in _normalise_rows(payload):
        name = str(row.get("Name") or "Unknown GPU").strip()
        pnp_device_id = str(row.get("PNPDeviceID") or "").strip()

        gpus.append(
            GpuInfo(
                name=name,
                vendor=_vendor_from_gpu(name, pnp_device_id),
                dedicated_vram_bytes=_safe_vram(row.get("AdapterRAM")),
            )
        )

    return tuple(gpus)


def detect_gpus() -> tuple[GpuInfo, ...]:
    """Return graphics adapters without assuming any particular AI backend."""

    if os.name == "nt":
        return _detect_windows_gpus()

    return ()


def detect_cuda_driver() -> bool:
    """Return whether an NVIDIA CUDA-capable driver tool is reachable.

    This does not claim that Impersonic's future Python inference stack can use
    CUDA; it only reports whether the NVIDIA driver utility is available.
    """

    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return False

    try:
        completed = subprocess.run(
            [nvidia_smi, "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False

    return completed.returncode == 0 and bool(completed.stdout.strip())
