import io
from xml.etree import ElementTree as etree
from ctkfontawesome.svgs import FA, FA_aliases

__version__ = "0.4.0"


def icon_names():
    """
    Return the available Font Awesome icon names.

    Returns:
        list[str]: Sorted icon names available in the built-in SVG map.
    """
    return sorted(FA)


def icon_to_image(name, fill=None, scale_to_width=None, scale_to_height=None, scale=1):
    """
    Look up a FontAwesome icon by name and return it as a tkinter-compatible
    image object using an optional rendering backend.

    Parameters:
        name (str): Name of the FontAwesome icon (e.g., 'facebook').
        fill (str): Optional fill color for the icon (e.g., "#4267B2").
        scale_to_width (int): Target width in pixels (maintains aspect ratio).
        scale_to_height (int): Target height in pixels (maintains aspect ratio).
        scale (float): Scaling factor (applied only if width/height are not set).

    Returns:
        PhotoImage: The converted image ready for tkinter use when the
        optional image dependencies are installed.

    Example:
        import tkinter as tk
        from ctkfontawesome import icon_to_image

        root = tk.Tk()
        img = icon_to_image("facebook", fill="#4267B2", scale_to_width=64)
        tk.Label(root, image=img).pack(padx=10, pady=10)
        root.mainloop()
    """
    name = FA_aliases.get(name, name)
    if name.startswith('fa-'):
        name = name[3:]
    xml_data = icon_to_svg(name)
    return svg_to_image(xml_data, fill, scale_to_width, scale_to_height, scale)


def icon_to_svg(name):
    """
    Look up a FontAwesome icon by name and return the raw SVG XML string.

    Parameters:
        name (str): Name of the FontAwesome icon (e.g., 'facebook').

    Returns:
        str: Raw SVG XML for the requested icon.
    """
    name = FA_aliases.get(name, name)
    if name.startswith('fa-'):
        name = name[3:]
    xml_data = FA.get(name)
    if xml_data is None:
        raise ValueError(
            f"'{name}' is not a valid icon name. Check spelling or visit https://fontawesome.com/icons."
        )
    return xml_data


def svg_to_image(source, fill=None, scale_to_width=None, scale_to_height=None, scale=1):
    """
    Convert an SVG string into an image object for use in tkinter.

    Parameters:
        source (str): Raw SVG XML string.
        fill (str): Optional fill color override.
        scale_to_width (int): Width in pixels (maintains aspect ratio).
        scale_to_height (int): Height in pixels (maintains aspect ratio).
        scale (float): Optional scaling factor.

    Returns:
        PhotoImage: The processed image object when the optional image
        dependencies are installed.
    """
    try:
        import cairosvg
        from PIL import Image, ImageTk
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "svg_to_image() requires the optional image dependencies. "
            "Install them with `pip install 'ctkfontawesome[images]'`."
        ) from exc

    root = etree.fromstring(source)

    # Apply fill color override if provided
    if fill:
        for elem in root.iter():
            tag = str(elem.tag)
            if 'fill' in elem.attrib:
                elem.attrib['fill'] = fill
            elif tag.endswith("path"):
                elem.attrib['fill'] = fill

    width, height = _get_svg_dimensions(root)
    output_width, output_height = _compute_output_size(
        width,
        height,
        scale_to_width,
        scale_to_height,
        scale,
    )

    img_data = io.StringIO()
    etree.ElementTree(root).write(img_data, encoding="unicode")
    png_data = cairosvg.svg2png(
        bytestring=img_data.getvalue().encode("utf-8"),
        output_width=output_width,
        output_height=output_height,
    )
    image = Image.open(io.BytesIO(png_data))
    photo = ImageTk.PhotoImage(image=image)
    photo._pil_image = image
    return photo


def _get_svg_dimensions(root):
    view_box = root.attrib.get("viewBox")
    if view_box:
        _, _, width, height = (float(value) for value in view_box.replace(",", " ").split())
        return width, height

    width = _parse_dimension(root.attrib.get("width"))
    height = _parse_dimension(root.attrib.get("height"))
    if width is None or height is None:
        raise ValueError("SVG is missing a usable viewBox or width/height values.")
    return width, height


def _parse_dimension(value):
    if value is None:
        return None

    value = value.strip()
    digits = []
    for char in value:
        if char.isdigit() or char == ".":
            digits.append(char)
        else:
            break

    return float("".join(digits)) if digits else None


def _compute_output_size(width, height, scale_to_width, scale_to_height, scale):
    if scale_to_width and scale_to_height:
        return int(scale_to_width), int(scale_to_height)

    if scale_to_width:
        return int(scale_to_width), int(round((height / width) * scale_to_width))

    if scale_to_height:
        return int(round((width / height) * scale_to_height)), int(scale_to_height)

    if scale != 1:
        return int(round(width * scale)), int(round(height * scale))

    return None, None
