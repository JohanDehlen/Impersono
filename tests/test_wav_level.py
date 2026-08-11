from __future__ import annotations

import math
import wave
from pathlib import Path

from impersono.core.audio.wav_level import inspect_wav_level, normalize_wav_rms


def write_test_wav(path: Path, amplitude: float, frames: int = 24000) -> None:
    import array

    samples = array.array(
        "h",
        (
            int(32767 * amplitude * math.sin(2 * math.pi * 440 * i / 24000))
            for i in range(frames)
        ),
    )
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(samples.tobytes())


def test_inspect_wav_level_reports_expected_values(tmp_path: Path) -> None:
    path = tmp_path / "tone.wav"
    write_test_wav(path, 0.1)

    level = inspect_wav_level(path)

    assert -20.2 < level.peak_dbfs < -19.8
    assert -23.3 < level.rms_dbfs < -22.8


def test_normalize_wav_rms_reaches_fixed_target(tmp_path: Path) -> None:
    path = tmp_path / "tone.wav"
    write_test_wav(path, 0.05)

    level = normalize_wav_rms(
        path,
        target_rms_dbfs=-16.0,
        peak_ceiling_dbfs=-1.0,
    )

    assert -16.2 < level.rms_dbfs < -15.8
    assert level.peak_dbfs <= -0.95


def test_normalize_wav_rms_respects_peak_ceiling(tmp_path: Path) -> None:
    path = tmp_path / "tone.wav"
    write_test_wav(path, 0.8)

    level = normalize_wav_rms(
        path,
        target_rms_dbfs=-10.0,
        peak_ceiling_dbfs=-1.0,
    )

    assert level.peak_dbfs <= -0.95
