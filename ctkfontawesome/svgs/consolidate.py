"""Backward-compatible wrapper around the development data generator."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from development.fontawesome_generator import regenerate_from_package


def main():
    package_root = Path(__file__).parent
    output_path = ROOT / "ctkfontawesome" / "svgs.py"
    icon_count, alias_count, category_count = regenerate_from_package(package_root, output_path)
    print(
        f"Wrote {output_path} with {icon_count} icons, {alias_count} aliases, "
        f"and {category_count} categorized icons."
    )


if __name__ == "__main__":
    main()
