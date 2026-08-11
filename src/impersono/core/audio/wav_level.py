"""Engine-independent WAV output utilities."""

from __future__ import annotations

import math
import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WavLevel:
    peak_dbfs: float
    rms_dbfs: float


def _dbfs(value: float) -> float:
    if value <= 0:
        return float("-inf")
    return 20.0 * math.log10(value)


def inspect_wav_level(path: Path) -> WavLevel:
    """Measure peak and RMS level for 16-bit PCM WAV audio."""

    import array

    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        raw = wav.readframes(wav.getnframes())

    if channels < 1:
        raise ValueError("WAV file has no audio channels.")
    if sample_width != 2:
        raise ValueError("Only 16-bit PCM WAV normalization is currently supported.")

    samples = array.array("h")
    samples.frombytes(raw)
    if not samples:
        return WavLevel(float("-inf"), float("-inf"))

    scale = 32768.0
    peak = max(abs(sample) for sample in samples) / scale
    rms = math.sqrt(
        sum((sample / scale) ** 2 for sample in samples) / len(samples)
    )
    return WavLevel(_dbfs(peak), _dbfs(rms))


def normalize_wav_rms(
    path: Path,
    *,
    target_rms_dbfs: float = -16.0,
    peak_ceiling_dbfs: float = -1.0,
) -> WavLevel:
    """Normalize a 16-bit PCM WAV to fixed RMS with a peak ceiling."""

    import array

    if target_rms_dbfs >= peak_ceiling_dbfs:
        raise ValueError("RMS target must remain below the peak ceiling.")

    with wave.open(str(path), "rb") as wav:
        params = wav.getparams()
        sample_width = wav.getsampwidth()
        raw = wav.readframes(wav.getnframes())

    if sample_width != 2:
        raise ValueError("Only 16-bit PCM WAV normalization is currently supported.")

    samples = array.array("h")
    samples.frombytes(raw)
    if not samples:
        return inspect_wav_level(path)

    scale = 32768.0
    peak = max(abs(sample) for sample in samples) / scale
    rms = math.sqrt(
        sum((sample / scale) ** 2 for sample in samples) / len(samples)
    )
    if rms <= 0:
        return inspect_wav_level(path)

    target_rms = 10 ** (target_rms_dbfs / 20.0)
    peak_ceiling = 10 ** (peak_ceiling_dbfs / 20.0)

    gain = target_rms / rms
    if peak > 0:
        gain = min(gain, peak_ceiling / peak)

    normalized = array.array(
        "h",
        (
            max(-32768, min(32767, int(round(sample * gain))))
            for sample in samples
        ),
    )

    temp = path.with_suffix(".normalizing.wav")
    with wave.open(str(temp), "wb") as wav:
        wav.setparams(params)
        wav.writeframes(normalized.tobytes())

    temp.replace(path)
    return inspect_wav_level(path)
