from __future__ import annotations

from pathlib import Path

from ddpt.capability import build_capability_matrix
from ddpt.models import CompetitorCoverageReport, CompetitorCoverageTool

BOUNDARY_NOTES = [
    "Synthetic-data-only public demos; do not use real patient DICOM in this repository.",
    "Not a diagnostic viewer, clinical device, legal certification, or regulatory approval.",
    (
        "Pixel review supports known-region redaction evidence; it does not claim "
        "automatic OCR discovery."
    ),
    (
        "The Orthanc-inspired API is local-first and lightweight, not a production "
        "PACS or DICOMweb server."
    ),
    "dcmodify plans are review artifacts and are not executed automatically.",
]


def build_competitor_coverage(root_dir: Path) -> CompetitorCoverageReport:
    root_dir = root_dir.resolve()
    matrix = build_capability_matrix(root_dir)
    tools: list[CompetitorCoverageTool] = []

    for reference in matrix.references:
        related = [
            item for item in matrix.items if reference.name in item.source_tools
        ]
        implemented = [item for item in related if item.status == "implemented"]
        partial = [item for item in related if item.status == "partial"]
        missing = [item for item in related if item.status == "missing"]
        if missing:
            status = "missing"
        elif partial:
            status = "partial"
        elif implemented:
            status = "covered"
        else:
            status = "missing"

        tools.append(
            CompetitorCoverageTool(
                name=reference.name,
                category=reference.category,
                url=reference.url,
                status=status,
                strengths_learned=reference.strengths,
                project_responses=_project_responses(reference.gaps_for_dental_toolkit),
                implemented_capabilities=len(implemented),
                partial_capabilities=len(partial),
                missing_capabilities=len(missing),
                capabilities=related,
            )
        )

    covered = sum(1 for tool in tools if tool.status == "covered")
    partial_tools = sum(1 for tool in tools if tool.status == "partial")
    missing_tools = sum(1 for tool in tools if tool.status == "missing")
    return CompetitorCoverageReport(
        root_dir=str(root_dir),
        passed=matrix.passed and missing_tools == 0 and partial_tools == 0,
        covered_tools=covered,
        partial_tools=partial_tools,
        missing_tools=missing_tools,
        total_tools=len(tools),
        implemented_capabilities=matrix.implemented_items,
        total_capabilities=matrix.total_items,
        boundary_notes=BOUNDARY_NOTES,
        tools=tools,
    )


def _project_responses(gaps: list[str]) -> list[str]:
    responses = []
    for gap in gaps:
        normalized = gap.lower()
        if "not dental" in normalized:
            response = "Add dental-specific naming, profiles, examples, and safety language."
        elif "cli" in normalized or "evidence" in normalized:
            response = "Provide CLI-first JSON/HTML reports and local evidence bundles."
        elif "bilingual" in normalized:
            response = "Use bilingual README, keywords, topics, and discoverability docs."
        elif "automate" in normalized or "ci" in normalized:
            response = "Make the workflow testable in CI with deterministic synthetic data."
        elif "server" in normalized or "deployment" in normalized:
            response = "Keep demos local-first while adding lightweight REST and HTML review."
        elif "tags" in normalized:
            response = "Wrap low-level tag operations with readable policy and audit reports."
        elif "workflow" in normalized or "report" in normalized:
            response = "Turn individual DICOM edits into staged workflow and review artifacts."
        elif "example-level" in normalized:
            response = "Package Python primitives into CLI, API, docs, tests, and reports."
        elif "setup" in normalized or "infrastructure" in normalized:
            response = "Avoid heavy infrastructure for the first public MacBook demo."
        else:
            response = f"Document and address this boundary: {gap}."
        responses.append(response)
    return responses
