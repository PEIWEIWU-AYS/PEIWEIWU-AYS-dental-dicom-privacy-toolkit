from __future__ import annotations

from pathlib import Path

import numpy as np
import pydicom

from ddpt.models import PixelRectangle, PixelRedactionAudit
from ddpt.utils import ensure_parent


def parse_rectangle(value: str) -> PixelRectangle:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("Rectangle must use x,y,width,height format")
    x, y, width, height = (int(part) for part in parts)
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError("Rectangle coordinates must be non-negative with positive size")
    return PixelRectangle(x=x, y=y, width=width, height=height)


def redact_pixels(
    input_path: Path,
    output_path: Path,
    rectangles: list[PixelRectangle],
    fill_value: int = 0,
) -> PixelRedactionAudit:
    dataset = pydicom.dcmread(input_path)
    pixel_array = np.array(dataset.pixel_array, copy=True)
    if not rectangles:
        raise ValueError("At least one rectangle is required")

    for rectangle in rectangles:
        _apply_rectangle(pixel_array, rectangle, fill_value)

    dataset.PixelData = pixel_array.astype(pixel_array.dtype).tobytes()
    ensure_parent(output_path)
    dataset.save_as(output_path, enforce_file_format=True)

    return PixelRedactionAudit(
        input_path=str(input_path),
        output_path=str(output_path),
        rectangles=rectangles,
        fill_value=fill_value,
        note=(
            "Manual rectangle pixel redaction was applied. This does not prove that all "
            "burned-in identifiers were found or removed."
        ),
    )


def _apply_rectangle(pixel_array: np.ndarray, rectangle: PixelRectangle, fill_value: int) -> None:
    if pixel_array.ndim == 3 and pixel_array.shape[-1] in (3, 4):
        rows = pixel_array.shape[0]
        cols = pixel_array.shape[1]
    else:
        rows = pixel_array.shape[-2]
        cols = pixel_array.shape[-1]

    if rectangle.x + rectangle.width > cols or rectangle.y + rectangle.height > rows:
        raise ValueError("Rectangle exceeds pixel array bounds")

    y_slice = slice(rectangle.y, rectangle.y + rectangle.height)
    x_slice = slice(rectangle.x, rectangle.x + rectangle.width)

    if pixel_array.ndim == 2:
        pixel_array[y_slice, x_slice] = fill_value
    elif pixel_array.ndim == 3 and pixel_array.shape[-1] in (3, 4):
        pixel_array[y_slice, x_slice, :] = fill_value
    elif pixel_array.ndim == 3:
        pixel_array[:, y_slice, x_slice] = fill_value
    else:
        raise ValueError(f"Unsupported pixel array shape: {pixel_array.shape}")
