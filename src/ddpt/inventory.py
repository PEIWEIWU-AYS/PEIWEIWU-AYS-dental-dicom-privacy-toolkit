from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

import pydicom
from pydicom.dataset import FileDataset

from ddpt.batch import find_dicom_files
from ddpt.models import InventoryFileRecord, InventoryReport
from ddpt.policy import classify_element
from ddpt.utils import ensure_parent, sha256_file, value_to_text

CSV_FIELDS = [
    "path",
    "readable",
    "error",
    "file_sha256",
    "modality",
    "sop_class_uid",
    "study_instance_uid_hash",
    "series_instance_uid_hash",
    "sop_instance_uid_hash",
    "patient_name_present",
    "patient_id_present",
    "patient_birth_date_present",
    "burned_in_annotation",
    "rows",
    "columns",
    "transfer_syntax_uid",
    "high_risk_tags",
    "medium_risk_tags",
    "low_risk_tags",
    "unknown_risk_tags",
    "recommended_actions",
    "high_risk_keywords",
]


def build_inventory(
    input_dir: Path,
    recursive: bool = True,
    include_hash: bool = True,
) -> InventoryReport:
    files = find_dicom_files(input_dir, recursive=recursive)
    records = [
        _record_for_path(path, input_dir, include_hash=include_hash) for path in files
    ]
    readable_records = [record for record in records if record.readable]
    modalities = Counter(record.modality or "unknown" for record in readable_records)

    return InventoryReport(
        root_dir=str(input_dir),
        recursive=recursive,
        total_files=len(records),
        readable_files=len(readable_records),
        unreadable_files=len(records) - len(readable_records),
        high_risk_tags=sum(record.high_risk_tags for record in records),
        medium_risk_tags=sum(record.medium_risk_tags for record in records),
        modalities=dict(sorted(modalities.items())),
        files=records,
    )


def write_inventory_csv(path: Path, report: InventoryReport) -> None:
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for record in report.files:
            row = record.model_dump(mode="json")
            row["recommended_actions"] = ";".join(record.recommended_actions)
            row["high_risk_keywords"] = ";".join(record.high_risk_keywords)
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def _record_for_path(path: Path, root_dir: Path, include_hash: bool) -> InventoryFileRecord:
    try:
        dataset = pydicom.dcmread(path, stop_before_pixels=True)
    except Exception as exc:
        return InventoryFileRecord(
            path=_relative_text(path, root_dir),
            readable=False,
            error=str(exc),
            file_sha256=sha256_file(path) if include_hash else None,
        )

    risk_counts, recommended_actions, high_risk_keywords = _risk_summary(dataset)
    return InventoryFileRecord(
        path=_relative_text(path, root_dir),
        readable=True,
        file_sha256=sha256_file(path) if include_hash else None,
        modality=value_to_text(dataset.get("Modality", "")) or None,
        sop_class_uid=value_to_text(dataset.get("SOPClassUID", "")) or None,
        study_instance_uid_hash=_hash_value(dataset.get("StudyInstanceUID")),
        series_instance_uid_hash=_hash_value(dataset.get("SeriesInstanceUID")),
        sop_instance_uid_hash=_hash_value(dataset.get("SOPInstanceUID")),
        patient_name_present=bool(dataset.get("PatientName")),
        patient_id_present=bool(dataset.get("PatientID")),
        patient_birth_date_present=bool(dataset.get("PatientBirthDate")),
        burned_in_annotation=value_to_text(dataset.get("BurnedInAnnotation", "")) or None,
        rows=_int_or_none(dataset.get("Rows")),
        columns=_int_or_none(dataset.get("Columns")),
        transfer_syntax_uid=value_to_text(
            getattr(dataset.file_meta, "TransferSyntaxUID", "")
        )
        or None,
        high_risk_tags=risk_counts["high"],
        medium_risk_tags=risk_counts["medium"],
        low_risk_tags=risk_counts["low"],
        unknown_risk_tags=risk_counts["unknown"],
        recommended_actions=recommended_actions,
        high_risk_keywords=high_risk_keywords,
    )


def _risk_summary(dataset: FileDataset) -> tuple[Counter[str], list[str], list[str]]:
    risk_counts: Counter[str] = Counter()
    recommended_actions: set[str] = set()
    high_risk_keywords: set[str] = set()

    for element in dataset.iterall():
        if element.keyword == "PixelData":
            continue
        risk, _reason, _category, recommended_action, _dicom_action_code = (
            classify_element(element)
        )
        risk_counts[risk] += 1
        if recommended_action != "review":
            recommended_actions.add(recommended_action)
        if risk == "high" and element.keyword:
            high_risk_keywords.add(element.keyword)

    return (
        risk_counts,
        sorted(recommended_actions),
        sorted(high_risk_keywords),
    )


def _hash_value(value: object) -> str | None:
    text = value_to_text(value)
    if not text:
        return None
    return hashlib.sha256(f"ddpt-inventory:{text}".encode()).hexdigest()[:16]


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _relative_text(path: Path, root_dir: Path) -> str:
    try:
        return str(path.relative_to(root_dir))
    except ValueError:
        return str(path)
