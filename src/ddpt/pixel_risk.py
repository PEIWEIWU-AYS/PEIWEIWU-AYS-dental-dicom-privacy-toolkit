from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pydicom

from ddpt.models import PixelRiskScanReport, PixelRiskSignal
from ddpt.utils import value_to_text


def scan_pixel_risk(input_path: Path) -> PixelRiskScanReport:
    dataset = pydicom.dcmread(input_path)
    burned_in = value_to_text(dataset.get("BurnedInAnnotation", "")) or None
    signals: list[PixelRiskSignal] = []
    recommended_actions: list[str] = []

    if "PixelData" not in dataset:
        signals.append(
            _signal(
                "pixel-data-present",
                "high",
                False,
                "DICOM PixelData is missing.",
                [],
            )
        )
        return PixelRiskScanReport(
            input_path=str(input_path),
            passed=False,
            pixel_data_present=False,
            burned_in_annotation=burned_in,
            signals=signals,
            recommended_actions=["Confirm this file is intended to be image-free."],
            note=_NOTE,
        )

    try:
        pixels = _to_grayscale_array(dataset.pixel_array)
    except Exception as exc:
        signals.append(
            _signal(
                "pixel-data-readable",
                "high",
                False,
                "DICOM PixelData could not be decoded.",
                [str(exc)],
            )
        )
        return PixelRiskScanReport(
            input_path=str(input_path),
            passed=False,
            pixel_data_present=True,
            burned_in_annotation=burned_in,
            signals=signals,
            recommended_actions=["Decode with a supported transfer syntax before sharing."],
            note=_NOTE,
        )

    rows, columns = pixels.shape
    min_pixel = float(np.min(pixels))
    max_pixel = float(np.max(pixels))
    edge_fraction, edge_contrast = _edge_metrics(pixels)

    signals.extend(
        [
            _signal(
                "pixel-data-readable",
                "low",
                True,
                "DICOM PixelData is readable.",
                [f"rows={rows}", f"columns={columns}"],
            ),
            _burned_in_signal(burned_in),
            _edge_signal(edge_fraction, rows, columns),
            _contrast_signal(edge_contrast, rows, columns),
        ]
    )

    failed = [signal for signal in signals if not signal.passed]
    if any(signal.id == "burned-in-annotation" for signal in failed):
        recommended_actions.append(
            "Run pixel review before sharing because BurnedInAnnotation is not reassuring."
        )
    if any(signal.id in {"edge-high-intensity", "edge-contrast"} for signal in failed):
        recommended_actions.append(
            "Inspect edge bands for burned-in labels and add a redaction plan if needed."
        )
    if not recommended_actions:
        recommended_actions.append(
            "Continue with metadata de-identification, validation, and workflow quality gate."
        )

    passed = not any(
        not signal.passed and signal.severity in {"high", "medium"} for signal in signals
    )
    return PixelRiskScanReport(
        input_path=str(input_path),
        passed=passed,
        pixel_data_present=True,
        rows=rows,
        columns=columns,
        burned_in_annotation=burned_in,
        min_pixel_value=min_pixel,
        max_pixel_value=max_pixel,
        edge_high_intensity_fraction=edge_fraction,
        edge_contrast_ratio=edge_contrast,
        signals=signals,
        recommended_actions=recommended_actions,
        note=_NOTE,
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


def _burned_in_signal(burned_in: str | None) -> PixelRiskSignal:
    if burned_in is None:
        return _signal(
            "burned-in-annotation",
            "medium",
            False,
            "BurnedInAnnotation is missing.",
            [],
        )
    if burned_in.upper() != "NO":
        return _signal(
            "burned-in-annotation",
            "high",
            False,
            f"BurnedInAnnotation is {burned_in!r}.",
            [],
        )
    return _signal(
        "burned-in-annotation",
        "low",
        True,
        "BurnedInAnnotation is NO.",
        [],
    )


def _edge_signal(edge_fraction: float | None, rows: int, columns: int) -> PixelRiskSignal:
    if edge_fraction is None:
        return _signal(
            "edge-high-intensity",
            "low",
            True,
            "Image is too small for edge high-intensity screening.",
            [f"rows={rows}", f"columns={columns}"],
        )
    passed = edge_fraction < 0.20
    return _signal(
        "edge-high-intensity",
        "medium",
        passed,
        "Edge high-intensity fraction is below review threshold."
        if passed
        else "Edge high-intensity fraction may indicate label bands.",
        [f"fraction={edge_fraction:.4f}", "threshold=0.2000"],
    )


def _contrast_signal(edge_contrast: float | None, rows: int, columns: int) -> PixelRiskSignal:
    if edge_contrast is None:
        return _signal(
            "edge-contrast",
            "low",
            True,
            "Image is too small for edge contrast screening.",
            [f"rows={rows}", f"columns={columns}"],
        )
    passed = edge_contrast < 0.35
    return _signal(
        "edge-contrast",
        "medium",
        passed,
        "Edge contrast ratio is below review threshold."
        if passed
        else "Edge contrast ratio may indicate burned-in overlays or label bands.",
        [f"ratio={edge_contrast:.4f}", "threshold=0.3500"],
    )


def _edge_metrics(pixels: np.ndarray) -> tuple[float | None, float | None]:
    rows, columns = pixels.shape
    if rows < 8 or columns < 8:
        return None, None
    width = max(1, round(min(rows, columns) * 0.08))
    mask = np.zeros((rows, columns), dtype=bool)
    mask[:width, :] = True
    mask[-width:, :] = True
    mask[:, :width] = True
    mask[:, -width:] = True
    edge_pixels = pixels[mask]
    center_pixels = pixels[~mask]
    pixel_range = float(np.max(pixels) - np.min(pixels))
    if pixel_range == 0:
        return 0.0, 0.0
    high_threshold = float(np.min(pixels) + pixel_range * 0.92)
    edge_fraction = float(np.mean(edge_pixels >= high_threshold))
    edge_contrast = abs(float(np.mean(edge_pixels)) - float(np.mean(center_pixels))) / pixel_range
    return edge_fraction, edge_contrast


def _signal(
    signal_id: str,
    severity: Literal["high", "medium", "low"],
    passed: bool,
    message: str,
    evidence: list[str],
) -> PixelRiskSignal:
    return PixelRiskSignal(
        id=signal_id,
        severity=severity,
        passed=passed,
        message=message,
        evidence=evidence,
    )


_NOTE = (
    "Pixel risk scan is a conservative workflow screen. It is not OCR, clinical "
    "interpretation, legal certification, or proof that all burned-in identifiers "
    "were detected."
)
