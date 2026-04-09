"""Smoke-test a generated Font Awesome data module before checking it in."""

# Author: Clive Bostock
# Date: 2026-04-09
# Description: Validate the structure and basic contents of a generated Font Awesome data module.

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULE_PATH = REPO_ROOT / "ctkfontawesome" / "svgs.py"


def load_module(module_path: Path) -> ModuleType:
    """Load a generated Python module from a file path.

    Args:
        module_path: Path to the Python module to inspect.

    Returns:
        ModuleType: Imported module object.

    Raises:
        ImportError: If the module cannot be loaded from the supplied path.
    """
    spec = importlib.util.spec_from_file_location("ctkfontawesome_generated_svgs", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_generated_module(
    module: ModuleType,
    *,
    expected_icon: str,
    minimum_icons: int,
) -> tuple[int, int, int]:
    """Validate the basic structure of a generated Font Awesome data module.

    Args:
        module: Imported generated module.
        expected_icon: Icon name expected to exist in the generated data.
        minimum_icons: Minimum acceptable number of bundled icons.

    Returns:
        tuple[int, int, int]: Counts of icons, aliases, and categorised icons.

    Raises:
        ValueError: If required attributes or basic invariants are missing.
    """
    fa = getattr(module, "FA", None)
    fa_aliases = getattr(module, "FA_aliases", None)
    fa_categories = getattr(module, "FA_categories", None)

    if not isinstance(fa, dict):
        raise ValueError("Generated module is missing a valid FA dictionary.")
    if not isinstance(fa_aliases, dict):
        raise ValueError("Generated module is missing a valid FA_aliases dictionary.")
    if not isinstance(fa_categories, dict):
        raise ValueError("Generated module is missing a valid FA_categories dictionary.")

    if len(fa) < minimum_icons:
        raise ValueError(f"Expected at least {minimum_icons} icons, found {len(fa)}.")
    if expected_icon not in fa:
        raise ValueError(f"Expected icon {expected_icon!r} was not found in FA.")

    svg_value = fa[expected_icon]
    if not isinstance(svg_value, str) or not svg_value.startswith("<svg "):
        raise ValueError(f"Expected {expected_icon!r} to map to an SVG string.")

    return len(fa), len(fa_aliases), len(fa_categories)


def compare_modules(candidate_module: ModuleType, baseline_module: ModuleType) -> tuple[int, int, int]:
    """Return count deltas between a candidate module and a baseline module.

    Args:
        candidate_module: Newly generated module to inspect.
        baseline_module: Existing checked-in module for comparison.

    Returns:
        tuple[int, int, int]: Deltas for icons, aliases, and categorised icons.
    """
    return (
        len(candidate_module.FA) - len(baseline_module.FA),
        len(candidate_module.FA_aliases) - len(baseline_module.FA_aliases),
        len(candidate_module.FA_categories) - len(baseline_module.FA_categories),
    )


def main() -> None:
    """Run the smoke test as a command-line tool."""
    parser = argparse.ArgumentParser(
        description="Validate a generated Font Awesome data module and optionally compare it to the current one."
    )
    parser.add_argument(
        "module_path",
        nargs="?",
        default=DEFAULT_MODULE_PATH,
        type=Path,
        help="Generated svgs.py file to validate",
    )
    parser.add_argument(
        "--compare-to",
        default=DEFAULT_MODULE_PATH,
        type=Path,
        help="Baseline svgs.py file to compare counts against",
    )
    parser.add_argument(
        "--expected-icon",
        default="facebook",
        help="Known icon name expected to exist in the generated data",
    )
    parser.add_argument(
        "--minimum-icons",
        default=1000,
        type=int,
        help="Minimum acceptable number of bundled icons",
    )
    args = parser.parse_args()

    candidate_module = load_module(args.module_path)
    icon_count, alias_count, category_count = validate_generated_module(
        candidate_module,
        expected_icon=args.expected_icon,
        minimum_icons=args.minimum_icons,
    )
    print(
        f"Validated {args.module_path}: {icon_count} icons, {alias_count} aliases, "
        f"{category_count} categorised icons."
    )

    if args.compare_to.resolve() != args.module_path.resolve():
        baseline_module = load_module(args.compare_to)
        icon_delta, alias_delta, category_delta = compare_modules(candidate_module, baseline_module)
        print(
            f"Delta vs {args.compare_to}: "
            f"icons {icon_delta:+d}, aliases {alias_delta:+d}, categorised icons {category_delta:+d}."
        )


if __name__ == "__main__":
    main()
