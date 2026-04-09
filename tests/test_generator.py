"""Tests for the Font Awesome metadata generator."""

# Author: Clive Bostock
# Date: 2026-04-09
# Description: Verify generator output and package validation rules.

import tempfile
import unittest
from pathlib import Path

from development.fontawesome_generator import (
    EXPECTED_PACKAGE_NAME,
    load_fontawesome_package,
    validate_fontawesome_package,
    write_data_module,
)


SAMPLE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"></svg>'


class GeneratorTests(unittest.TestCase):
    """Tests for Font Awesome package metadata extraction."""

    def _write_package_manifest(
        self,
        package_root: Path,
        package_name: str = EXPECTED_PACKAGE_NAME,
    ) -> None:
        """Write a minimal package manifest for a synthetic test package."""
        (package_root / "package.json").write_text(
            f'{{"name": "{package_name}"}}',
            encoding="utf-8",
        )

    def test_load_fontawesome_package_reads_aliases_and_categories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir)
            (package_root / "svgs" / "brands").mkdir(parents=True)
            (package_root / "metadata").mkdir()
            self._write_package_manifest(package_root)
            (package_root / "svgs" / "brands" / "facebook.svg").write_text(SAMPLE_SVG, encoding="utf-8")
            (package_root / "metadata" / "icons.json").write_text(
                """
                {
                  "facebook": {
                    "aliases": {"names": ["fb"]},
                    "categories": ["social", "brands"]
                  }
                }
                """,
                encoding="utf-8",
            )

            svg_dict, alias_dict, category_dict = load_fontawesome_package(package_root)

            self.assertEqual(svg_dict["facebook"], SAMPLE_SVG)
            self.assertEqual(alias_dict["fb"], "facebook")
            self.assertEqual(category_dict["facebook"], ("brands", "social"))

    def test_load_fontawesome_package_falls_back_to_icon_families_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir)
            (package_root / "svgs" / "brands").mkdir(parents=True)
            (package_root / "metadata").mkdir()
            self._write_package_manifest(package_root)
            (package_root / "svgs" / "brands" / "facebook.svg").write_text(SAMPLE_SVG, encoding="utf-8")
            (package_root / "metadata" / "icon-families.json").write_text(
                """
                {
                  "facebook": {
                    "aliases": {"names": ["fb"]},
                    "categories": ["social", "brands"]
                  }
                }
                """,
                encoding="utf-8",
            )

            svg_dict, alias_dict, category_dict = load_fontawesome_package(package_root)

            self.assertEqual(svg_dict["facebook"], SAMPLE_SVG)
            self.assertEqual(alias_dict["fb"], "facebook")
            self.assertEqual(category_dict["facebook"], ("brands", "social"))

    def test_load_fontawesome_package_reads_categories_from_categories_yml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir)
            (package_root / "svgs" / "brands").mkdir(parents=True)
            (package_root / "metadata").mkdir()
            self._write_package_manifest(package_root)
            (package_root / "svgs" / "brands" / "facebook.svg").write_text(SAMPLE_SVG, encoding="utf-8")
            (package_root / "metadata" / "icon-families.json").write_text(
                """
                {
                  "facebook": {
                    "aliases": {"names": ["fb"]}
                  }
                }
                """,
                encoding="utf-8",
            )
            (package_root / "metadata" / "categories.yml").write_text(
                """
                social:
                  label: Social
                  icons:
                    - facebook
                brands:
                  label: Brands
                  icons:
                    - facebook
                """,
                encoding="utf-8",
            )

            svg_dict, alias_dict, category_dict = load_fontawesome_package(package_root)

            self.assertEqual(svg_dict["facebook"], SAMPLE_SVG)
            self.assertEqual(alias_dict["fb"], "facebook")
            self.assertEqual(category_dict["facebook"], ("brands", "social"))

    def test_validate_fontawesome_package_rejects_non_free_package_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir)
            (package_root / "svgs").mkdir()
            self._write_package_manifest(package_root, package_name="@fortawesome/pro-solid-svg-icons")

            with self.assertRaises(ValueError):
                validate_fontawesome_package(package_root)

    def test_validate_fontawesome_package_rejects_unexpected_style_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir)
            (package_root / "svgs" / "brands").mkdir(parents=True)
            (package_root / "svgs" / "duotone").mkdir(parents=True)
            self._write_package_manifest(package_root)

            with self.assertRaises(ValueError):
                validate_fontawesome_package(package_root)

    def test_write_data_module_includes_category_mapping(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "svgs.py"
            write_data_module(
                output_path,
                {"facebook": SAMPLE_SVG},
                {"fb": "facebook"},
                {"facebook": ("brands", "social")},
            )

            output = output_path.read_text(encoding="utf-8")
            self.assertIn("FA = {", output)
            self.assertIn("FA_aliases = {", output)
            self.assertIn("FA_categories = {", output)


if __name__ == "__main__":
    unittest.main()
