from __future__ import annotations

import json
from pathlib import Path

from ddpt.models import (
    EvidenceBundleResult,
    ShowcaseItem,
    ShowcasePreview,
    ShowcaseReport,
)

SHOWCASE_LABELS = [
    "Review dashboard HTML",
    "Demo summary HTML",
    "De-identification certificate HTML",
    "De-identification comparison HTML",
    "Profile conformance HTML",
    "DICOM confidentiality alignment HTML",
    "Clinic export intake triage HTML",
    "Reference tool export HTML",
    "Competitor coverage HTML",
    "Capability matrix HTML",
    "Privacy regression suite HTML",
    "GitHub publish preflight HTML",
]

SHOWCASE_PREVIEWS = [
    (
        "Synthetic input",
        "demo-run/reports/input-preview.png",
        "Synthetic dental DICOM preview before anonymization.",
    ),
    (
        "Anonymized output",
        "demo-run/reports/anonymized-preview.png",
        "Preview after metadata de-identification.",
    ),
    (
        "Pixel review overlay",
        "demo-run/reports/pixel-review/pixel-review-overlay.png",
        "Known-region burned-in annotation review overlay.",
    ),
    (
        "Pixel-redacted output",
        "demo-run/reports/redacted-preview.png",
        "Preview after demonstration pixel redaction.",
    ),
]

STORY_POINTS = [
    "Start with synthetic dental DICOM data only.",
    "Inspect metadata, paths, DICOMDIR risk, and sidecar export risks before sharing.",
    "Apply profile-driven de-identification and verify the output after writing DICOM.",
    "Review pixel-layer risk with local PNG evidence instead of uploading images.",
    "Package, audit, score, and certify the synthetic handoff evidence.",
    "Map the workflow back to RSNA, DicomCleaner, Orthanc, RSNA CTP, DCMTK, and pydicom lessons.",
]

SAFETY_NOTES = [
    "The showcase is generated from synthetic evidence only.",
    "Do not commit real DICOM, clinic exports, PDFs, spreadsheets, photos, or consent forms.",
    (
        "Generated showcase output is for local review and GitHub screenshots; "
        "it is not clinical, legal, regulatory, or security certification."
    ),
]


def build_showcase_report(evidence_dir: Path, output_path: Path) -> ShowcaseReport:
    evidence_dir = evidence_dir.resolve()
    output_path = output_path.resolve()
    evidence_result = _load_evidence_bundle(evidence_dir)
    artifact_by_label = {artifact.label: artifact for artifact in evidence_result.artifacts}

    items: list[ShowcaseItem] = []
    for label in SHOWCASE_LABELS:
        artifact = artifact_by_label.get(label)
        if artifact is None:
            items.append(
                ShowcaseItem(
                    label=label,
                    category="missing",
                    path="",
                    description="Expected showcase artifact is missing from evidence bundle.",
                    exists=False,
                )
            )
            continue
        items.append(
            ShowcaseItem(
                label=artifact.label,
                category=artifact.category,
                path=artifact.path,
                description=artifact.description,
                exists=(evidence_dir / artifact.path).is_file(),
            )
        )

    previews = [
        ShowcasePreview(
            label=label,
            path=path,
            description=description,
            exists=(evidence_dir / path).is_file(),
        )
        for label, path, description in SHOWCASE_PREVIEWS
    ]
    available_items = sum(1 for item in items if item.exists)
    available_previews = sum(1 for item in previews if item.exists)
    return ShowcaseReport(
        evidence_dir=str(evidence_dir),
        output_path=str(output_path),
        passed=(
            evidence_result.passed
            and available_items == len(items)
            and available_previews == len(previews)
        ),
        title="Dental DICOM Privacy Toolkit Showcase",
        subtitle=(
            "Synthetic evidence gallery for GitHub visitors, collaborators, and "
            "MacBook demonstrations."
        ),
        total_items=len(items),
        available_items=available_items,
        total_previews=len(previews),
        available_previews=available_previews,
        items=items,
        previews=previews,
        story_points=STORY_POINTS,
        safety_notes=SAFETY_NOTES,
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
