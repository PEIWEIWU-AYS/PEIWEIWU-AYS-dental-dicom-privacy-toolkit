from __future__ import annotations

from pathlib import Path

import numpy as np
import pydicom
from PIL import Image, ImageDraw

from ddpt.models import PixelRectangle, PixelReviewRegion, PixelReviewReport
from ddpt.redaction_plan import load_redaction_plan, rectangles_from_plan
from ddpt.utils import value_to_text


def create_pixel_review(
    input_path: Path,
    output_dir: Path,
    rectangles: list[PixelRectangle],
    plan_path: Path | None = None,
    fill_value: int = 0,
    max_size: int = 512,
) -> PixelReviewReport:
    dataset = pydicom.dcmread(input_path)
    pixel_array = np.array(dataset.pixel_array, copy=True)
    pixels = _to_grayscale_array(pixel_array)
    rows, columns = pixels.shape
    region_pairs = [
        (f"manual-{index + 1}", rectangle) for index, rectangle in enumerate(rectangles)
    ]

    if plan_path:
        plan = load_redaction_plan(plan_path)
        plan_rectangles = rectangles_from_plan(input_path, plan_path)
        region_pairs.extend(
            (region.label, rectangle)
            for region, rectangle in zip(plan.regions, plan_rectangles, strict=True)
        )

    if not region_pairs:
        raise ValueError("At least one manual rectangle or redaction plan is required")

    output_dir.mkdir(parents=True, exist_ok=True)
    original_preview = output_dir / "pixel-review-original.png"
    overlay_preview = output_dir / "pixel-review-overlay.png"
    redacted_preview = output_dir / "pixel-review-redacted.png"

    image_array = _normalize_to_uint8(pixels)
    original_image = _resize_image(Image.fromarray(image_array), columns, rows, max_size)
    original_image.save(original_preview)

    scale_x = original_image.width / columns
    scale_y = original_image.height / rows
    overlay_image = original_image.convert("RGB")
    draw = ImageDraw.Draw(overlay_image)
    for _, rectangle in region_pairs:
        _validate_rectangle(rectangle, rows=rows, columns=columns)
        x0 = round(rectangle.x * scale_x)
        y0 = round(rectangle.y * scale_y)
        x1 = round((rectangle.x + rectangle.width) * scale_x)
        y1 = round((rectangle.y + rectangle.height) * scale_y)
        draw.rectangle([x0, y0, x1, y1], outline=(220, 38, 38), width=3)
    overlay_image.save(overlay_preview)

    redacted_pixels = np.array(pixels, copy=True)
    for _, rectangle in region_pairs:
        redacted_pixels[
            rectangle.y : rectangle.y + rectangle.height,
            rectangle.x : rectangle.x + rectangle.width,
        ] = fill_value
    redacted_image = _resize_image(
        Image.fromarray(_normalize_to_uint8(redacted_pixels)),
        columns,
        rows,
        max_size,
    )
    redacted_image.save(redacted_preview)

    burned_in = value_to_text(dataset.get("BurnedInAnnotation", "")) or None
    warnings = _pixel_review_warnings(burned_in)
    regions = [
        PixelReviewRegion(
            label=label,
            x=rectangle.x,
            y=rectangle.y,
            width=rectangle.width,
            height=rectangle.height,
        )
        for label, rectangle in region_pairs
    ]
    return PixelReviewReport(
        input_path=str(input_path),
        plan_path=str(plan_path) if plan_path else None,
        original_preview_png=str(original_preview),
        overlay_preview_png=str(overlay_preview),
        redacted_preview_png=str(redacted_preview),
        rows=rows,
        columns=columns,
        rendered_width=original_image.width,
        rendered_height=original_image.height,
        burned_in_annotation=burned_in,
        regions=regions,
        warnings=warnings,
        note=(
            "Pixel review images are for workflow review only. They do not prove that "
            "all burned-in identifiers were found or removed."
        ),
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


def _resize_image(image: Image.Image, columns: int, rows: int, max_size: int) -> Image.Image:
    rendered_width, rendered_height = _rendered_size(columns, rows, max_size=max_size)
    if (rendered_width, rendered_height) == (columns, rows):
        return image
    return image.resize((rendered_width, rendered_height), Image.Resampling.NEAREST)


def _rendered_size(columns: int, rows: int, max_size: int) -> tuple[int, int]:
    if columns <= 0 or rows <= 0:
        raise ValueError("DICOM pixel dimensions must be positive")
    largest_side = max(columns, rows)
    if largest_side <= max_size:
        scale = max(1, min(max_size // largest_side, 64))
        return columns * scale, rows * scale
    ratio = max_size / largest_side
    return max(1, round(columns * ratio)), max(1, round(rows * ratio))


def _validate_rectangle(rectangle: PixelRectangle, rows: int, columns: int) -> None:
    if rectangle.x + rectangle.width > columns or rectangle.y + rectangle.height > rows:
        raise ValueError("Rectangle exceeds pixel array bounds")


def _pixel_review_warnings(burned_in: str | None) -> list[str]:
    warnings = [
        "Manual visual review is still required for burned-in identifiers.",
        "Preview PNGs are not diagnostic images.",
    ]
    if burned_in is None:
        warnings.append("BurnedInAnnotation is missing.")
    elif burned_in.upper() != "NO":
        warnings.append(f"BurnedInAnnotation is {burned_in!r}.")
    return warnings
