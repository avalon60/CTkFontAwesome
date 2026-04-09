[![GitHub issues](https://img.shields.io/github/issues/avalon60/CTkFontAwesome.svg)](https://github.com/avalon60/CTkFontAwesome/issues)
[![License](https://img.shields.io/github/license/avalon60/CTkFontAwesome.svg)](https://github.com/avalon60/CTkFontAwesome/blob/main/LICENSE)

# CTkFontAwesome

> Requires Python **3.8+**

CTkFontAwesome is a maintained continuation and repackaging of the original
TkFontAwesome project by Israel Dryer.

A library that enables you to use [FontAwesome icons](https://fontawesome.com/v6/icons?o=r&m=free)
in your CustomTkinter / Tkinter application.

You may use any of the 2k+ *free* [FontAwesome 6.5 icons](https://fontawesome.com/v6/icons?o=r&m=free).
The **fill color** and **size** are customized to your specifications and then converted
to an object via an optional image backend based on CairoSVG and Pillow that can be used anywhere you would use a `tkinter.PhotoImage` object.

![example-2](https://raw.githubusercontent.com/avalon60/CTkFontAwesome/main/assets/example-2.png)

## Highlights

- Use 2k+ bundled free Font Awesome icons without downloading assets at runtime
- Generate `customtkinter.CTkImage` objects for DPI-aware CustomTkinter widgets
- Generate `tkinter.PhotoImage` objects for Tkinter widgets
- Launch an icon browser to search icons, preview them, and copy ready-to-use code
- Access raw SVG XML when you want to manage rendering yourself

## Icon Browser

CTkFontAwesome includes an installable browser for searching the bundled icon set,
previewing icons, and copying ready-to-use CustomTkinter code snippets.

```shell
ctkfontawesome-browser
```

The browser is included in the base install. Live image previews require the
optional image dependencies:

```shell
python -m pip install "ctkfontawesome[images]"
```

![CTkFontAwesome browser](assets/browser.png)

## Installation

```shell
python -m pip install ctkfontawesome
```

This installs the icon database and SVG lookup helpers without any native or compiled dependencies.

If you also want `icon_to_image()` or `icon_to_ctkimage()`, install the optional image dependencies:

```shell
python -m pip install "ctkfontawesome[images]"
```

This installs CairoSVG, Pillow, and CustomTkinter for SVG rasterization,
image support, and CustomTkinter integration.

## CustomTkinter Usage

Use `icon_to_ctkimage()` when you want a `customtkinter.CTkImage` for
CustomTkinter widgets.

```python
import customtkinter as ctk
from ctkfontawesome import icon_to_ctkimage

app = ctk.CTk()
icon = icon_to_ctkimage("eye", fill="#1D9F75", scale_to_width=28)

button = ctk.CTkButton(app, text="Preview", image=icon, compound="left")
button.pack(padx=20, pady=20)

app.mainloop()
```

## Tkinter Usage

Use `icon_to_image()` when you want a `tkinter.PhotoImage` for standard Tkinter
widgets.

```python
import tkinter as tk
from ctkfontawesome import icon_to_image

root = tk.Tk()
fb = icon_to_image("facebook", fill="#4267B2", scale_to_width=64)
send = icon_to_image("paper-plane", fill="#1D9F75", scale_to_width=64)

tk.Label(root, image=fb).pack(padx=10, pady=10)
tk.Button(root, image=send).pack(padx=10, pady=10)

root.mainloop()
```

## Usage Without Image Dependencies

If you only need the bundled icon data, use `icon_to_svg()` and avoid the
optional image stack entirely.

```python
from ctkfontawesome import icon_to_svg

svg = icon_to_svg("facebook")
print(svg[:80])
```

## Development

```shell
poetry install
```

To install the optional image backend in the Poetry environment:

```shell
poetry install --extras images
```

To run the icon browser during development:

```shell
poetry run ctkfontawesome-browser
```

To run the automated test suite:

```shell
poetry run pytest -q
```

If you are using the project virtualenv directly instead of Poetry:

```shell
.venv/bin/python -m pytest -q
```

To refresh the bundled Font Awesome SVGs and metadata from the upstream npm
package:

```shell
.venv/bin/python development/update_fontawesome.py
```

This maintainer command installs `@fortawesome/fontawesome-free` into a
temporary directory, then regenerates [`ctkfontawesome/svgs.py`](ctkfontawesome/svgs.py)
with icon SVGs, aliases, and any upstream category metadata that is present.

Recommended update workflow:

1. Generate a candidate data file without touching the checked-in module:

   ```shell
   .venv/bin/python development/update_fontawesome.py --output /tmp/svgs_new.py
   ```

2. Smoke-test the generated file structure and icon counts:

   ```shell
   .venv/bin/python development/smoke_test_fontawesome_update.py /tmp/svgs_new.py
   ```

3. Compare the candidate file against the current checked-in data:

   ```shell
   .venv/bin/python development/smoke_test_fontawesome_update.py /tmp/svgs_new.py --compare-to ctkfontawesome/svgs.py
   ```

4. If the candidate looks correct, regenerate the checked-in module:

   ```shell
   .venv/bin/python development/update_fontawesome.py
   ```

5. Run the automated test suite:

   ```shell
   .venv/bin/python -m pytest -q
   ```

The smoke test validates the generated module shape, checks a known icon is
present, and compares counts with the current checked-in data. It does not run
the npm update itself.

To smoke-test a generated data file directly:

```shell
.venv/bin/python development/update_fontawesome.py --output /tmp/svgs_new.py
.venv/bin/python development/smoke_test_fontawesome_update.py /tmp/svgs_new.py
```

To compare a generated file against the current checked-in data:

```shell
.venv/bin/python development/smoke_test_fontawesome_update.py /tmp/svgs_new.py --compare-to ctkfontawesome/svgs.py
```

To bump the package version and create a git commit and tag:

```shell
poetry run bump2version patch
```

Use `minor` or `major` instead of `patch` when appropriate. The bump updates
both `pyproject.toml` and `ctkfontawesome/__init__.py`.

Once installed, you can launch the browser with:

```shell
ctkfontawesome-browser
```

![example-1](https://raw.githubusercontent.com/avalon60/CTkFontAwesome/main/assets/example-1.png)

## API: `icon_to_image()`

```python
(
    name=None,
    fill=None,
    scale_to_width=None,
    scale_to_height=None,
    scale=1
)
```

### Parameters

| Name              | Type  | Description                                                           | Default   |
|-------------------|-------|-----------------------------------------------------------------------|-----------|
| name              | str   | The name of the FontAwesome icon.                                     | None      |
| fill              | str   | The fill color of the svg path.                                       | None      |
| scale_to_width    | int   | Adjust image width to this size (in pixels); maintains aspect ratio.  | None      |
| scale_to_height   | int   | Adjust image height to this size (in pixels); maintains aspect ratio. | None      |
| scale             | float | Scale the image width and height by this factor.                      | 1         |

## API: `icon_to_ctkimage()`

Same parameters as `icon_to_image()`, but returns a `customtkinter.CTkImage`
for DPI-aware use in CustomTkinter widgets. This API requires the
`ctkfontawesome[images]` optional dependencies.

## API: `icon_to_svg()`

Returns the raw SVG XML string for the requested icon name.

## License

The [CC BY 4.0](https://fontawesome.com/license/free) license applies to all FontAwesome *free* icons used in the library.
The MIT License applies to all other work.

---

**Maintainer**: Clive Bostock
Original project concept and implementation by [Israel Dryer](https://github.com/israel-dryer)
📦 Available on [PyPI](https://pypi.org/project/ctkfontawesome/) | 🐙 [GitHub](https://github.com/avalon60/CTkFontAwesome)
