from __future__ import annotations

from pathlib import Path
from typing import Any

import pydicom
from pydicom.dataelem import DataElement

from ddpt.models import DicomJsonElement, DicomJsonExportReport, RiskLevel
from ddpt.policy import classify_element
from ddpt.utils import value_to_text

REDACTED_VALUE = "[redacted]"


def export_dicom_json(
    input_path: Path,
    include_values: bool = False,
) -> DicomJsonExportReport:
    dataset = pydicom.dcmread(input_path, stop_before_pixels=True)
    elements: list[DicomJsonElement] = []
    dicom_json: dict[str, dict[str, Any]] = {}

    for element in dataset.iterall():
        if element.keyword == "PixelData":
            continue
        item = _element_to_json(element, include_values=include_values)
        elements.append(item)
        dicom_json[item.tag] = {
            "vr": item.vr,
            "Keyword": item.keyword,
            "Name": item.name,
            "Risk": item.risk,
            "Category": item.category,
            "RecommendedAction": item.recommended_action,
            "Redacted": item.redacted,
            "Value": item.value,
        }

    return DicomJsonExportReport(
        input_path=str(input_path.resolve()),
        safe_mode=not include_values,
        include_values=include_values,
        total_elements=len(elements),
        redacted_elements=sum(1 for item in elements if item.redacted),
        high_risk_elements=sum(1 for item in elements if item.risk == "high"),
        medium_risk_elements=sum(1 for item in elements if item.risk == "medium"),
        unknown_risk_elements=sum(1 for item in elements if item.risk == "unknown"),
        dicom_json=dicom_json,
        elements=elements,
    )


def _element_to_json(element: DataElement, include_values: bool) -> DicomJsonElement:
    risk, reason, category, recommended_action, _dicom_action_code = classify_element(
        element
    )
    redacted = _should_redact(risk, include_values=include_values)
    return DicomJsonElement(
        tag=_json_tag(element),
        keyword=element.keyword or "",
        name=element.name,
        vr=element.VR,
        risk=risk,
        category=category,
        recommended_action=recommended_action,
        value=[REDACTED_VALUE] if redacted else _value_list(element.value),
        redacted=redacted,
        note=reason if not redacted else f"{reason}; value redacted in safe mode.",
    )


def _should_redact(risk: RiskLevel, include_values: bool) -> bool:
    if include_values:
        return False
    return risk in {"high", "medium", "unknown"}


def _value_list(value: Any) -> list[str]:
    text = value_to_text(value)
    if not text:
        return []
    return [text]


def _json_tag(element: DataElement) -> str:
    return f"{element.tag.group:04X}{element.tag.element:04X}"
