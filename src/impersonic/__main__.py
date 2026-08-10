from __future__ import annotations

import platform
import sys

from impersonic import __app_name__, __version__


def main() -> None:
    print(f"{__app_name__} {__version__}")
    print("Professional Local AI Voice Creation")
    print()
    print(f"Python: {platform.python_version()}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")


if __name__ == "__main__":
    main()