#!/usr/bin/env python3
"""Dependency installation script.

Supports pip installation.

[INPUT]: None
[OUTPUT]: Install dependencies required by awiki-did
[POS]: Project root, provides pip installation

[PROTOCOL]:
1. Update this header when logic changes
2. Check the folder's CLAUDE.md after updating
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> bool:
    """Run a command."""
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        return False


def find_installer() -> tuple[str, list[str]]:
    """Find an available package installer."""
    script_dir = Path(__file__).parent
    requirements = str(script_dir / "requirements.txt")

    # Prefer pip
    if shutil.which("pip"):
        return "pip", ["pip", "install", "-r", requirements]

    # Try python -m pip
    return "python-pip", [
        sys.executable, "-m", "pip", "install", "-r", requirements,
    ]


def main() -> int:
    """Main function."""
    print("=" * 50)
    print("awiki-did Skill Dependency Installation")
    print("=" * 50)

    installer_name, cmd = find_installer()
    print(f"\nUsing {installer_name} to install dependencies...")
    print(f"Running: {' '.join(cmd)}\n")

    if run_command(cmd):
        print("\nDependencies installed successfully!")
        print("\nReady to use:")
        print("  python scripts/setup_identity.py --name MyAgent")
        return 0
    else:
        print("\nDependency installation failed. Please install manually:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
