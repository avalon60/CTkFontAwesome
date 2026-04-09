"""Tests for the Font Awesome update smoke-test helper."""

# Author: Clive Bostock
# Date: 2026-04-09
# Description: Verify smoke-test validation for generated Font Awesome modules.

import types
import unittest

from development.smoke_test_fontawesome_update import compare_modules, validate_generated_module


class SmokeUpdateTests(unittest.TestCase):
    """Tests for generated module smoke-test helpers."""

    def test_validate_generated_module_accepts_expected_shape(self) -> None:
        module = types.SimpleNamespace(
            FA={"facebook": "<svg xmlns='http://www.w3.org/2000/svg'></svg>"},
            FA_aliases={"fb": "facebook"},
            FA_categories={"facebook": ("brands",)},
        )

        counts = validate_generated_module(module, expected_icon="facebook", minimum_icons=1)

        self.assertEqual(counts, (1, 1, 1))

    def test_compare_modules_returns_count_deltas(self) -> None:
        baseline = types.SimpleNamespace(
            FA={"facebook": "<svg xmlns='http://www.w3.org/2000/svg'></svg>"},
            FA_aliases={},
            FA_categories={},
        )
        candidate = types.SimpleNamespace(
            FA={
                "facebook": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "github": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
            },
            FA_aliases={"git": "github"},
            FA_categories={"github": ("brands",)},
        )

        deltas = compare_modules(candidate, baseline)

        self.assertEqual(deltas, (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
