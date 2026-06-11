from __future__ import annotations

import re
import zipfile
from collections import Counter
from io import BytesIO
from pathlib import Path

import pydicom
from pydicom.dataset import FileDataset

from ddpt.batch import DICOM_SUFFIXES
from ddpt.models import ClinicExportIntakeReport, IntakeFileRecord, IntakeFinding
from ddpt.policy import classify_element
from ddpt.utils import value_to_text

SIDECAR_EXTENSIONS = {
    ".csv": "spreadsheet export can contain patient lists, appointment IDs, or billing data",
    ".doc": "document can contain reports, consent forms, or private notes",
    ".docx": "document can contain reports, consent forms, or private notes",
    ".heic": "photo or radiograph export can contain patient identifiers",
    ".jpeg": "photo or radiograph export can contain patient identifiers",
    ".jpg": "photo or radiograph export can contain patient identifiers",
    ".pdf": "PDF can contain reports, consent forms, or patient identifiers",
    ".png": "image export or screenshot can contain patient identifiers",
    ".tif": "image export can contain patient identifiers",
    ".tiff": "image export can contain patient identifiers",
    ".xls": "spreadsheet export can contain patient lists, appointment IDs, or billing data",
    ".xlsx": "spreadsheet export can contain patient lists, appointment IDs, or billing data",
}

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?\d[\s._-]?){8,}")
DATE_RE = re.compile(
    r"(?<!\d)(?:19|20)\d{2}[\s._-]?(?:0[1-9]|1[0-2])[\s._-]?(?:0[1-9]|[12]\d|3[01])(?!\d)"
)
PATIENT_ID_RE = re.compile(r"\b(?:patient|pt|mrn|id|case)[\s._-]*\d{3,}\b", re.IGNORECASE)
CHINESE_PATIENT_MARKERS = ("患者", "病人", "病例", "姓名", "身份证", "手机号")
PRIVATE_DIR_MARKERS = {
    "clinical-data",
    "clinic-exports",
    "dicom-private",
    "patient-data",
    "private",
    "raw-dicom",
    "real-data",
    "病例",
    "患者",
    "真实病例",
}

BOUNDARY_NOTES = [
    "Read-only intake triage; no files are anonymized, modified, extracted, or uploaded.",
    "ZIP archives are inspected in place. Members are not extracted to disk.",
    "DICOMDIR can contain patient/study directory records and should be treated as PHI.",
    "A failed intake report means action is required before public sharing or GitHub upload.",
]


def triage_clinic_export(
    input_path: Path,
    recursive: bool = True,
    max_archive_member_bytes: int = 16 * 1024 * 1024,
) -> ClinicExportIntakeReport:
    input_path = input_path.resolve()
    if not input_path.exists():
        return ClinicExportIntakeReport(
            input_path=str(input_path),
            input_type="missing",
            recursive=recursive,
            passed=False,
            total_files=0,
            dicom_files=0,
            dicomdir_files=0,
            sidecar_files=0,
            archive_risk_files=0,
            unknown_files=0,
            high_findings=1,
            medium_findings=0,
            files=[
                IntakeFileRecord(
                    path=str(input_path),
                    source="filesystem",
                    kind="archive-risk",
                    size_bytes=0,
                    findings=[
                        _finding(
                            str(input_path),
                            "high",
                            "input",
                            "missing-input",
                            "Input path does not exist.",
                            "Choose an existing clinic export folder, DICOM file, or ZIP archive.",
                        )
                    ],
                )
            ],
            next_steps=["Choose an existing local path and run intake triage again."],
            boundary_notes=BOUNDARY_NOTES,
        )

    if input_path.is_dir():
        records = _directory_records(input_path, recursive=recursive)
        input_type = "directory"
    elif input_path.is_file() and input_path.suffix.lower() == ".zip":
        records = _zip_records(input_path, max_member_bytes=max_archive_member_bytes)
        input_type = "zip"
    elif input_path.is_file():
        records = [_filesystem_record(input_path, input_path.parent)]
        input_type = "file"
    else:
        records = []
        input_type = "missing"

    findings = [finding for record in records for finding in record.findings]
    high = sum(1 for finding in findings if finding.severity == "high")
    medium = sum(1 for finding in findings if finding.severity == "medium")
    counts = Counter(record.kind for record in records)
    return ClinicExportIntakeReport(
        input_path=str(input_path),
        input_type=input_type,
        recursive=recursive,
        passed=high == 0 and medium == 0,
        total_files=len(records),
        dicom_files=counts["dicom"],
        dicomdir_files=counts["dicomdir"],
        sidecar_files=counts["sidecar"],
        archive_risk_files=counts["archive-risk"],
        unknown_files=counts["unknown"],
        high_findings=high,
        medium_findings=medium,
        files=records,
        next_steps=_next_steps(records, high, medium),
        boundary_notes=BOUNDARY_NOTES,
    )


def _directory_records(root: Path, recursive: bool) -> list[IntakeFileRecord]:
    iterator = root.rglob("*") if recursive else root.glob("*")
    return [
        _filesystem_record(path, root)
        for path in sorted(iterator)
        if path.is_file()
    ]


def _filesystem_record(path: Path, root: Path) -> IntakeFileRecord:
    relative = _relative_text(path, root)
    common_findings = _path_findings(relative)
    size_bytes = path.stat().st_size
    if _is_dicomdir_name(path.name):
        return _dicom_record(
            relative,
            size_bytes,
            "filesystem",
            _read_dicom_from_path(path),
            kind="dicomdir",
            base_findings=common_findings,
        )
    if path.suffix.lower() in DICOM_SUFFIXES:
        return _dicom_record(
            relative,
            size_bytes,
            "filesystem",
            _read_dicom_from_path(path),
            kind="dicom",
            base_findings=common_findings,
        )
    if path.suffix.lower() == ".zip":
        return IntakeFileRecord(
            path=relative,
            source="filesystem",
            kind="archive-risk",
            size_bytes=size_bytes,
            findings=[
                *common_findings,
                _finding(
                    relative,
                    "medium",
                    "archive",
                    "nested-archive",
                    "Nested archive found inside the clinic export.",
                    "Run intake triage on the archive separately before using its contents.",
                ),
            ],
        )
    return _sidecar_or_unknown(relative, size_bytes, "filesystem", common_findings)


def _zip_records(path: Path, max_member_bytes: int) -> list[IntakeFileRecord]:
    try:
        with zipfile.ZipFile(path) as archive:
            records = []
            for member in archive.infolist():
                if member.is_dir():
                    continue
                records.append(_zip_member_record(archive, member, max_member_bytes))
            return records
    except zipfile.BadZipFile:
        return [
            IntakeFileRecord(
                path=path.name,
                source="filesystem",
                kind="archive-risk",
                size_bytes=path.stat().st_size,
                findings=[
                    _finding(
                        path.name,
                        "high",
                        "archive",
                        "invalid-zip",
                        "ZIP archive could not be opened.",
                        "Do not process this archive until it is replaced or repaired.",
                    )
                ],
            )
        ]


def _zip_member_record(
    archive: zipfile.ZipFile,
    member: zipfile.ZipInfo,
    max_member_bytes: int,
) -> IntakeFileRecord:
    member_path = member.filename
    findings = _archive_path_findings(member_path) + _path_findings(member_path)
    size_bytes = int(member.file_size)
    if _is_dicomdir_name(Path(member_path).name):
        dataset = _read_dicom_from_zip(archive, member, max_member_bytes)
        return _dicom_record(
            member_path,
            size_bytes,
            "archive",
            dataset,
            kind="dicomdir",
            base_findings=findings,
        )
    if Path(member_path).suffix.lower() in DICOM_SUFFIXES:
        dataset = _read_dicom_from_zip(archive, member, max_member_bytes)
        return _dicom_record(
            member_path,
            size_bytes,
            "archive",
            dataset,
            kind="dicom",
            base_findings=findings,
        )
    return _sidecar_or_unknown(member_path, size_bytes, "archive", findings)


def _dicom_record(
    path: str,
    size_bytes: int,
    source: str,
    dataset: FileDataset | Exception | None,
    kind: str,
    base_findings: list[IntakeFinding],
) -> IntakeFileRecord:
    findings = list(base_findings)
    if isinstance(dataset, Exception) or dataset is None:
        findings.append(
            _finding(
                path,
                "high",
                "dicom",
                "unreadable-dicom",
                "File has a DICOM-like role but could not be read as DICOM metadata.",
                "Quarantine this file and review it before de-identification.",
            )
        )
        return IntakeFileRecord(
            path=path,
            source=source,  # type: ignore[arg-type]
            kind=kind,  # type: ignore[arg-type]
            size_bytes=size_bytes,
            readable_dicom=False,
            findings=findings,
        )

    risk_counts, patient_findings = _dicom_findings(path, dataset, kind)
    findings.extend(patient_findings)
    return IntakeFileRecord(
        path=path,
        source=source,  # type: ignore[arg-type]
        kind=kind,  # type: ignore[arg-type]
        size_bytes=size_bytes,
        readable_dicom=True,
        modality=value_to_text(dataset.get("Modality", "")) or None,
        patient_name_present=bool(dataset.get("PatientName")),
        patient_id_present=bool(dataset.get("PatientID")),
        high_risk_tags=risk_counts["high"],
        medium_risk_tags=risk_counts["medium"],
        findings=findings,
    )


def _dicom_findings(
    path: str,
    dataset: FileDataset,
    kind: str,
) -> tuple[Counter[str], list[IntakeFinding]]:
    risk_counts: Counter[str] = Counter()
    high_keywords: set[str] = set()
    medium_keywords: set[str] = set()

    for element in dataset.iterall():
        if element.keyword == "PixelData":
            continue
        risk, _reason, _category, _action, _code = classify_element(element)
        risk_counts[risk] += 1
        if risk == "high" and element.keyword:
            high_keywords.add(element.keyword)
        if risk == "medium" and element.keyword:
            medium_keywords.add(element.keyword)

    findings: list[IntakeFinding] = []
    if high_keywords:
        high_text = ", ".join(sorted(high_keywords))
        findings.append(
            _finding(
                path,
                "high",
                "dicom-metadata",
                f"{kind}-direct-identifiers",
                f"DICOM metadata contains high-risk identifiers: {high_text}.",
                "Run DDPT de-identification and validation before sharing.",
            )
        )
    if medium_keywords:
        medium_text = ", ".join(sorted(medium_keywords)[:8])
        findings.append(
            _finding(
                path,
                "medium",
                "dicom-metadata",
                f"{kind}-linkage-identifiers",
                f"DICOM metadata contains linkage identifiers: {medium_text}.",
                "Review dates, UIDs, institution, device, and workflow identifiers.",
            )
        )
    if kind == "dicomdir":
        findings.append(
            _finding(
                path,
                "high",
                "dicomdir",
                "dicomdir-present",
                "DICOMDIR is present and can contain patient/study directory records.",
                "Treat DICOMDIR as PHI and regenerate or exclude it after de-identification.",
            )
        )
    return risk_counts, findings


def _sidecar_or_unknown(
    path: str,
    size_bytes: int,
    source: str,
    base_findings: list[IntakeFinding],
) -> IntakeFileRecord:
    suffix = Path(path).suffix.lower()
    findings = list(base_findings)
    if suffix in SIDECAR_EXTENSIONS:
        findings.append(
            _finding(
                path,
                "high",
                "sidecar",
                "sidecar-private-file",
                SIDECAR_EXTENSIONS[suffix],
                (
                    "Remove sidecar files before DICOM anonymization or handle "
                    "them in a separate private workflow."
                ),
            )
        )
        kind = "sidecar"
    else:
        findings.append(
            _finding(
                path,
                "low",
                "unknown",
                "unknown-file-type",
                "File is not recognized as DICOM, DICOMDIR, or a known sidecar type.",
                "Review whether this file belongs in the DICOM privacy workflow.",
            )
        )
        kind = "unknown"
    return IntakeFileRecord(
        path=path,
        source=source,  # type: ignore[arg-type]
        kind=kind,  # type: ignore[arg-type]
        size_bytes=size_bytes,
        findings=findings,
    )


def _path_findings(path: str) -> list[IntakeFinding]:
    findings: list[IntakeFinding] = []
    parts = Path(path).parts
    for part in parts:
        normalized = part.lower()
        if EMAIL_RE.search(part):
            findings.append(
                _finding(
                    path,
                    "high",
                    "path",
                    "email-in-path",
                    "Path contains an email-like token.",
                    "Rename export folders and files before sharing.",
                )
            )
        if PHONE_RE.search(part):
            findings.append(
                _finding(
                    path,
                    "high",
                    "path",
                    "phone-in-path",
                    "Path contains a phone-like number.",
                    "Rename export folders and files before sharing.",
                )
            )
        if any(marker in part for marker in CHINESE_PATIENT_MARKERS):
            findings.append(
                _finding(
                    path,
                    "high",
                    "path",
                    "patient-marker-in-path",
                    "Path contains a Chinese patient or case marker.",
                    "Rename export folders and files before sharing.",
                )
            )
        if PATIENT_ID_RE.search(part):
            findings.append(
                _finding(
                    path,
                    "medium",
                    "path",
                    "patient-id-in-path",
                    "Path contains a patient/case/MRN-like identifier.",
                    "Rename export folders and files before sharing.",
                )
            )
        if DATE_RE.search(part):
            findings.append(
                _finding(
                    path,
                    "medium",
                    "path",
                    "date-in-path",
                    "Path contains a date-like token that can aid linkage.",
                    "Use neutral export folder names for shared packages.",
                )
            )
        if normalized in PRIVATE_DIR_MARKERS:
            findings.append(
                _finding(
                    path,
                    "high",
                    "path",
                    "private-folder-marker",
                    "Path contains a private clinical export marker.",
                    "Keep raw clinic exports outside public repositories and shared packages.",
                )
            )
    return findings


def _archive_path_findings(path: str) -> list[IntakeFinding]:
    pure = Path(path)
    unsafe = path.startswith("/") or ".." in pure.parts
    if not unsafe:
        return []
    return [
        _finding(
            path,
            "high",
            "archive",
            "unsafe-archive-path",
            "Archive member uses an absolute or parent-directory path.",
            "Reject the archive; do not extract it.",
        )
    ]


def _read_dicom_from_path(path: Path) -> FileDataset | Exception:
    try:
        return pydicom.dcmread(path, stop_before_pixels=True)
    except Exception as exc:
        return exc


def _read_dicom_from_zip(
    archive: zipfile.ZipFile,
    member: zipfile.ZipInfo,
    max_member_bytes: int,
) -> FileDataset | Exception:
    if member.file_size > max_member_bytes:
        return ValueError("archive member is too large for intake metadata read")
    try:
        with archive.open(member) as handle:
            data = handle.read(max_member_bytes + 1)
        return pydicom.dcmread(BytesIO(data), stop_before_pixels=True)
    except Exception as exc:
        return exc


def _next_steps(
    records: list[IntakeFileRecord],
    high_findings: int,
    medium_findings: int,
) -> list[str]:
    if not records:
        return ["No files were found. Choose a clinic export folder, DICOM file, or ZIP archive."]
    steps: list[str] = []
    if any(record.kind == "archive-risk" for record in records):
        steps.append("Reject or separately review unsafe/nested archives before extraction.")
    if any(record.kind == "sidecar" for record in records):
        steps.append("Move PDFs, spreadsheets, photos, and screenshots into a private workflow.")
    if any(record.kind == "dicomdir" for record in records):
        steps.append("Treat DICOMDIR as PHI; regenerate or exclude it after de-identification.")
    if any(record.kind == "dicom" for record in records):
        steps.append(
            "Run filename scan, remediation plan, anonymization, validation, and comparison."
        )
    if high_findings or medium_findings:
        steps.append("Do not publish or push this export until findings are resolved.")
    if not steps:
        steps.append(
            "No blocking intake findings were detected; continue with normal DDPT workflow."
        )
    return steps


def _finding(
    path: str,
    severity: str,
    category: str,
    rule_id: str,
    message: str,
    recommended_action: str,
) -> IntakeFinding:
    return IntakeFinding(
        path=path,
        severity=severity,  # type: ignore[arg-type]
        category=category,
        rule_id=rule_id,
        message=message,
        recommended_action=recommended_action,
    )


def _is_dicomdir_name(name: str) -> bool:
    return name.upper() == "DICOMDIR"


def _relative_text(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
