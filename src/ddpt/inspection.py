from __future__ import annotations

from pathlib import Path

import pydicom
from pydicom.dataelem import DataElement

from ddpt.models import InspectionReport, TagFinding
from ddpt.risk import classify_element
from ddpt.utils import value_to_text


def inspect_dicom(path: Path) -> InspectionReport:
    dataset = pydicom.dcmread(path)
    findings: list[TagFinding] = []

    for element in dataset.iterall():
        if element.keyword == "PixelData":
            continue
        findings.append(_finding_from_element(element))

    return InspectionReport(
        file_path=str(path),
        sop_class_uid=value_to_text(dataset.get("SOPClassUID", "")) or None,
        modality=value_to_text(dataset.get("Modality", "")) or None,
        patient_id_present=bool(dataset.get("PatientID")),
        patient_name_present=bool(dataset.get("PatientName")),
        findings=findings,
    )


def _finding_from_element(element: DataElement) -> TagFinding:
    risk, reason = classify_element(element)
    keyword = element.keyword or ""
    return TagFinding(
        tag=str(element.tag),
        keyword=keyword,
        name=element.name,
        vr=element.VR,
        value=value_to_text(element.value),
        risk=risk,
        reason=reason,
    )
