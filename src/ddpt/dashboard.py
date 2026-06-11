from __future__ import annotations

import json
from pathlib import Path

from ddpt.models import (
    DashboardArtifact,
    DashboardPreview,
    EvidenceArtifact,
    EvidenceBundleResult,
    ReviewDashboardReport,
)

PREVIEW_CANDIDATES = [
    ("Synthetic input preview", "demo-run/reports/input-preview.png"),
    ("Anonymized DICOM preview", "demo-run/reports/anonymized-preview.png"),
    ("Pixel-redacted DICOM preview", "demo-run/reports/redacted-preview.png"),
    ("Pixel review overlay", "demo-run/reports/pixel-review/pixel-review-overlay.png"),
    ("Pixel review redacted", "demo-run/reports/pixel-review/pixel-review-redacted.png"),
]


def build_review_dashboard_report(
    evidence_dir: Path,
    output_path: Path,
    evidence_result: EvidenceBundleResult | None = None,
) -> ReviewDashboardReport:
    evidence_dir = evidence_dir.resolve()
    output_path = output_path.resolve()
    if evidence_result is None:
        evidence_result = _load_evidence_bundle(evidence_dir)

    artifacts = [
        _dashboard_artifact(evidence_dir, output_path, artifact)
        for artifact in evidence_result.artifacts
    ]
    previews = [
        DashboardPreview(
            label=label,
            path=relative_path,
            exists=(evidence_dir / relative_path).is_file(),
        )
        for label, relative_path in PREVIEW_CANDIDATES
    ]
    available = sum(1 for artifact in artifacts if artifact.exists)
    missing = len(artifacts) - available
    return ReviewDashboardReport(
        evidence_dir=str(evidence_dir),
        output_path=str(output_path),
        passed=evidence_result.passed and missing == 0,
        evidence_bundle_passed=evidence_result.passed,
        total_artifacts=len(artifacts),
        available_artifacts=available,
        missing_artifacts=missing,
        artifacts=artifacts,
        previews=previews,
    )


def _load_evidence_bundle(evidence_dir: Path) -> EvidenceBundleResult:
    evidence_json = evidence_dir / "reports" / "evidence-bundle.json"
    if not evidence_json.is_file():
        raise FileNotFoundError(
            f"Evidence bundle index not found: {evidence_json}. "
            "Run `ddpt evidence bundle . --out evidence-run` first."
        )
    return EvidenceBundleResult.model_validate(
        json.loads(evidence_json.read_text(encoding="utf-8"))
    )


def _dashboard_artifact(
    evidence_dir: Path,
    output_path: Path,
    artifact: EvidenceArtifact,
) -> DashboardArtifact:
    artifact_path = (evidence_dir / artifact.path).resolve()
    exists = artifact_path.is_file() or artifact_path == output_path
    return DashboardArtifact(
        label=artifact.label,
        category=artifact.category,
        path=artifact.path,
        description=artifact.description,
        exists=exists,
    )
