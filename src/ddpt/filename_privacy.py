from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from ddpt.batch import find_dicom_files
from ddpt.models import (
    FilenamePrivacyFileResult,
    FilenamePrivacyFinding,
    FilenamePrivacyScanReport,
)

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?\d[\s._-]?){8,}")
DATE_RE = re.compile(
    r"(?<!\d)(?:19|20)\d{2}[\s._-]?(?:0[1-9]|1[0-2])[\s._-]?(?:0[1-9]|[12]\d|3[01])(?!\d)"
)
PATIENT_ID_RE = re.compile(r"\b(?:patient|pt|mrn|id|case)[\s._-]*\d{3,}\b", re.IGNORECASE)
CHINESE_PATIENT_MARKERS = ("患者", "病人", "病例", "姓名", "身份证", "手机号")
SAFE_HINTS = ("synthetic", "anonymized", "redacted", "demo", "sample", "ddpt")


def scan_filename_privacy(
    input_path: Path,
    recursive: bool = True,
) -> FilenamePrivacyScanReport:
    input_path = input_path.resolve()
    files = _input_files(input_path, recursive=recursive)
    results = [
        _file_result(path, input_path, index=index)
        for index, path in enumerate(files, start=1)
    ]
    findings = [finding for result in results for finding in result.findings]
    high = sum(1 for finding in findings if finding.severity == "high")
    medium = sum(1 for finding in findings if finding.severity == "medium")
    return FilenamePrivacyScanReport(
        input_path=str(input_path),
        recursive=recursive,
        passed=high == 0 and medium == 0,
        scanned_files=len(results),
        findings_count=len(findings),
        high_findings=high,
        medium_findings=medium,
        files=results,
    )


def _input_files(input_path: Path, recursive: bool) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return find_dicom_files(input_path, recursive=recursive)
    return []


def _file_result(path: Path, input_root: Path, index: int) -> FilenamePrivacyFileResult:
    relative = _relative_text(path, input_root)
    suggested = f"ddpt-file-{index:04d}{path.suffix.lower() or '.dcm'}"
    findings: list[FilenamePrivacyFinding] = []
    for part in _privacy_relevant_parts(path, input_root):
        findings.extend(_findings_for_part(relative, part, suggested))
    return FilenamePrivacyFileResult(
        path=relative,
        suggested_safe_name=suggested,
        findings=findings,
    )


def _privacy_relevant_parts(path: Path, input_root: Path) -> tuple[str, ...]:
    root = input_root if input_root.is_dir() else input_root.parent
    try:
        return path.relative_to(root).parts
    except ValueError:
        return (path.name,)


def _findings_for_part(
    relative: str,
    part: str,
    suggested: str,
) -> list[FilenamePrivacyFinding]:
    if _looks_safe(part):
        return []
    findings: list[FilenamePrivacyFinding] = []
    normalized = part.lower()
    if EMAIL_RE.search(part):
        findings.append(
            _finding(
                relative,
                part,
                "high",
                "email-in-path",
                "Path contains an email-like token.",
                suggested,
            )
        )
    if PHONE_RE.search(part):
        findings.append(
            _finding(
                relative,
                part,
                "high",
                "phone-in-path",
                "Path contains a phone-like number.",
                suggested,
            )
        )
    if any(marker in part for marker in CHINESE_PATIENT_MARKERS):
        findings.append(
            _finding(
                relative,
                part,
                "high",
                "patient-marker-in-path",
                "Path contains a Chinese patient or case marker.",
                suggested,
            )
        )
    if PATIENT_ID_RE.search(part):
        findings.append(
            _finding(
                relative,
                part,
                "medium",
                "patient-id-in-path",
                "Path contains a patient/case/MRN-like identifier.",
                suggested,
            )
        )
    if DATE_RE.search(part):
        findings.append(
            _finding(
                relative,
                part,
                "medium",
                "date-in-path",
                "Path contains a date-like token that can aid linkage.",
                suggested,
            )
        )
    if normalized in {"private", "real-data", "raw-dicom", "patient-data"}:
        findings.append(
            _finding(
                relative,
                part,
                "high",
                "private-folder-marker",
                "Path contains a private-data folder marker.",
                suggested,
            )
        )
    return findings


def _looks_safe(part: str) -> bool:
    normalized = part.lower()
    return any(hint in normalized for hint in SAFE_HINTS)


def _finding(
    relative: str,
    part: str,
    severity: Literal["high", "medium", "low"],
    rule_id: str,
    message: str,
    suggested: str,
) -> FilenamePrivacyFinding:
    return FilenamePrivacyFinding(
        path=relative,
        part=part,
        severity=severity,
        rule_id=rule_id,
        message=message,
        suggested_safe_name=suggested,
    )


def _relative_text(path: Path, input_root: Path) -> str:
    root = input_root if input_root.is_dir() else input_root.parent
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
