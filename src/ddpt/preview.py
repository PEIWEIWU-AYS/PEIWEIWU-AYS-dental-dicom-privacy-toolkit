from __future__ import annotations

from pathlib import Path

import numpy as np
import pydicom
from PIL import Image

from ddpt.models import PreviewReport
from ddpt.utils import ensure_parent, value_to_text


def render_dicom_preview(
    input_path: Path,
    output_path: Path,
    max_size: int = 512,
) -> PreviewReport:
    dataset = pydicom.dcmread(input_path)
    pixels = _to_grayscale_array(dataset.pixel_array)
    rows, columns = pixels.shape
    min_pixel = float(np.min(pixels))
    max_pixel = float(np.max(pixels))
    image_array = _normalize_to_uint8(pixels)

    photometric = value_to_text(dataset.get("PhotometricInterpretation", "")) or None
    if photometric == "MONOCHROME1":
        image_array = 255 - image_array

    image = Image.fromarray(image_array)
    rendered_width, rendered_height = _rendered_size(columns, rows, max_size=max_size)
    if (rendered_width, rendered_height) != (columns, rows):
        image = image.resize((rendered_width, rendered_height), Image.Resampling.NEAREST)

    ensure_parent(output_path)
    image.save(output_path)

    return PreviewReport(
        input_path=str(input_path),
        output_path=str(output_path),
        rows=rows,
        columns=columns,
        rendered_width=rendered_width,
        rendered_height=rendered_height,
        min_pixel_value=min_pixel,
        max_pixel_value=max_pixel,
        photometric_interpretation=photometric,
        note="PNG preview is for workflow review only, not diagnostic interpretation.",
    )


def _to_grayscale_array(pixel_array: np.ndarray) -> np.ndarray:
    pixels = np.asarray(pixel_array)
    if pixels.ndim == 2:
        return pixels.astype(np.float32)
    if pixels.ndim == 3 and pixels.shape[-1] in {3, 4}:
        return pixels[..., :3].mean(axis=-1).astype(np.float32)
    if pixels.ndim >= 3:
        return np.asarray(pixels[0]).astype(np.float32)
    raise ValueError("Unsupported DICOM pixel array shape")


def _normalize_to_uint8(pixels: np.ndarray) -> np.ndarray:
    min_pixel = float(np.min(pixels))
    max_pixel = float(np.max(pixels))
    if max_pixel == min_pixel:
        return np.zeros(pixels.shape, dtype=np.uint8)
    normalized = (pixels - min_pixel) / (max_pixel - min_pixel)
    return np.clip(normalized * 255, 0, 255).astype(np.uint8)


def _rendered_size(columns: int, rows: int, max_size: int) -> tuple[int, int]:
    if columns <= 0 or rows <= 0:
        raise ValueError("DICOM pixel dimensions must be positive")

    largest_side = max(columns, rows)
    if largest_side <= max_size:
        scale = max(1, min(max_size // largest_side, 64))
        return columns * scale, rows * scale

    ratio = max_size / largest_side
    return max(1, round(columns * ratio)), max(1, round(rows * ratio))
