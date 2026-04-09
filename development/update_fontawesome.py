"""Install Font Awesome package assets and regenerate bundled metadata."""

# Author: Clive Bostock
# Date: 2026-04-09
# Description: Install the free Font Awesome package and regenerate bundled metadata.

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from development.fontawesome_generator import regenerate_from_package


DEFAULT_PACKAGE_NAME = "@fortawesome/fontawesome-free"
OUTPUT_PATH = ROOT / "ctkfontawesome" / "svgs.py"


def install_package(target_dir, package_name):
    """Install the requested npm package into a temporary working directory.

    Args:
        target_dir: Directory used as the npm working directory.
        package_name: npm package name to install.
    """
    subprocess.run(
        [
            "npm",
            "install",
            "--no-package-lock",
            "--no-save",
            package_name,
        ],
        cwd=target_dir,
        check=True,
    )


def main():
    """Run the maintainer update workflow from the command line."""
    parser = argparse.ArgumentParser(
        description="Install Font Awesome assets with npm and regenerate bundled metadata."
    )
    parser.add_argument(
        "--package-name",
        default=DEFAULT_PACKAGE_NAME,
        help="npm package to install before regenerating metadata; only the free package is accepted",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_PATH,
        type=Path,
        help="Generated Python module to update",
    )
    args = parser.parse_args()

    if args.package_name != DEFAULT_PACKAGE_NAME:
        raise ValueError(
            f"This updater only supports {DEFAULT_PACKAGE_NAME!r}, got {args.package_name!r}."
        )

    with tempfile.TemporaryDirectory(prefix="ctkfontawesome-fa-") as temp_dir:
        temp_path = Path(temp_dir)
        install_package(temp_path, args.package_name)
        package_root = temp_path / "node_modules" / "@fortawesome" / "fontawesome-free"
        icon_count, alias_count, category_count = regenerate_from_package(package_root, args.output)
        print(
            f"Updated {args.output} with {icon_count} icons, {alias_count} aliases, "
            f"and {category_count} categorized icons from {args.package_name}."
        )


if __name__ == "__main__":
    main()
