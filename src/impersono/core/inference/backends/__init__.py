"""Concrete voice-engine backends for Impersono."""

from .vibevoice import (
    VibeVoiceConfig,
    VibeVoiceDependencyStatus,
    VibeVoiceEngine,
    VibeVoiceRuntime,
    VibeVoiceRuntimeLoader,
    detect_vibevoice_dependencies,
)

__all__ = [
    "VibeVoiceConfig",
    "VibeVoiceDependencyStatus",
    "VibeVoiceEngine",
    "VibeVoiceRuntime",
    "VibeVoiceRuntimeLoader",
    "detect_vibevoice_dependencies",
]
