from __future__ import annotations

import argparse
import platform
import sys
from collections.abc import Sequence

from impersonic import __app_name__, __version__
from impersonic.core.hardware import detect_hardware, format_hardware_report
from impersonic.core.hardware.compatibility import assess_vibevoice_1_5b
from impersonic.core.hardware.compatibility_formatting import (
    format_model_compatibility,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m impersonic",
        description="Impersonic development command-line interface.",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--hardware",
        action="store_true",
        help="Show detected local hardware.",
    )
    group.add_argument(
        "--compatibility",
        action="store_true",
        help="Show VibeVoice 1.5B compatibility guidance for this computer.",
    )

    return parser


def _print_identity() -> None:
    print(f"{__app_name__} {__version__}")
    print("Professional Local AI Voice Creation")
    print()
    print(f"Python: {platform.python_version()}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.hardware:
        print(format_hardware_report(detect_hardware()))
        return 0

    if args.compatibility:
        hardware = detect_hardware()
        assessment = assess_vibevoice_1_5b(hardware)
        print(format_model_compatibility(assessment))
        return 0

    _print_identity()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
