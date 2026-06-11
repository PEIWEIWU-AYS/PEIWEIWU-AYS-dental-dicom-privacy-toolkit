from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from ddpt.models import (
    AnonymizationAudit,
    AuditChainVerification,
    CertificateEvidenceItem,
    DeidentificationCertificate,
    DeidentificationComparisonReport,
    PackageVerificationReceipt,
    PixelReviewReport,
    ShareReadinessReport,
    ValidationReport,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def build_deidentification_certificate(root_dir: Path) -> DeidentificationCertificate:
    root = root_dir.resolve()
    reports_dir = root / "reports"

    audit_path = reports_dir / "audit.json"
    validation_path = reports_dir / "validation.json"
    comparison_path = reports_dir / "deid-comparison.json"
    pixel_review_path = reports_dir / "pixel-review.json"
    package_receipt_path = reports_dir / "package-receipt.json"
    audit_chain_verify_path = reports_dir / "audit-chain-verify.json"
    share_readiness_path = reports_dir / "share-readiness.json"

    audit = _read_model(audit_path, AnonymizationAudit)
    validation = _read_model(validation_path, ValidationReport)
    comparison = _read_model(comparison_path, DeidentificationComparisonReport)
    pixel_review = _read_model(pixel_review_path, PixelReviewReport)
    package_receipt = _read_model(package_receipt_path, PackageVerificationReceipt)
    audit_chain = _read_model(audit_chain_verify_path, AuditChainVerification)
    share_readiness = _read_model(share_readiness_path, ShareReadinessReport)

    checks = [
        _check_from_model(
            "anonymization-audit",
            "metadata",
            audit is not None and bool(audit.actions),
            "Anonymization audit records metadata changes.",
            [str(audit_path)],
        ),
        _check_from_model(
            "validation",
            "privacy",
            validation is not None and validation.passed,
            "Anonymized DICOM validation passed.",
            [str(validation_path)],
        ),
        _comparison_check(comparison_path, comparison),
        _pixel_review_check(pixel_review_path, pixel_review),
        _package_check(package_receipt_path, package_receipt),
        _check_from_model(
            "audit-chain",
            "audit",
            audit_chain is not None and audit_chain.passed,
            "Audit chain verification passed.",
            [str(audit_chain_verify_path)],
        ),
        _check_from_model(
            "share-readiness",
            "sharing",
            share_readiness is not None and share_readiness.passed,
            "Share-readiness gate passed.",
            [str(share_readiness_path)],
        ),
    ]

    passed_checks = sum(1 for check in checks if check.passed)
    return DeidentificationCertificate(
        root_dir=str(root),
        passed=passed_checks == len(checks),
        profile=audit.profile if audit else "unknown",
        input_path=audit.input_path if audit else "",
        anonymized_path=audit.output_path if audit else "",
        package_path=package_receipt.package_path if package_receipt else None,
        package_sha256=package_receipt.package_sha256 if package_receipt else None,
        passed_checks=passed_checks,
        total_checks=len(checks),
        residual_high_risk_keywords=(
            comparison.residual_high_risk_keywords if comparison else []
        ),
        residual_medium_risk_keywords=(
            comparison.residual_medium_risk_keywords if comparison else []
        ),
        private_tags_after=comparison.private_tags_after if comparison else None,
        pixel_review_regions=len(pixel_review.regions) if pixel_review else 0,
        package_entries=len(package_receipt.entries) if package_receipt else 0,
        share_readiness_passed=share_readiness.passed if share_readiness else False,
        checks=checks,
    )


def _comparison_check(
    path: Path,
    report: DeidentificationComparisonReport | None,
) -> CertificateEvidenceItem:
    passed = (
        report is not None
        and report.passed
        and not report.residual_high_risk_keywords
        and not report.residual_medium_risk_keywords
        and report.private_tags_after == 0
    )
    evidence = [str(path)]
    if report:
        evidence.extend(
            [
                f"passed_items={report.passed_items}/{report.total_items}",
                f"private_tags_after={report.private_tags_after}",
                f"residual_high={len(report.residual_high_risk_keywords)}",
                f"residual_medium={len(report.residual_medium_risk_keywords)}",
            ]
        )
    return _check_from_model(
        "deid-comparison",
        "privacy",
        passed,
        "Before/after de-identification comparison passed.",
        evidence,
    )


def _pixel_review_check(
    path: Path,
    report: PixelReviewReport | None,
) -> CertificateEvidenceItem:
    previews = []
    if report:
        previews = [
            report.original_preview_png,
            report.overlay_preview_png,
            report.redacted_preview_png,
        ]
    missing = [preview for preview in previews if not Path(preview).is_file()]
    passed = report is not None and bool(report.regions) and not missing
    evidence = [str(path), f"regions={len(report.regions) if report else 0}", *missing]
    return _check_from_model(
        "pixel-review",
        "pixel",
        passed,
        "Pixel review and redaction preview evidence is present.",
        evidence,
    )


def _package_check(
    path: Path,
    receipt: PackageVerificationReceipt | None,
) -> CertificateEvidenceItem:
    package_exists = Path(receipt.package_path).is_file() if receipt else False
    passed = (
        receipt is not None
        and receipt.passed
        and receipt.encrypted is True
        and package_exists
    )
    evidence = [str(path)]
    if receipt:
        evidence.extend(
            [
                f"package={receipt.package_path}",
                f"encrypted={receipt.encrypted}",
                f"entries={len(receipt.entries)}",
                f"sha256={receipt.package_sha256}",
            ]
        )
    return _check_from_model(
        "package-receipt",
        "sharing",
        passed,
        "Encrypted package verification receipt passed.",
        evidence,
    )


def _check_from_model(
    check_id: str,
    category: str,
    passed: bool,
    summary: str,
    evidence: list[str],
) -> CertificateEvidenceItem:
    return CertificateEvidenceItem(
        id=check_id,
        category=category,
        passed=passed,
        summary=summary if passed else f"{summary} Evidence is missing or failed.",
        evidence=evidence,
    )


def _read_model(path: Path, model_type: type[ModelT]) -> ModelT | None:
    if not path.is_file():
        return None
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception:
        return None
