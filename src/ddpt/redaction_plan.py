from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import Any

import pydicom
import yaml

from ddpt.models import PixelRectangle, PixelRedactionPlan, PixelRedactionPlanRegion
from ddpt.utils import ensure_parent

DEFAULT_REDACTION_PLAN: dict[str, Any] = {
    "name": "dental-burned-in-banner",
    "description": (
        "Demo dental pixel redaction plan for known burned-in acquisition labels "
        "near the top image banner."
    ),
    "regions": [
        {
            "label": "top-acquisition-banner",
            "unit": "percent",
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 12,
        }
    ],
}


def load_redaction_plan(path: Path) -> PixelRedactionPlan:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Redaction plan YAML must contain a mapping")
    return PixelRedactionPlan(**data)


def write_redaction_plan_template(path: Path, overwrite: bool = False) -> Path:
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists. Use --overwrite to replace it.")
    ensure_parent(path)
    path.write_text(
        yaml.safe_dump(DEFAULT_REDACTION_PLAN, sort_keys=False),
        encoding="utf-8",
    )
    return path


def rectangles_from_plan(input_path: Path, plan_path: Path) -> list[PixelRectangle]:
    plan = load_redaction_plan(plan_path)
    dataset = pydicom.dcmread(input_path, stop_before_pixels=True)
    rows = int(dataset.Rows)
    columns = int(dataset.Columns)
    return [_resolve_region(region, rows=rows, columns=columns) for region in plan.regions]


def _resolve_region(
    region: PixelRedactionPlanRegion,
    rows: int,
    columns: int,
) -> PixelRectangle:
    if region.unit == "pixels":
        x = round(region.x)
        y = round(region.y)
        width = round(region.width)
        height = round(region.height)
    else:
        _validate_percent_region(region)
        x = round(columns * region.x / 100)
        y = round(rows * region.y / 100)
        width = max(1, ceil(columns * region.width / 100))
        height = max(1, ceil(rows * region.height / 100))

    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError(f"Invalid redaction region: {region.label}")
    return PixelRectangle(x=x, y=y, width=width, height=height)


def _validate_percent_region(region: PixelRedactionPlanRegion) -> None:
    values = [region.x, region.y, region.width, region.height]
    if any(value < 0 or value > 100 for value in values):
        raise ValueError(f"Percent region values must be between 0 and 100: {region.label}")
    if region.x + region.width > 100 or region.y + region.height > 100:
        raise ValueError(f"Percent region exceeds image bounds: {region.label}")
