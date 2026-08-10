"""Local hardware detection with standard-library-only fallbacks."""

from __future__ import annotations

import ctypes
import os
import platform

from .cpu import detect_cpu_model
from .gpu import detect_cuda_driver, detect_gpus
from .models import HardwareInfo


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def _detect_total_ram_bytes() -> int | None:
    """Return total physical RAM when the platform exposes it safely."""

    if os.name == "nt":
        status = _MemoryStatusEx()
        status.dwLength = ctypes.sizeof(_MemoryStatusEx)

        try:
            success = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        except (AttributeError, OSError):
            return None

        return int(status.ullTotalPhys) if success else None

    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        physical_pages = os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        return None

    if not isinstance(page_size, int) or not isinstance(physical_pages, int):
        return None

    if page_size <= 0 or physical_pages <= 0:
        return None

    return page_size * physical_pages


def detect_hardware() -> HardwareInfo:
    """Collect stable local hardware facts without model-specific assumptions."""

    return HardwareInfo(
        operating_system=platform.system() or "Unknown",
        operating_system_version=platform.version() or "Unknown",
        machine_architecture=platform.machine() or "Unknown",
        python_version=platform.python_version(),
        cpu_model=detect_cpu_model(),
        logical_cpu_count=os.cpu_count(),
        total_ram_bytes=_detect_total_ram_bytes(),
        gpus=detect_gpus(),
        cuda_driver_available=detect_cuda_driver(),
    )
