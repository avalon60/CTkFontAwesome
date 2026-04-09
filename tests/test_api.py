import unittest
from unittest import mock

import ctkfontawesome


class ApiTests(unittest.TestCase):
    def test_icon_names_returns_sorted_names(self):
        names = ctkfontawesome.icon_names()
        self.assertGreater(len(names), 1000)
        self.assertEqual(names, sorted(names))
        self.assertIn("facebook", names)

    def test_icon_to_svg_returns_svg_xml(self):
        svg = ctkfontawesome.icon_to_svg("facebook")
        self.assertTrue(svg.startswith("<svg "))
        self.assertIn("viewBox=", svg)

    def test_icon_to_svg_supports_fa_prefix(self):
        plain = ctkfontawesome.icon_to_svg("facebook")
        prefixed = ctkfontawesome.icon_to_svg("fa-facebook")
        self.assertEqual(plain, prefixed)

    def test_icon_categories_support_aliases(self):
        with mock.patch.dict(ctkfontawesome.FA_categories, {"facebook": ("brands",)}, clear=True):
            self.assertEqual(ctkfontawesome.icon_categories("facebook"), ("brands",))
            self.assertEqual(ctkfontawesome.icon_categories("fa-facebook"), ("brands",))

    def test_icon_categories_return_empty_tuple_when_no_categories_exist(self):
        with mock.patch.dict(ctkfontawesome.FA_categories, {}, clear=True):
            self.assertEqual(ctkfontawesome.icon_categories("facebook"), ())

    def test_category_names_returns_sorted_unique_names(self):
        with mock.patch.dict(
            ctkfontawesome.FA_categories,
            {
                "facebook": ("brands", "social"),
                "github": ("brands", "code"),
            },
            clear=True,
        ):
            self.assertEqual(
                ctkfontawesome.category_names(),
                ["brands", "code", "social"],
            )

    def test_icons_in_category_returns_sorted_names(self):
        with mock.patch.dict(
            ctkfontawesome.FA_categories,
            {
                "github": ("brands", "code"),
                "facebook": ("brands", "social"),
                "python": ("code",),
            },
            clear=True,
        ):
            self.assertEqual(
                ctkfontawesome.icons_in_category("code"),
                ["github", "python"],
            )

    def test_icons_in_category_returns_empty_list_for_unknown_category(self):
        with mock.patch.dict(ctkfontawesome.FA_categories, {"facebook": ("brands",)}, clear=True):
            self.assertEqual(ctkfontawesome.icons_in_category("social"), [])

    def test_icon_to_svg_rejects_invalid_icon_name(self):
        with self.assertRaises(ValueError):
            ctkfontawesome.icon_to_svg("not-a-real-icon-name")

    def test_icon_to_image_requires_optional_backend(self):
        with self.assertRaises(RuntimeError) as ctx:
            ctkfontawesome.icon_to_image("facebook")
        self.assertIn("optional image dependencies", str(ctx.exception))

    def test_icon_to_ctkimage_requires_optional_backend(self):
        with self.assertRaises(RuntimeError) as ctx:
            ctkfontawesome.icon_to_ctkimage("facebook")
        self.assertTrue(
            "optional image dependencies" in str(ctx.exception)
            or "CustomTkinter" in str(ctx.exception)
        )

    def test_compute_output_size_from_width(self):
        self.assertEqual(
            ctkfontawesome._compute_output_size(512, 512, 64, None, 1),
            (64, 64),
        )

    def test_compute_output_size_from_scale(self):
        self.assertEqual(
            ctkfontawesome._compute_output_size(512, 256, None, None, 0.5),
            (256, 128),
        )

    def test_svg_dimensions_use_viewbox(self):
        root = mock.Mock()
        root.attrib = {"viewBox": "0 0 640 512"}
        self.assertEqual(ctkfontawesome._get_svg_dimensions(root), (640.0, 512.0))

    def test_svg_dimensions_use_width_height(self):
        root = mock.Mock()
        root.attrib = {"width": "24px", "height": "12px"}
        self.assertEqual(ctkfontawesome._get_svg_dimensions(root), (24.0, 12.0))


if __name__ == "__main__":
    unittest.main()
