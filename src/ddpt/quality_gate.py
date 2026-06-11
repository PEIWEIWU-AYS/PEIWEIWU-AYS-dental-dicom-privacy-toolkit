from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from ddpt.models import (
    AuditChainVerification,
    DeidentificationCertificate,
    DeidentificationComparisonReport,
    PackageVerificationReceipt,
    PixelReviewReport,
    ShareReadinessReport,
    ValidationReport,
    WorkflowQualityGateCheck,
    WorkflowQualityGateReport,
    WorkflowRunReport,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def run_workflow_quality_gate(
    root_dir: Path,
    workflow_report_path: Path | None = None,
) -> WorkflowQualityGateReport:
    root_dir = root_dir.resolve()
    workflow_report_path = _locate_workflow_report(root_dir, workflow_report_path)
    checks = [
        _artifact_check(root_dir, "input/sample.synthetic.dcm", "source-dicom", "source"),
        _artifact_check(
            root_dir,
            "outputs/sample.anonymized.dcm",
            "anonymized-dicom",
            "de-identification",
        ),
        _artifact_check(
            root_dir,
            "outputs/sample.redacted.dcm",
            "pixel-redacted-dicom",
            "pixel",
        ),
        _validation_check(root_dir),
        _deid_comparison_check(root_dir),
        _pixel_review_check(root_dir),
        _package_receipt_check(root_dir),
        _audit_chain_check(root_dir),
        _share_readiness_check(root_dir),
        _certificate_check(root_dir),
        _workflow_report_check(workflow_report_path),
    ]
    required_checks = [check for check in checks if check.required]
    failed_checks = [check for check in required_checks if not check.passed]
    return WorkflowQualityGateReport(
        root_dir=str(root_dir),
        passed=not failed_checks,
        workflow_report_path=str(workflow_report_path) if workflow_report_path else None,
        required_checks=len(required_checks),
        passed_checks=len(required_checks) - len(failed_checks),
        failed_checks=len(failed_checks),
        checks=checks,
    )


def _artifact_check(
    root_dir: Path,
    relative_path: str,
    check_id: str,
    stage: str,
) -> WorkflowQualityGateCheck:
    path = root_dir / relative_path
    return _check(
        check_id,
        stage,
        True,
        path.is_file(),
        f"Required artifact is present: {relative_path}"
        if path.is_file()
        else f"Missing required artifact: {relative_path}",
        [str(path)],
    )


def _validation_check(root_dir: Path) -> WorkflowQualityGateCheck:
    path = root_dir / "reports" / "validation.json"
    report = _read_model(path, ValidationReport)
    if report is None:
        return _check(
            "validation-report",
            "de-identification",
            True,
            False,
            "Validation report is missing or unreadable.",
            [str(path)],
        )
    return _check(
        "validation-report",
        "de-identification",
        True,
        report.passed,
        "Anonymized DICOM validation passed."
        if report.passed
        else "Anonymized DICOM validation failed.",
        [str(path), f"checks={len(report.checks)}", f"warnings={len(report.warnings)}"],
    )


def _deid_comparison_check(root_dir: Path) -> WorkflowQualityGateCheck:
    path = root_dir / "reports" / "deid-comparison.json"
    report = _read_model(path, DeidentificationComparisonReport)
    if report is None:
        return _check(
            "deid-comparison-report",
            "de-identification",
            True,
            False,
            "Before/after de-identification comparison is missing or unreadable.",
            [str(path)],
        )
    passed = (
        report.passed
        and report.private_tags_after == 0
        and not report.residual_high_risk_keywords
        and not report.residual_medium_risk_keywords
    )
    return _check(
        "deid-comparison-report",
        "de-identification",
        True,
        passed,
        "Before/after de-identification comparison passed."
        if passed
        else "Before/after de-identification comparison found residual risk.",
        [
            str(path),
            f"passed_items={report.passed_items}/{report.total_items}",
            f"private_tags_after={report.private_tags_after}",
            f"residual_high={len(report.residual_high_risk_keywords)}",
            f"residual_medium={len(report.residual_medium_risk_keywords)}",
        ],
    )


def _pixel_review_check(root_dir: Path) -> WorkflowQualityGateCheck:
    path = root_dir / "reports" / "pixel-review.json"
    report = _read_model(path, PixelReviewReport)
    if report is None:
        return _check(
            "pixel-review-report",
            "pixel",
            True,
            False,
            "Pixel review report is missing or unreadable.",
            [str(path)],
        )
    preview_paths = [
        Path(report.original_preview_png),
        Path(report.overlay_preview_png),
        Path(report.redacted_preview_png),
    ]
    missing = [str(path) for path in preview_paths if not path.is_file()]
    passed = bool(report.regions) and not missing
    return _check(
        "pixel-review-report",
        "pixel",
        True,
        passed,
        "Pixel review regions and PNG previews are present."
        if passed
        else "Pixel review evidence is incomplete.",
        [str(path), f"regions={len(report.regions)}", *missing],
    )


def _package_receipt_check(root_dir: Path) -> WorkflowQualityGateCheck:
    path = root_dir / "reports" / "package-receipt.json"
    report = _read_model(path, PackageVerificationReceipt)
    if report is None:
        return _check(
            "package-receipt",
            "sharing",
            True,
            False,
            "Package verification receipt is missing or unreadable.",
            [str(path)],
        )
    package_path = Path(report.package_path)
    passed = (
        report.passed
        and report.encrypted is True
        and package_path.is_file()
        and len(report.entries) > 0
    )
    return _check(
        "package-receipt",
        "sharing",
        True,
        passed,
        "Encrypted package receipt passed and has entries."
        if passed
        else "Encrypted package receipt is incomplete or failed.",
        [
            str(path),
            f"package={report.package_path}",
            f"encrypted={report.encrypted}",
            f"entries={len(report.entries)}",
        ],
    )


def _audit_chain_check(root_dir: Path) -> WorkflowQualityGateCheck:
    path = root_dir / "reports" / "audit-chain-verify.json"
    report = _read_model(path, AuditChainVerification)
    if report is None:
        return _check(
            "audit-chain-verification",
            "audit",
            True,
            False,
            "Audit chain verification report is missing or unreadable.",
            [str(path)],
        )
    return _check(
        "audit-chain-verification",
        "audit",
        True,
        report.passed,
        "Audit chain verification passed."
        if report.passed
        else "Audit chain verification failed.",
        [str(path), f"checked_files={report.checked_files}", *report.errors],
    )


def _share_readiness_check(root_dir: Path) -> WorkflowQualityGateCheck:
    path = root_dir / "reports" / "share-readiness.json"
    report = _read_model(path, ShareReadinessReport)
    if report is None:
        return _check(
            "share-readiness",
            "sharing",
            True,
            False,
            "Share-readiness report is missing or unreadable.",
            [str(path)],
        )
    return _check(
        "share-readiness",
        "sharing",
        True,
        report.passed,
        "Share-readiness gate passed."
        if report.passed
        else "Share-readiness gate failed.",
        [str(path), f"passed_checks={report.passed_checks}/{len(report.checks)}"],
    )


def _certificate_check(root_dir: Path) -> WorkflowQualityGateCheck:
    path = root_dir / "reports" / "deid-certificate.json"
    certificate = _read_model(path, DeidentificationCertificate)
    if certificate is None:
        return _check(
            "deid-certificate",
            "handoff",
            True,
            False,
            "De-identification certificate is missing or unreadable.",
            [str(path)],
        )
    return _check(
        "deid-certificate",
        "handoff",
        True,
        certificate.passed,
        "De-identification certificate passed."
        if certificate.passed
        else "De-identification certificate failed.",
        [
            str(path),
            f"checks={certificate.passed_checks}/{certificate.total_checks}",
            f"package_entries={certificate.package_entries}",
        ],
    )


def _workflow_report_check(
    workflow_report_path: Path | None,
) -> WorkflowQualityGateCheck:
    if workflow_report_path is None:
        return _check(
            "workflow-run-report",
            "pipeline",
            False,
            True,
            "Workflow run report was not provided; artifact-level gate was evaluated.",
            [],
        )
    report = _read_model(workflow_report_path, WorkflowRunReport)
    if report is None:
        return _check(
            "workflow-run-report",
            "pipeline",
            True,
            False,
            "Workflow run report is missing or unreadable.",
            [str(workflow_report_path)],
        )
    failed_steps = [step.id for step in report.steps if not step.passed]
    return _check(
        "workflow-run-report",
        "pipeline",
        True,
        report.passed and not failed_steps,
        "Workflow run report passed."
        if report.passed and not failed_steps
        else "Workflow run report contains failed steps.",
        [
            str(workflow_report_path),
            f"steps={len(report.steps)}",
            f"failed_steps={','.join(failed_steps)}",
        ],
    )


def _locate_workflow_report(root_dir: Path, workflow_report_path: Path | None) -> Path | None:
    if workflow_report_path is not None:
        return workflow_report_path.resolve()
    candidates = [
        root_dir / "reports" / "workflow-run.json",
        root_dir / "workflow-run.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def _read_model(path: Path, model_type: type[ModelT]) -> ModelT | None:
    if not path.is_file():
        return None
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _check(
    check_id: str,
    stage: str,
    required: bool,
    passed: bool,
    message: str,
    evidence: list[str],
) -> WorkflowQualityGateCheck:
    return WorkflowQualityGateCheck(
        id=check_id,
        stage=stage,
        required=required,
        passed=passed,
        message=message,
        evidence=evidence,
    )
