from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from ddpt.models import (
    AuditChainVerification,
    ConfidentialityAlignmentReport,
    DeidentificationCertificate,
    DeidentificationComparisonReport,
    FilenamePrivacyScanReport,
    PackageVerificationReceipt,
    PixelReviewReport,
    PixelRiskScanReport,
    ProfileConformanceReport,
    ResidualRiskComponent,
    ResidualRiskReport,
    ShareReadinessReport,
    WorkflowQualityGateReport,
)

ModelT = TypeVar("ModelT", bound=BaseModel)

BOUNDARY_NOTES = [
    "Synthetic-data and explicitly approved test DICOM workflows only.",
    (
        "A low residual-risk score is not legal, clinical, regulatory, "
        "security, or DICOM conformance certification."
    ),
    (
        "Pixel evidence depends on review artifacts; this toolkit does not "
        "claim automatic OCR detection."
    ),
    (
        "Final sharing decisions still need human review, local policy review, "
        "and recipient trust checks."
    ),
]


def score_residual_privacy_risk(root_dir: Path) -> ResidualRiskReport:
    root_dir = root_dir.resolve()
    components = [
        _deidentification_component(root_dir),
        _profile_conformance_component(root_dir),
        _confidentiality_alignment_component(root_dir),
        _pixel_evidence_component(root_dir),
        _filename_privacy_component(root_dir),
        _package_sharing_component(root_dir),
        _quality_gate_component(root_dir),
    ]
    score = sum(component.score for component in components)
    max_score = sum(component.weight for component in components)
    blocking = sum(1 for component in components if component.status == "fail")
    warnings = sum(1 for component in components if component.status in {"warn", "missing"})
    residual_risk = _residual_risk_level(score, max_score, blocking)
    return ResidualRiskReport(
        root_dir=str(root_dir),
        passed=blocking == 0 and score >= 90,
        score=score,
        max_score=max_score,
        residual_risk=residual_risk,
        blocking_findings=blocking,
        warning_findings=warnings,
        components=components,
        boundary_notes=BOUNDARY_NOTES,
    )


def _deidentification_component(root_dir: Path) -> ResidualRiskComponent:
    path = root_dir / "reports" / "deid-comparison.json"
    report = _read_model(path, DeidentificationComparisonReport)
    if report is None:
        return _component(
            "deid-comparison",
            "metadata",
            25,
            0,
            "fail",
            "Before/after de-identification comparison is missing or unreadable.",
            [str(path)],
            ["Run `ddpt compare deid` before scoring residual risk."],
        )

    residual_high = len(report.residual_high_risk_keywords)
    residual_medium = len(report.residual_medium_risk_keywords)
    if (
        report.passed
        and report.private_tags_after == 0
        and not residual_high
        and not residual_medium
    ):
        return _component(
            "deid-comparison",
            "metadata",
            25,
            25,
            "pass",
            (
                "Direct identifier comparison passed with no residual high/medium "
                "keywords or private tags."
            ),
            [
                str(path),
                f"passed_items={report.passed_items}/{report.total_items}",
                f"private_tags_after={report.private_tags_after}",
            ],
        )

    if report.private_tags_after or residual_high:
        status = "fail"
        score = 0
        action = "Fix residual high-risk identifiers or private tags before sharing."
    else:
        status = "warn"
        score = 12
        action = "Review residual medium-risk identifiers before sharing."
    return _component(
        "deid-comparison",
        "metadata",
        25,
        score,
        status,
        "Before/after de-identification comparison found residual metadata risk.",
        [
            str(path),
            f"residual_high={residual_high}",
            f"residual_medium={residual_medium}",
            f"private_tags_after={report.private_tags_after}",
        ],
        [action],
    )


def _profile_conformance_component(root_dir: Path) -> ResidualRiskComponent:
    path = root_dir / "reports" / "profile-conformance.json"
    report = _read_model(path, ProfileConformanceReport)
    if report is None:
        return _component(
            "profile-conformance",
            "profile",
            18,
            0,
            "fail",
            "Profile conformance report is missing or unreadable.",
            [str(path)],
            ["Run `ddpt profile verify` against the selected anonymization profile."],
        )
    if report.passed:
        return _component(
            "profile-conformance",
            "profile",
            18,
            18,
            "pass",
            "Anonymized output conforms to the selected profile.",
            [
                str(path),
                f"profile={report.profile}",
                f"passed={report.passed_checks}/{report.total_checks}",
            ],
        )
    status = "warn" if report.failed_checks <= 2 else "fail"
    score = 8 if status == "warn" else 0
    return _component(
        "profile-conformance",
        "profile",
        18,
        score,
        status,
        "Anonymized output does not fully conform to the selected profile.",
        [
            str(path),
            f"profile={report.profile}",
            f"failed_checks={report.failed_checks}",
            f"skipped_checks={report.skipped_checks}",
        ],
        ["Resolve profile verification failures before public sharing."],
    )


def _confidentiality_alignment_component(root_dir: Path) -> ResidualRiskComponent:
    path = root_dir / "reports" / "confidentiality-alignment.json"
    report = _read_model(path, ConfidentialityAlignmentReport)
    if report is None:
        return _component(
            "confidentiality-alignment",
            "standards",
            12,
            0,
            "missing",
            "DICOM confidentiality alignment report is missing or unreadable.",
            [str(path)],
            ["Run `ddpt confidentiality alignment` to document DICOM PS3.15-inspired coverage."],
        )
    if report.passed:
        return _component(
            "confidentiality-alignment",
            "standards",
            12,
            12,
            "pass",
            "Profile alignment has no high/medium DICOM confidentiality gaps.",
            [
                str(path),
                f"aligned={report.aligned_items}/{report.total_policy_items}",
                f"high_medium_unaligned={report.high_medium_unaligned}",
            ],
        )
    status = "fail" if report.high_medium_unaligned else "warn"
    score = 0 if status == "fail" else 6
    return _component(
        "confidentiality-alignment",
        "standards",
        12,
        score,
        status,
        "DICOM confidentiality alignment has unresolved gaps.",
        [
            str(path),
            f"aligned={report.aligned_items}/{report.total_policy_items}",
            f"high_medium_unaligned={report.high_medium_unaligned}",
        ],
        ["Update the selected profile or explain the accepted confidentiality gap."],
    )


def _pixel_evidence_component(root_dir: Path) -> ResidualRiskComponent:
    review_path = root_dir / "reports" / "pixel-review.json"
    risk_path = root_dir / "reports" / "pixel-risk.json"
    review = _read_model(review_path, PixelReviewReport)
    pixel_risk = _read_model(risk_path, PixelRiskScanReport)
    evidence = [str(review_path), str(risk_path)]

    if review is None and pixel_risk is None:
        return _component(
            "pixel-evidence",
            "pixel",
            15,
            0,
            "fail",
            "Pixel review and pixel risk evidence are both missing or unreadable.",
            evidence,
            ["Run `ddpt pixel-risk scan` and `ddpt pixel-review` before sharing images."],
        )

    if review is None:
        status = "warn" if pixel_risk and pixel_risk.passed else "fail"
        score = 8 if status == "warn" else 0
        return _component(
            "pixel-evidence",
            "pixel",
            15,
            score,
            status,
            "Pixel risk scan exists, but reviewer PNG/redaction evidence is missing.",
            evidence,
            ["Create a pixel review report with original, overlay, and redacted previews."],
        )

    preview_paths = [
        Path(review.original_preview_png),
        Path(review.overlay_preview_png),
        Path(review.redacted_preview_png),
    ]
    missing_previews = [str(path) for path in preview_paths if not path.is_file()]
    review_passed = bool(review.regions) and not missing_previews
    if review_passed and (pixel_risk is None or pixel_risk.passed):
        score = 15 if pixel_risk else 14
        return _component(
            "pixel-evidence",
            "pixel",
            15,
            score,
            "pass",
            "Pixel review evidence includes redaction regions and PNG previews.",
            [
                str(review_path),
                f"regions={len(review.regions)}",
                f"pixel_risk_present={pixel_risk is not None}",
            ],
        )

    status = "warn" if review_passed else "fail"
    score = 10 if status == "warn" else 0
    return _component(
        "pixel-evidence",
        "pixel",
        15,
        score,
        status,
        "Pixel evidence needs review before sharing.",
        [
            str(review_path),
            f"regions={len(review.regions)}",
            f"missing_previews={len(missing_previews)}",
            f"pixel_risk_passed={pixel_risk.passed if pixel_risk else 'missing'}",
        ],
        ["Review burned-in identifiers and regenerate missing pixel evidence."],
    )


def _filename_privacy_component(root_dir: Path) -> ResidualRiskComponent:
    path = root_dir / "reports" / "filename-privacy.json"
    report = _read_model(path, FilenamePrivacyScanReport)
    if report is None:
        return _component(
            "filename-privacy",
            "path-privacy",
            10,
            6,
            "missing",
            "Filename/path privacy report is missing; metadata evidence may still pass.",
            [str(path)],
            ["Run `ddpt filename scan` to catch PHI in file and folder names."],
        )
    if report.passed:
        return _component(
            "filename-privacy",
            "path-privacy",
            10,
            10,
            "pass",
            "Filename and path privacy scan passed.",
            [
                str(path),
                f"scanned_files={report.scanned_files}",
                f"findings={report.findings_count}",
            ],
        )
    status = "fail" if report.high_findings else "warn"
    score = 0 if status == "fail" else 5
    return _component(
        "filename-privacy",
        "path-privacy",
        10,
        score,
        status,
        "Filename/path privacy scan found identifiers that need review.",
        [
            str(path),
            f"high_findings={report.high_findings}",
            f"medium_findings={report.medium_findings}",
        ],
        ["Rename risky files/folders before packaging or uploading evidence."],
    )


def _package_sharing_component(root_dir: Path) -> ResidualRiskComponent:
    receipt_path = root_dir / "reports" / "package-receipt.json"
    readiness_path = root_dir / "reports" / "share-readiness.json"
    audit_path = root_dir / "reports" / "audit-chain-verify.json"
    certificate_path = root_dir / "reports" / "deid-certificate.json"
    receipt = _read_model(receipt_path, PackageVerificationReceipt)
    readiness = _read_model(readiness_path, ShareReadinessReport)
    audit = _read_model(audit_path, AuditChainVerification)
    certificate = _read_model(certificate_path, DeidentificationCertificate)
    evidence = [
        str(receipt_path),
        str(readiness_path),
        str(audit_path),
        str(certificate_path),
    ]

    if receipt is None:
        return _component(
            "package-sharing",
            "sharing",
            12,
            0,
            "fail",
            "Encrypted package receipt is missing or unreadable.",
            evidence,
            ["Create and verify an encrypted package before handoff."],
        )

    receipt_passed = receipt.passed and receipt.encrypted is True and len(receipt.entries) > 0
    readiness_passed = readiness.passed if readiness else False
    audit_passed = audit.passed if audit else False
    certificate_passed = certificate.passed if certificate else False
    if receipt_passed and readiness_passed and audit_passed and certificate_passed:
        return _component(
            "package-sharing",
            "sharing",
            12,
            12,
            "pass",
            "Encrypted package, share-readiness, audit-chain, and certificate evidence passed.",
            [
                str(receipt_path),
                f"entries={len(receipt.entries)}",
                f"share_ready={readiness_passed}",
                f"audit_chain={audit_passed}",
                f"certificate={certificate_passed}",
            ],
        )

    if not receipt_passed:
        status = "fail"
        score = 0
    else:
        status = "warn"
        score = 8
    return _component(
        "package-sharing",
        "sharing",
        12,
        score,
        status,
        "Package sharing evidence is incomplete.",
        [
            str(receipt_path),
            f"receipt_passed={receipt_passed}",
            f"share_ready={readiness_passed}",
            f"audit_chain={audit_passed}",
            f"certificate={certificate_passed}",
        ],
        ["Regenerate share-readiness, audit-chain verification, and certificate reports."],
    )


def _quality_gate_component(root_dir: Path) -> ResidualRiskComponent:
    path = root_dir / "reports" / "quality-gate.json"
    report = _read_model(path, WorkflowQualityGateReport)
    if report is None:
        return _component(
            "workflow-quality-gate",
            "quality",
            8,
            4,
            "missing",
            "Workflow quality gate is missing; residual score uses lower-level reports only.",
            [str(path)],
            ["Run `ddpt quality gate` after generating workflow evidence."],
        )
    if report.passed:
        return _component(
            "workflow-quality-gate",
            "quality",
            8,
            8,
            "pass",
            "Workflow quality gate passed.",
            [
                str(path),
                f"passed_checks={report.passed_checks}/{report.required_checks}",
                f"failed_checks={report.failed_checks}",
            ],
        )
    return _component(
        "workflow-quality-gate",
        "quality",
        8,
        0,
        "fail",
        "Workflow quality gate failed.",
        [
            str(path),
            f"passed_checks={report.passed_checks}/{report.required_checks}",
            f"failed_checks={report.failed_checks}",
        ],
        ["Resolve failed quality gate checks before publishing or sharing evidence."],
    )


def _read_model(path: Path, model_type: type[ModelT]) -> ModelT | None:
    if not path.is_file():
        return None
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _component(
    component_id: str,
    category: str,
    weight: int,
    score: int,
    status: str,
    message: str,
    evidence: list[str],
    recommended_actions: list[str] | None = None,
) -> ResidualRiskComponent:
    return ResidualRiskComponent(
        id=component_id,
        category=category,
        weight=weight,
        score=min(score, weight),
        status=status,  # type: ignore[arg-type]
        message=message,
        evidence=evidence,
        recommended_actions=recommended_actions or [],
    )


def _residual_risk_level(score: int, max_score: int, blocking_findings: int) -> str:
    if blocking_findings:
        return "high"
    percentage = score / max_score if max_score else 0
    if percentage >= 0.9:
        return "low"
    if percentage >= 0.7:
        return "medium"
    return "high"
