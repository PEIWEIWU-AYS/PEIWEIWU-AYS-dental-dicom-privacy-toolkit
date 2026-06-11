from __future__ import annotations

from pathlib import Path

from ddpt.models import (
    AuditChainVerification,
    DeidentificationComparisonReport,
    PackageVerificationReceipt,
    PixelReviewReport,
    ShareReadinessCheck,
    ShareReadinessReport,
    ValidationReport,
)


def run_share_readiness(root_dir: Path) -> ShareReadinessReport:
    root_dir = root_dir.resolve()
    checks = [
        _file_exists_check(
            root_dir,
            "outputs/sample.anonymized.dcm",
            "anonymized-dicom",
            "dicom",
            "Anonymized DICOM output is present.",
        ),
        _validation_check(root_dir),
        _deid_comparison_check(root_dir),
        _pixel_review_check(root_dir),
        _package_receipt_check(root_dir),
        _audit_chain_check(root_dir),
    ]
    return ShareReadinessReport(
        root_dir=str(root_dir),
        passed=all(check.passed for check in checks),
        checks=checks,
    )


def _validation_check(root_dir: Path) -> ShareReadinessCheck:
    path = root_dir / "reports" / "validation.json"
    report = _read_model(path, ValidationReport)
    if report is None:
        return _check(
            "validation",
            "privacy",
            False,
            "Validation report is missing or unreadable.",
            [str(path)],
        )
    return _check(
        "validation",
        "privacy",
        report.passed,
        "Anonymized DICOM validation passed."
        if report.passed
        else "Anonymized DICOM validation failed.",
        [str(path)],
    )


def _deid_comparison_check(root_dir: Path) -> ShareReadinessCheck:
    path = root_dir / "reports" / "deid-comparison.json"
    report = _read_model(path, DeidentificationComparisonReport)
    if report is None:
        return _check(
            "deid-comparison",
            "privacy",
            False,
            "Before/after de-identification comparison is missing or unreadable.",
            [str(path)],
        )
    passed = (
        report.passed
        and not report.residual_high_risk_keywords
        and not report.residual_medium_risk_keywords
        and report.private_tags_after == 0
    )
    return _check(
        "deid-comparison",
        "privacy",
        passed,
        "Before/after de-identification comparison passed."
        if passed
        else "Before/after de-identification comparison found residual risk.",
        [
            str(path),
            f"passed_items={report.passed_items}/{report.total_items}",
            f"private_tags_after={report.private_tags_after}",
        ],
    )


def _pixel_review_check(root_dir: Path) -> ShareReadinessCheck:
    path = root_dir / "reports" / "pixel-review.json"
    report = _read_model(path, PixelReviewReport)
    if report is None:
        return _check(
            "pixel-review",
            "pixel",
            False,
            "Pixel review report is missing or unreadable.",
            [str(path)],
        )
    preview_paths = [
        report.original_preview_png,
        report.overlay_preview_png,
        report.redacted_preview_png,
    ]
    missing = [preview for preview in preview_paths if not Path(preview).is_file()]
    passed = bool(report.regions) and not missing
    return _check(
        "pixel-review",
        "pixel",
        passed,
        "Pixel review previews and redaction regions are present."
        if passed
        else "Pixel review evidence is incomplete.",
        [str(path), f"regions={len(report.regions)}", *missing],
    )


def _package_receipt_check(root_dir: Path) -> ShareReadinessCheck:
    path = root_dir / "reports" / "package-receipt.json"
    report = _read_model(path, PackageVerificationReceipt)
    if report is None:
        return _check(
            "package-receipt",
            "sharing",
            False,
            "Package verification receipt is missing or unreadable.",
            [str(path)],
        )
    package_path = Path(report.package_path)
    passed = report.passed and report.encrypted is True and package_path.is_file()
    return _check(
        "package-receipt",
        "sharing",
        passed,
        "Encrypted package verification receipt passed."
        if passed
        else "Encrypted package verification receipt is incomplete or failed.",
        [
            str(path),
            f"package={report.package_path}",
            f"encrypted={report.encrypted}",
            f"entries={len(report.entries)}",
        ],
    )


def _audit_chain_check(root_dir: Path) -> ShareReadinessCheck:
    path = root_dir / "reports" / "audit-chain-verify.json"
    report = _read_model(path, AuditChainVerification)
    if report is None:
        return _check(
            "audit-chain",
            "audit",
            False,
            "Audit chain verification report is missing or unreadable.",
            [str(path)],
        )
    return _check(
        "audit-chain",
        "audit",
        report.passed,
        "Audit chain verification passed."
        if report.passed
        else "Audit chain verification failed.",
        [str(path), f"checked_files={report.checked_files}", *report.errors],
    )


def _file_exists_check(
    root_dir: Path,
    relative_path: str,
    check_id: str,
    category: str,
    passed_message: str,
) -> ShareReadinessCheck:
    path = root_dir / relative_path
    return _check(
        check_id,
        category,
        path.is_file(),
        passed_message if path.is_file() else f"Missing required file: {relative_path}",
        [str(path)],
    )


def _read_model(path: Path, model_type):
    if not path.is_file():
        return None
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _check(
    check_id: str,
    category: str,
    passed: bool,
    message: str,
    evidence: list[str],
) -> ShareReadinessCheck:
    return ShareReadinessCheck(
        id=check_id,
        category=category,
        passed=passed,
        message=message,
        evidence=evidence,
    )
