"""Utilities for generating bundled Font Awesome data modules."""

# Author: Clive Bostock
# Date: 2026-04-09
# Description: Generate bundled Font Awesome SVG, alias, and category metadata.

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from pprint import pformat
from typing import Any


EXPECTED_PACKAGE_NAME = "@fortawesome/fontawesome-free"
DEFAULT_STYLES = ("brands", "regular", "solid")


def _coerce_str_list(value):
    """Return a list of string values from a loosely typed metadata field."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return [item for item in value if isinstance(item, str)]
    return []


def _extract_aliases(icon_data):
    """Extract alias names from an icon metadata record."""
    aliases = icon_data.get("aliases")
    if not isinstance(aliases, dict):
        return []
    return _coerce_str_list(aliases.get("names"))


def _extract_categories(icon_data):
    """Extract category names from an icon metadata record."""
    categories = []

    for candidate in (
        icon_data.get("categories"),
        icon_data.get("category"),
        icon_data.get("search", {}).get("categories") if isinstance(icon_data.get("search"), dict) else None,
    ):
        categories.extend(_coerce_str_list(candidate))

    return tuple(sorted(set(categories)))


def _strip_yaml_scalar(value: str) -> str:
    """Return a plain string value from a simple YAML scalar."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _load_categories_yaml(metadata_dir: Path) -> dict[str, tuple[str, ...]]:
    """Load icon-to-category mappings from Font Awesome categories.yml.

    Args:
        metadata_dir: Path to the package metadata directory.

    Returns:
        dict[str, tuple[str, ...]]: Mapping of icon names to category tuples.
    """
    categories_path = metadata_dir / "categories.yml"
    if not categories_path.is_file():
        return {}

    icon_categories: dict[str, set[str]] = {}
    current_category = None
    in_icons_block = False

    yaml_text = textwrap.dedent(categories_path.read_text(encoding="utf-8"))

    for raw_line in yaml_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent == 0 and stripped.endswith(":"):
            current_category = _strip_yaml_scalar(stripped[:-1])
            in_icons_block = False
            continue

        if current_category is None:
            continue

        if indent == 2 and stripped == "icons:":
            in_icons_block = True
            continue

        if indent == 2 and stripped.endswith(":"):
            in_icons_block = False
            continue

        if in_icons_block and stripped.startswith("- "):
            icon_name = _strip_yaml_scalar(stripped[2:])
            icon_categories.setdefault(icon_name, set()).add(current_category)

    return {
        icon_name: tuple(sorted(category_names))
        for icon_name, category_names in sorted(icon_categories.items())
    }


def _load_icon_metadata(metadata_dir: Path) -> dict[str, Any]:
    """Load icon metadata from the supported Font Awesome metadata files.

    Args:
        metadata_dir: Path to the package metadata directory.

    Returns:
        dict[str, Any]: Mapping of icon names to metadata records.

    Raises:
        FileNotFoundError: If no supported metadata file is present.
    """
    candidate_files = ("icons.json", "icon-families.json")

    for file_name in candidate_files:
        metadata_path = metadata_dir / file_name
        if not metadata_path.is_file():
            continue
        with metadata_path.open("r", encoding="utf-8") as handle:
            icon_metadata = json.load(handle)
        if not isinstance(icon_metadata, dict):
            raise ValueError(f"Expected a JSON object in {metadata_path}.")
        return icon_metadata

    raise FileNotFoundError(
        f"Could not find supported Font Awesome metadata in {metadata_dir}. "
        f"Tried: {', '.join(candidate_files)}. "
        f"Available files: {', '.join(sorted(path.name for path in metadata_dir.iterdir())) if metadata_dir.is_dir() else 'metadata directory missing'}."
    )


def validate_fontawesome_package(package_root, styles=DEFAULT_STYLES):
    """Validate that the source package only contains supported free assets.

    Args:
        package_root: Root directory of the installed Font Awesome package.
        styles: Allowed SVG style directories.

    Raises:
        ValueError: If the package name or available styles do not match the
            expected free package layout.
    """
    package_root = Path(package_root)
    package_json_path = package_root / "package.json"
    svg_root = package_root / "svgs"

    with package_json_path.open("r", encoding="utf-8") as handle:
        package_metadata = json.load(handle)

    package_name = package_metadata.get("name")
    if package_name != EXPECTED_PACKAGE_NAME:
        raise ValueError(
            f"Expected package name {EXPECTED_PACKAGE_NAME!r}, found {package_name!r} in {package_json_path}."
        )

    allowed_styles = set(styles)
    actual_styles = {path.name for path in svg_root.iterdir() if path.is_dir()}
    unexpected_styles = sorted(actual_styles - allowed_styles)
    if unexpected_styles:
        raise ValueError(
            f"Unexpected SVG style directories found in {svg_root}: {', '.join(unexpected_styles)}."
        )


def load_fontawesome_package(package_root, styles=DEFAULT_STYLES):
    """Load SVGs, aliases, and categories from a Font Awesome package.

    Args:
        package_root: Root directory of the installed Font Awesome package.
        styles: SVG style directories to include.

    Returns:
        tuple[dict[str, str], dict[str, str], dict[str, tuple[str, ...]]]:
            Mappings for SVG content, aliases, and category metadata.
    """
    package_root = Path(package_root)
    svg_root = package_root / "svgs"
    metadata_dir = package_root / "metadata"
    validate_fontawesome_package(package_root, styles)

    svg_dict = {}
    for style in styles:
        style_dir = svg_root / style
        if not style_dir.is_dir():
            continue
        for file in sorted(style_dir.glob("*.svg")):
            svg_dict[file.stem] = file.read_text(encoding="utf-8")

    icons = _load_icon_metadata(metadata_dir)
    yaml_category_dict = _load_categories_yaml(metadata_dir)

    alias_dict = {}
    category_dict = {}
    for icon_name, icon_data in icons.items():
        for alias in _extract_aliases(icon_data):
            alias_dict[alias] = icon_name

        categories = _extract_categories(icon_data)
        if icon_name in yaml_category_dict:
            categories = tuple(sorted(set(categories).union(yaml_category_dict[icon_name])))
        if categories:
            category_dict[icon_name] = categories

    return svg_dict, alias_dict, category_dict


def write_data_module(output_path, svg_dict, alias_dict, category_dict):
    """Write bundled Font Awesome data to a Python module.

    Args:
        output_path: Output file for the generated module.
        svg_dict: Mapping of icon names to raw SVG strings.
        alias_dict: Mapping of alias names to canonical icon names.
        category_dict: Mapping of icon names to category tuples.
    """
    output_path = Path(output_path)
    output_path.write_text(
        "FA = "
        + pformat(svg_dict, width=9999, indent=4)
        + "\nFA_aliases = "
        + pformat(alias_dict, indent=4)
        + "\nFA_categories = "
        + pformat(category_dict, indent=4)
        + "\n",
        encoding="utf-8",
    )


def regenerate_from_package(package_root, output_path):
    """Generate and write bundled Font Awesome data from a package root.

    Args:
        package_root: Root directory of the installed Font Awesome package.
        output_path: Output file for the generated module.

    Returns:
        tuple[int, int, int]: Counts of icons, aliases, and categorised icons.
    """
    svg_dict, alias_dict, category_dict = load_fontawesome_package(package_root)
    write_data_module(output_path, svg_dict, alias_dict, category_dict)
    return len(svg_dict), len(alias_dict), len(category_dict)


def main():
    """Run the generator as a command-line tool."""
    parser = argparse.ArgumentParser(description="Generate bundled Font Awesome data.")
    parser.add_argument("package_root", help="Path to the extracted @fortawesome/fontawesome-free package")
    parser.add_argument(
        "--output",
        default=Path(__file__).resolve().parents[1] / "ctkfontawesome" / "svgs.py",
        type=Path,
        help="Output path for the generated Python data module",
    )
    args = parser.parse_args()

    icon_count, alias_count, category_count = regenerate_from_package(args.package_root, args.output)
    print(
        f"Wrote {args.output} with {icon_count} icons, {alias_count} aliases, "
        f"and {category_count} categorized icons."
    )


if __name__ == "__main__":
    main()
