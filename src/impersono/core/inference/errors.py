"""Engine-independent inference errors."""


class EngineError(RuntimeError):
    """Base error for failures crossing the voice-engine boundary."""


class EngineNotReadyError(EngineError):
    """Raised when generation is requested before an engine is ready."""


class ModelLoadError(EngineError):
    """Raised when an engine cannot load the requested model."""


class GenerationCancelledError(EngineError):
    """Raised when an in-progress generation is cancelled."""
