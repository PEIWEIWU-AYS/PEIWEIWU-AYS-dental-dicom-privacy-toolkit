from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ddpt.capability import build_capability_matrix
from ddpt.models import ObjectiveAuditItem, ObjectiveAuditReport
from ddpt.release import run_release_audit
from ddpt.safety import scan_repository_safety


@dataclass(frozen=True)
class ObjectiveRequirement:
    id: str
    category: str
    requirement: str
    evidence_files: tuple[str, ...]
    capability_ids: tuple[str, ...]
    evidence_terms: tuple[tuple[str, str], ...] = ()
    note: str = ""


OBJECTIVE_REQUIREMENTS = [
    ObjectiveRequirement(
        id="study-rsna-anonymizer",
        category="competitor-learning",
        requirement=(
            "Study RSNA DICOM Anonymizer and inherit configurable research "
            "de-identification."
        ),
        evidence_files=("docs/competitor-analysis.md", "docs/capability-matrix.md"),
        capability_ids=("configurable-anonymization", "profile-quality-review"),
        evidence_terms=(
            ("docs/competitor-analysis.md", "RSNA DICOM Anonymizer"),
            ("docs/competitor-analysis.md", "configurable"),
        ),
        note="Covers configurable profiles, identifier replacement, and profile review.",
    ),
    ObjectiveRequirement(
        id="study-dicomcleaner",
        category="competitor-learning",
        requirement="Study DicomCleaner and inherit header cleaning plus burned-in pixel review.",
        evidence_files=(
            "docs/competitor-analysis.md",
            "docs/pixel-review.md",
            "docs/remediation-plan.md",
        ),
        capability_ids=(
            "metadata-inspection",
            "privacy-remediation-plan",
            "pixel-review-redaction",
        ),
        evidence_terms=(
            ("docs/competitor-analysis.md", "DicomCleaner"),
            ("docs/competitor-analysis.md", "burned-in"),
            ("docs/remediation-plan.md", "ddpt remediation plan"),
        ),
        note=(
            "Covers metadata risk review, remediation planning, pixel preview, "
            "overlay, and redaction evidence."
        ),
    ),
    ObjectiveRequirement(
        id="study-orthanc",
        category="competitor-learning",
        requirement="Study Orthanc and inherit local REST/Web UI workflow integration.",
        evidence_files=(
            "docs/competitor-analysis.md",
            "docs/local-api.md",
            "docs/local-workbench.md",
        ),
        capability_ids=("local-rest-api", "local-browser-workbench"),
        evidence_terms=(
            ("docs/competitor-analysis.md", "Orthanc"),
            ("docs/local-api.md", "/workbench"),
        ),
        note="Keeps Orthanc-inspired integration lightweight and local-first.",
    ),
    ObjectiveRequirement(
        id="study-rsna-ctp",
        category="competitor-learning",
        requirement=(
            "Study RSNA CTP and inherit multi-stage clinical-trial-style "
            "pipeline thinking."
        ),
        evidence_files=("docs/competitor-analysis.md", "recipes/dental-demo-workflow.yml"),
        capability_ids=(
            "pipeline-recipes",
            "share-readiness-gate",
            "workflow-quality-gate",
            "audit-evidence-bundle",
        ),
        evidence_terms=(
            ("docs/competitor-analysis.md", "RSNA CTP"),
            ("recipes/dental-demo-workflow.yml", "share-readiness"),
            ("recipes/dental-demo-workflow.yml", "quality-gate"),
        ),
        note=(
            "Covers staged recipes, audit chain, evidence bundle, sharing gate, "
            "and workflow quality gate."
        ),
    ),
    ObjectiveRequirement(
        id="study-dcmtk-dcmodify",
        category="competitor-learning",
        requirement="Study DCMTK dcmodify and inherit exact DICOM tag operations.",
        evidence_files=("docs/competitor-analysis.md", "docs/tag-operations.md"),
        capability_ids=("tag-operations", "privacy-remediation-plan"),
        evidence_terms=(
            ("docs/competitor-analysis.md", "DCMTK"),
            ("docs/tag-operations.md", "ddpt tag set"),
            ("docs/remediation-plan.md", "recommended action"),
        ),
        note=(
            "Covers dump, set, blank, delete, JSON audit, and planning around "
            "tag-level remediation actions."
        ),
    ),
    ObjectiveRequirement(
        id="study-pydicom-example",
        category="competitor-learning",
        requirement="Study pydicom anonymization examples and build understandable Python logic.",
        evidence_files=(
            "docs/competitor-analysis.md",
            "src/ddpt/anonymize.py",
            "src/ddpt/tag_ops.py",
        ),
        capability_ids=("configurable-anonymization", "tag-operations"),
        evidence_terms=(
            ("docs/competitor-analysis.md", "pydicom"),
            ("src/ddpt/anonymize.py", "pydicom.dcmread"),
        ),
        note="Core DICOM editing is implemented in readable Python modules.",
    ),
    ObjectiveRequirement(
        id="dental-specific-positioning",
        category="differentiation",
        requirement=(
            "Add dental-specific positioning, bilingual discovery, and "
            "synthetic-data safety."
        ),
        evidence_files=("README.md", "docs/discoverability.md", "docs/data-safety.md"),
        capability_ids=("bilingual-discoverability",),
        evidence_terms=(
            ("README.md", "牙科 DICOM 脱敏加密共享工具包"),
            ("docs/data-safety.md", "synthetic"),
        ),
        note="Supports GitHub search, clinical-domain credibility, and public safety boundaries.",
    ),
    ObjectiveRequirement(
        id="multi-file-synthetic-workflow",
        category="differentiation",
        requirement="Provide multi-file synthetic dental datasets for safe batch workflow demos.",
        evidence_files=("docs/synthetic-study.md", "src/ddpt/synthetic.py", "docs/batch.md"),
        capability_ids=(
            "synthetic-study-generator",
            "pipeline-recipes",
            "batch-deid-evidence",
        ),
        evidence_terms=(
            ("docs/synthetic-study.md", "ddpt synthetic-study"),
            ("docs/synthetic-study.md", "dental-linkable-research"),
            ("docs/batch.md", "de-identification comparison"),
            ("src/ddpt/batch.py", "compare_deidentification"),
        ),
        note=(
            "Single files are useful for tests; multi-file synthetic studies better "
            "demonstrate batch, comparison evidence, and research workflows."
        ),
    ),
    ObjectiveRequirement(
        id="research-differentiators",
        category="differentiation",
        requirement="Add research-oriented capabilities beyond baseline anonymizers.",
        evidence_files=(
            "docs/research-sharing-profile.md",
            "docs/linkable-research-profile.md",
            "profiles/dental-linkable-research.yml",
        ),
        capability_ids=("linkable-pseudonymization", "profile-quality-review"),
        evidence_terms=(
            ("docs/research-sharing-profile.md", "date shifting"),
            ("docs/linkable-research-profile.md", "deterministic pseudonymization"),
        ),
        note="Covers deterministic date shifting and linkable pseudonymization for demos.",
    ),
    ObjectiveRequirement(
        id="shareable-proof-package",
        category="differentiation",
        requirement="Add portable proof artifacts for MacBook demos and collaborator review.",
        evidence_files=(
            "docs/evidence-bundle.md",
            "docs/review-dashboard.md",
            "docs/share-readiness.md",
            "docs/deid-certificate.md",
            "docs/quality-gate.md",
            "docs/remediation-plan.md",
        ),
        capability_ids=(
            "audit-evidence-bundle",
            "static-review-dashboard",
            "secure-sharing",
            "deid-certificate",
            "workflow-quality-gate",
            "privacy-remediation-plan",
        ),
        evidence_terms=(
            ("docs/evidence-bundle.md", "ddpt evidence bundle"),
            ("docs/share-readiness.md", "ddpt share readiness"),
            ("docs/deid-certificate.md", "ddpt certificate create"),
            ("docs/quality-gate.md", "ddpt quality gate"),
            ("docs/remediation-plan.md", "Privacy Remediation Plan"),
        ),
        note=(
            "Covers release audit, safety scan, evidence bundle, dashboard, "
            "remediation plan, package receipt, quality gate, and handoff certificate."
        ),
    ),
    ObjectiveRequirement(
        id="deid-certificate-handoff",
        category="differentiation",
        requirement=(
            "Produce a reviewer-friendly de-identification certificate that "
            "summarizes handoff evidence."
        ),
        evidence_files=("docs/deid-certificate.md", "src/ddpt/certificate.py"),
        capability_ids=("deid-certificate", "share-readiness-gate"),
        evidence_terms=(
            ("docs/deid-certificate.md", "De-identification Certificate"),
            ("src/ddpt/certificate.py", "build_deidentification_certificate"),
            ("recipes/dental-demo-workflow.yml", "action: certificate"),
            ("docs/workflow-recipes.md", "`certificate`"),
        ),
        note=(
            "Collects anonymization, validation, comparison, pixel review, "
            "package receipt, audit chain, and share-readiness evidence."
        ),
    ),
    ObjectiveRequirement(
        id="public-release-readiness",
        category="release-readiness",
        requirement=(
            "Provide public repository gates for safety, CI, release readiness, "
            "and testing."
        ),
        evidence_files=(
            ".github/workflows/ci.yml",
            "src/ddpt/release.py",
            "tests/test_cli_workflow.py",
        ),
        capability_ids=("audit-evidence-bundle",),
        evidence_terms=(
            (".github/workflows/ci.yml", "python -m ddpt release audit"),
            (".github/workflows/ci.yml", "python -m ddpt safety scan"),
        ),
        note="Release audit and CI keep the repo publishable without real patient data.",
    ),
]


def run_objective_audit(root_dir: Path) -> ObjectiveAuditReport:
    root = root_dir.resolve()
    capability_report = build_capability_matrix(root)
    release_report = run_release_audit(root)
    safety_report = scan_repository_safety(root)
    implemented_capability_ids = {
        item.id for item in capability_report.items if item.status == "implemented"
    }
    items = [
        _build_requirement_item(root, requirement, implemented_capability_ids)
        for requirement in OBJECTIVE_REQUIREMENTS
    ]
    items.extend(
        [
            _gate_item(
                "capability-matrix-gate",
                "verification",
                "Competitor-informed capability matrix passes with no partial or missing items.",
                capability_report.passed,
                [
                    f"{capability_report.implemented_items}/"
                    f"{capability_report.total_items} implemented"
                ],
                "Run `ddpt capability matrix --root .`.",
            ),
            _gate_item(
                "release-audit-gate",
                "verification",
                "Public release audit passes.",
                release_report.passed,
                [f"{release_report.passed_checks}/{len(release_report.checks)} checks passed"],
                "Run `ddpt release audit .`.",
            ),
            _gate_item(
                "repository-safety-gate",
                "verification",
                "Public repository safety scan passes with no findings.",
                safety_report.passed,
                [f"{safety_report.scanned_files} files scanned"],
                "Run `ddpt safety scan .`.",
            ),
        ]
    )
    passed_items = sum(1 for item in items if item.passed)
    return ObjectiveAuditReport(
        root_dir=str(root),
        passed=passed_items == len(items),
        total_items=len(items),
        passed_items=passed_items,
        failed_items=len(items) - passed_items,
        items=items,
    )


def _build_requirement_item(
    root: Path,
    requirement: ObjectiveRequirement,
    implemented_capability_ids: set[str],
) -> ObjectiveAuditItem:
    evidence: list[str] = []
    missing: list[str] = []

    for path in requirement.evidence_files:
        if (root / path).is_file():
            evidence.append(f"file:{path}")
        else:
            missing.append(f"file:{path}")

    for capability_id in requirement.capability_ids:
        if capability_id in implemented_capability_ids:
            evidence.append(f"capability:{capability_id}")
        else:
            missing.append(f"capability:{capability_id}")

    for path, term in requirement.evidence_terms:
        if _file_contains(root / path, term):
            evidence.append(f"term:{path}:{term}")
        else:
            missing.append(f"term:{path}:{term}")

    return ObjectiveAuditItem(
        id=requirement.id,
        category=requirement.category,
        requirement=requirement.requirement,
        passed=not missing,
        evidence=evidence,
        missing_evidence=missing,
        note=requirement.note,
    )


def _gate_item(
    item_id: str,
    category: str,
    requirement: str,
    passed: bool,
    evidence: list[str],
    note: str,
) -> ObjectiveAuditItem:
    return ObjectiveAuditItem(
        id=item_id,
        category=category,
        requirement=requirement,
        passed=passed,
        evidence=evidence if passed else [],
        missing_evidence=[] if passed else evidence,
        note=note,
    )


def _file_contains(path: Path, term: str) -> bool:
    if not path.is_file():
        return False
    return term.casefold() in path.read_text(encoding="utf-8").casefold()
