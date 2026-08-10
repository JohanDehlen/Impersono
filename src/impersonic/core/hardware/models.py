"""Data models used by hardware discovery."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GpuInfo:
    """Raw facts about one graphics adapter."""

    name: str
    vendor: str
    dedicated_vram_bytes: int | None


@dataclass(frozen=True, slots=True)
class HardwareInfo:
    """Raw hardware facts collected from the local computer."""

    operating_system: str
    operating_system_version: str
    machine_architecture: str
    python_version: str
    cpu_model: str
    logical_cpu_count: int | None
    total_ram_bytes: int | None
    gpus: tuple[GpuInfo, ...] = ()
    cuda_driver_available: bool = False
