from __future__ import annotations

from pathlib import Path

from ddpt.models import SafetyFinding, SafetyScanReport

EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "evidence-run",
    "node_modules",
    "outputs",
    "reports",
    "restored",
    "share",
    "venv",
    "workflow-run",
}

FORBIDDEN_PATH_PARTS = {
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

FORBIDDEN_EXTENSIONS = {
    ".csv": "spreadsheet exports can contain clinic or patient data",
    ".dcm": "DICOM files are blocked unless they are clearly synthetic examples",
    ".dicom": "DICOM files are blocked unless they are clearly synthetic examples",
    ".ddpt": "sharing packages are generated artifacts and may contain DICOM files",
    ".doc": "Word documents can contain private clinical or manuscript material",
    ".docx": "Word documents can contain private clinical or manuscript material",
    ".heic": "clinical photos or radiographs must not be committed",
    ".jpeg": "clinical photos or radiographs must not be committed",
    ".jpg": "clinical photos or radiographs must not be committed",
    ".pdf": "PDFs can contain consent forms, reports, or manuscript drafts",
    ".png": "image files can contain radiographs, photos, or screenshots with PHI",
    ".tif": "clinical photos or radiographs must not be committed",
    ".tiff": "clinical photos or radiographs must not be committed",
    ".xls": "spreadsheet exports can contain clinic or patient data",
    ".xlsx": "spreadsheet exports can contain clinic or patient data",
    ".zip": "archives can hide private clinical material",
}

SECRET_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.test",
}

SECRET_EXTENSIONS = {
    ".key",
    ".p12",
    ".pem",
    ".pfx",
}


def scan_repository_safety(root_dir: Path) -> SafetyScanReport:
    files = _public_files(root_dir)
    findings: list[SafetyFinding] = []

    for path in files:
        relative = _relative_text(path, root_dir)
        findings.extend(_path_part_findings(path, root_dir, relative))
        findings.extend(_file_type_findings(path, root_dir, relative))

    return SafetyScanReport(
        root_dir=str(root_dir),
        passed=len(findings) == 0,
        scanned_files=len(files),
        findings=findings,
    )


def _public_files(root_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in root_dir.rglob("*")
        if path.is_file() and not _is_excluded(path, root_dir)
    )


def _is_excluded(path: Path, root_dir: Path) -> bool:
    relative_parts = _relative_parts(path, root_dir)
    for part in relative_parts[:-1]:
        if part in EXCLUDED_DIR_NAMES:
            return True
        if part.startswith("demo-"):
            return True
        if part.startswith("evidence-"):
            return True
        if part.startswith("workflow-"):
            return True
    return False


def _path_part_findings(path: Path, root_dir: Path, relative: str) -> list[SafetyFinding]:
    findings: list[SafetyFinding] = []
    for part in _relative_parts(path, root_dir):
        normalized = part.lower()
        if normalized in FORBIDDEN_PATH_PARTS:
            findings.append(
                SafetyFinding(
                    path=relative,
                    severity="high",
                    rule_id="forbidden-path-part",
                    message=f"Path contains private clinical directory marker: {part}",
                )
            )
    return findings


def _file_type_findings(path: Path, root_dir: Path, relative: str) -> list[SafetyFinding]:
    if _is_allowed_synthetic_dicom(path, root_dir):
        return []

    findings: list[SafetyFinding] = []
    suffix = path.suffix.lower()
    if path.name in SECRET_FILENAMES:
        findings.append(
            SafetyFinding(
                path=relative,
                severity="high",
                rule_id="secret-file",
                message="Environment files must not be committed to a public repository.",
            )
        )
    if suffix in SECRET_EXTENSIONS:
        findings.append(
            SafetyFinding(
                path=relative,
                severity="high",
                rule_id="secret-extension",
                message="Key or certificate files must not be committed.",
            )
        )
    if suffix in FORBIDDEN_EXTENSIONS:
        findings.append(
            SafetyFinding(
                path=relative,
                severity="high",
                rule_id="forbidden-extension",
                message=FORBIDDEN_EXTENSIONS[suffix],
            )
        )
    return findings


def _is_allowed_synthetic_dicom(path: Path, root_dir: Path) -> bool:
    suffix = path.suffix.lower()
    if suffix not in {".dcm", ".dicom"}:
        return False

    parts = _relative_parts(path, root_dir)
    in_examples = len(parts) >= 3 and parts[0] == "examples" and parts[1] == "synthetic-dicom"
    return in_examples and "synthetic" in path.name.lower()


def _relative_text(path: Path, root_dir: Path) -> str:
    return "/".join(_relative_parts(path, root_dir))


def _relative_parts(path: Path, root_dir: Path) -> tuple[str, ...]:
    try:
        return path.relative_to(root_dir).parts
    except ValueError:
        return path.parts
