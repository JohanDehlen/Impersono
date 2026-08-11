"""Concrete voice-engine backends for Impersono."""

from .vibevoice import (
    VibeVoiceConfig,
    VibeVoiceDependencyStatus,
    VibeVoiceEngine,
    VibeVoiceRuntime,
    VibeVoiceRuntimeLoader,
    detect_vibevoice_dependencies,
)
from .vibevoice_runtime import NativeVibeVoiceRuntime, NativeVibeVoiceRuntimeLoader

__all__ = [
    "NativeVibeVoiceRuntime",
    "NativeVibeVoiceRuntimeLoader",
    "VibeVoiceConfig",
    "VibeVoiceDependencyStatus",
    "VibeVoiceEngine",
    "VibeVoiceRuntime",
    "VibeVoiceRuntimeLoader",
    "detect_vibevoice_dependencies",
]
