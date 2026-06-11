from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ddpt.models import (
    CapabilityMatrixItem,
    CapabilityMatrixReport,
    CompetitorReference,
)


@dataclass(frozen=True)
class CapabilitySpec:
    id: str
    capability: str
    source_tools: tuple[str, ...]
    evidence_files: tuple[str, ...]
    command: str | None
    differentiator: str
    note: str


REFERENCE_TOOLS = [
    CompetitorReference(
        name="RSNA DICOM Anonymizer",
        category="research GUI anonymizer",
        url="https://github.com/RSNA/Anonymizer",
        strengths=[
            "research-oriented workflow",
            "configurable DICOM de-identification",
            "reputable radiology community source",
        ],
        gaps_for_dental_toolkit=[
            "not dental-specific",
            "less focused on small CLI evidence bundles",
            "not bilingual GitHub-discoverability-first",
        ],
    ),
    CompetitorReference(
        name="PixelMed DicomCleaner",
        category="desktop DICOM cleaning GUI",
        url="https://www.pixelmed.com/cleaner.html",
        strengths=[
            "free GUI workflow",
            "DICOM header cleaning",
            "burned-in pixel annotation masking support",
        ],
        gaps_for_dental_toolkit=[
            "harder to automate in CI",
            "less focused on reusable public evidence reports",
            "not dental workflow packaged",
        ],
    ),
    CompetitorReference(
        name="Orthanc",
        category="DICOM server and REST API",
        url="https://orthanc.uclouvain.be/book/users/anonymization.html",
        strengths=[
            "production-grade DICOM server",
            "Web UI and REST API",
            "server-side anonymization flow",
        ],
        gaps_for_dental_toolkit=[
            "heavier server architecture",
            "not a small local research toolkit",
            "requires more deployment knowledge",
        ],
    ),
    CompetitorReference(
        name="RSNA CTP",
        category="clinical trial image pipeline",
        url="https://mircwiki.rsna.org/index.php?title=MIRC_CTP",
        strengths=[
            "multi-stage clinical trial pipeline",
            "DICOM anonymizer stage",
            "mature processing architecture",
        ],
        gaps_for_dental_toolkit=[
            "heavy Java/server setup",
            "not optimized for a first GitHub demo",
            "not dental-focused",
        ],
    ),
    CompetitorReference(
        name="DCMTK dcmodify",
        category="low-level DICOM tag CLI",
        url="https://support.dcmtk.org/docs/dcmodify.html",
        strengths=[
            "precise tag set/insert/delete operations",
            "deterministic command-line behavior",
            "widely known DICOM toolkit",
        ],
        gaps_for_dental_toolkit=[
            "requires users to know exact DICOM tags",
            "not a workflow/reporting product",
            "no dental-specific safety package by itself",
        ],
    ),
    CompetitorReference(
        name="pydicom anonymization example",
        category="Python library example",
        url="https://pydicom.github.io/pydicom/stable/auto_examples/metadata_processing/plot_anonymize.html",
        strengths=[
            "clear Python-level DICOM editing pattern",
            "easy for researchers to understand",
            "lightweight library foundation",
        ],
        gaps_for_dental_toolkit=[
            "example-level only",
            "no complete CLI/report/encryption workflow",
            "no dental-specific profiles or evidence bundle",
        ],
    ),
]


CAPABILITY_SPECS = [
    CapabilitySpec(
        id="metadata-inspection",
        capability="DICOM metadata inspection and privacy risk classification",
        source_tools=("DicomCleaner", "DCMTK dcmodify", "pydicom anonymization example"),
        evidence_files=(
            "src/ddpt/inspection.py",
            "src/ddpt/risk.py",
            "docs/product-requirements.md",
            "tests/test_cli_workflow.py",
        ),
        command="ddpt inspect synthetic.dcm --json inspect.json --html inspect.html",
        differentiator="Dental-focused risk language with JSON and static HTML reports.",
        note="Matches the baseline need to see risky DICOM header values before writing output.",
    ),
    CapabilitySpec(
        id="synthetic-study-generator",
        capability="Multi-file synthetic dental study generation for local workflow demos",
        source_tools=("RSNA CTP", "pydicom anonymization example"),
        evidence_files=(
            "src/ddpt/synthetic.py",
            "docs/synthetic-study.md",
            "tests/test_cli_workflow.py",
        ),
        command=(
            "ddpt synthetic-study synthetic-study-demo --patients 2 "
            "--files-per-patient 2 --json synthetic-study-demo/manifest.json"
        ),
        differentiator=(
            "Creates repeated-subject synthetic folders for batch and linkable "
            "research demonstrations without real patient data."
        ),
        note=(
            "Provides safe multi-file inputs for inventory, batch anonymization, "
            "and pseudonymization verification."
        ),
    ),
    CapabilitySpec(
        id="configurable-anonymization",
        capability="Configurable metadata anonymization profiles",
        source_tools=("RSNA DICOM Anonymizer", "pydicom anonymization example"),
        evidence_files=(
            "src/ddpt/anonymize.py",
            "src/ddpt/profiles.py",
            "profiles/dental-basic.yml",
            "profiles/dental-research-sharing.yml",
        ),
        command="ddpt anonymize input.dcm --out output.dcm --profile dental-basic",
        differentiator="Dental and research-sharing profiles are included as readable YAML.",
        note="Supports replace, blank, UID regeneration, private tag removal, and date shifting.",
    ),
    CapabilitySpec(
        id="profile-quality-review",
        capability="Profile coverage, comparison, and lint reports",
        source_tools=("RSNA DICOM Anonymizer", "RSNA CTP"),
        evidence_files=(
            "src/ddpt/profiles.py",
            "src/ddpt/policy.py",
            "docs/profile-comparison.md",
            "docs/profile-lint.md",
        ),
        command="ddpt profile lint dental-basic --json lint.json --html lint.html",
        differentiator="Custom YAML profiles can be audited before touching DICOM files.",
        note="Catches unknown DICOM keywords, conflicting actions, and policy coverage gaps.",
    ),
    CapabilitySpec(
        id="linkable-pseudonymization",
        capability="Deterministic pseudonymization for synthetic longitudinal research demos",
        source_tools=("RSNA DICOM Anonymizer", "RSNA CTP", "pydicom anonymization example"),
        evidence_files=(
            "src/ddpt/anonymize.py",
            "src/ddpt/profiles.py",
            "profiles/dental-linkable-research.yml",
            "docs/linkable-research-profile.md",
            "tests/test_cli_workflow.py",
        ),
        command=(
            "ddpt anonymize input.dcm --profile dental-linkable-research "
            "--out output.dcm --audit audit.json"
        ),
        differentiator=(
            "The same synthetic patient can stay linkable across studies without "
            "exposing the original PatientName or PatientID."
        ),
        note=(
            "Adds research-oriented linkage evidence while keeping public demos "
            "synthetic-data-only."
        ),
    ),
    CapabilitySpec(
        id="before-after-deid-comparison",
        capability="Before/after de-identification comparison reports",
        source_tools=("DicomCleaner", "RSNA DICOM Anonymizer", "pydicom anonymization example"),
        evidence_files=(
            "src/ddpt/deid_compare.py",
            "docs/deid-comparison.md",
            "recipes/dental-demo-workflow.yml",
            "tests/test_cli_workflow.py",
        ),
        command=(
            "ddpt compare deid input.dcm output.dcm --json deid-comparison.json "
            "--html deid-comparison.html"
        ),
        differentiator="Side-by-side privacy policy evidence shows what changed and what remains.",
        note="Complements audit logs with a reviewer-friendly before/after report.",
    ),
    CapabilitySpec(
        id="pixel-review-redaction",
        capability="Burned-in pixel annotation review and rectangular redaction",
        source_tools=("PixelMed DicomCleaner",),
        evidence_files=(
            "src/ddpt/pixel_review.py",
            "src/ddpt/pixels.py",
            "profiles/dental-pixel-redaction.yml",
            "docs/pixel-review.md",
        ),
        command=(
            "ddpt pixel-review output.dcm --plan profiles/dental-pixel-redaction.yml "
            "--html pixel-review.html"
        ),
        differentiator="Creates original, overlay, and redacted PNG evidence for GitHub demos.",
        note="Supports known-region review; it does not claim automatic OCR detection.",
    ),
    CapabilitySpec(
        id="tag-operations",
        capability="Exact DICOM tag dump, set, blank, and delete operations",
        source_tools=("DCMTK dcmodify", "pydicom anonymization example"),
        evidence_files=(
            "src/ddpt/tag_ops.py",
            "docs/tag-operations.md",
            "tests/test_cli_workflow.py",
        ),
        command="ddpt tag set input.dcm PatientID DDPT-ID --out edited.dcm --audit tag-audit.json",
        differentiator="Low-level edits produce JSON audit trails instead of silent mutation.",
        note="Gives expert users deterministic control without hiding DICOM tag changes.",
    ),
    CapabilitySpec(
        id="pipeline-recipes",
        capability="Multi-stage privacy workflow recipes",
        source_tools=("RSNA CTP", "Orthanc"),
        evidence_files=(
            "src/ddpt/workflow.py",
            "recipes/dental-demo-workflow.yml",
            "docs/workflow-recipes.md",
            "tests/test_cli_workflow.py",
        ),
        command=(
            "ddpt workflow run recipes/dental-demo-workflow.yml --root workflow-run "
            "--html workflow.html"
        ),
        differentiator="CTP-style staged processing without heavy server infrastructure.",
        note=(
            "Synthetic, inspect, anonymize, validate, pixel review, package, "
            "and audit stages run together."
        ),
    ),
    CapabilitySpec(
        id="batch-deid-evidence",
        capability="Batch de-identification evidence for directory workflows",
        source_tools=("RSNA CTP", "pydicom anonymization example", "DCMTK dcmodify"),
        evidence_files=(
            "src/ddpt/batch.py",
            "docs/batch.md",
            "tests/test_cli_workflow.py",
        ),
        command="ddpt batch synthetic-study-demo --out synthetic-study-demo-batch",
        differentiator=(
            "Directory-level processing writes per-file inspection, audit, "
            "validation, and before/after de-identification comparison evidence."
        ),
        note=(
            "Extends the CTP-style pipeline idea from single demos to repeated "
            "synthetic folders and batch validation."
        ),
    ),
    CapabilitySpec(
        id="local-rest-api",
        capability="Local REST API for integration demos",
        source_tools=("Orthanc",),
        evidence_files=(
            "src/ddpt/api.py",
            "docs/local-api.md",
            "tests/test_cli_workflow.py",
        ),
        command="ddpt api serve demo-run --host 127.0.0.1 --port 8765",
        differentiator="Orthanc-inspired local API focused on synthetic dental privacy demos.",
        note="Keeps the first release lightweight while still enabling integration testing.",
    ),
    CapabilitySpec(
        id="local-browser-workbench",
        capability="Local browser workbench for synthetic DICOM workflow review",
        source_tools=("RSNA DICOM Anonymizer", "PixelMed DicomCleaner", "Orthanc"),
        evidence_files=(
            "src/ddpt/api.py",
            "src/ddpt/workbench.py",
            "docs/local-workbench.md",
            "tests/test_cli_workflow.py",
        ),
        command="ddpt api serve demo-run --host 127.0.0.1 --port 8765",
        differentiator=(
            "GUI-style browser controls run against the local API without adding "
            "a production PACS or cloud upload path."
        ),
        note=(
            "Workbench exposes health, demo, inventory, inspect, anonymize, "
            "validate, preview, and safe file links for synthetic workflows."
        ),
    ),
    CapabilitySpec(
        id="static-review-dashboard",
        capability="Static local review dashboard for non-programmer walkthroughs",
        source_tools=("RSNA DICOM Anonymizer", "PixelMed DicomCleaner", "Orthanc"),
        evidence_files=(
            "src/ddpt/dashboard.py",
            "src/ddpt/reports.py",
            "docs/review-dashboard.md",
            "docs/macbook-validation.md",
        ),
        command=(
            "ddpt dashboard build evidence-run --out "
            "evidence-run/reports/review-dashboard.html"
        ),
        differentiator="A single local HTML entrypoint gathers reports, links, and previews.",
        note=(
            "Adds GUI-style review without requiring a server, browser upload, or real data."
        ),
    ),
    CapabilitySpec(
        id="secure-sharing",
        capability="Encrypted sharing package with manifest, checksums, and receipt",
        source_tools=("RSNA CTP",),
        evidence_files=(
            "src/ddpt/sharing.py",
            "docs/package-verification-receipts.md",
            "dicom-encryption/README.md",
            "dicom-sharing/README.md",
        ),
        command="ddpt package outputs --out package.ddpt --encrypt --key-out package.key",
        differentiator="Receiver-side verification receipts make sharing evidence portable.",
        note="Adds a practical collaboration layer beyond basic anonymization.",
    ),
    CapabilitySpec(
        id="share-readiness-gate",
        capability="Share-readiness gate for package, privacy, pixel, and audit evidence",
        source_tools=("RSNA CTP", "Orthanc", "PixelMed DicomCleaner"),
        evidence_files=(
            "src/ddpt/share_readiness.py",
            "docs/share-readiness.md",
            "src/ddpt/pipeline.py",
            "tests/test_cli_workflow.py",
        ),
        command=(
            "ddpt share readiness demo-run --json reports/share-readiness.json "
            "--html reports/share-readiness.html"
        ),
        differentiator="One gate checks whether synthetic sharing evidence is complete.",
        note="Turns individual reports into a final reviewer-friendly sharing checklist.",
    ),
    CapabilitySpec(
        id="workflow-quality-gate",
        capability="Workflow quality gate for reproducible public review evidence",
        source_tools=("RSNA CTP", "Orthanc", "PixelMed DicomCleaner"),
        evidence_files=(
            "src/ddpt/quality_gate.py",
            "docs/quality-gate.md",
            "recipes/dental-demo-workflow.yml",
            "tests/test_cli_workflow.py",
        ),
        command=(
            "ddpt quality gate workflow-run --workflow-report "
            "workflow-run/reports/workflow-run.json --json "
            "workflow-run/reports/quality-gate.json --html "
            "workflow-run/reports/quality-gate.html"
        ),
        differentiator=(
            "A single JSON/HTML gate verifies workflow, privacy, pixel, package, "
            "audit, readiness, and certificate evidence for MacBook and CI demos."
        ),
        note=(
            "This extends CTP-style staged processing into a public-review quality "
            "gate while staying lightweight and local-first."
        ),
    ),
    CapabilitySpec(
        id="deid-certificate",
        capability="De-identification certificate for synthetic sharing handoff",
        source_tools=("RSNA DICOM Anonymizer", "RSNA CTP", "PixelMed DicomCleaner"),
        evidence_files=(
            "src/ddpt/certificate.py",
            "src/ddpt/workflow.py",
            "docs/deid-certificate.md",
            "docs/workflow-recipes.md",
            "src/ddpt/pipeline.py",
            "recipes/dental-demo-workflow.yml",
            "tests/test_cli_workflow.py",
        ),
        command=(
            "ddpt certificate create demo-run --json demo-run/reports/"
            "deid-certificate.json --html demo-run/reports/deid-certificate.html"
        ),
        differentiator=(
            "A portable JSON/HTML handoff certificate gathers privacy, pixel, "
            "package, audit, and readiness proof in one artifact, including "
            "as the final YAML workflow stage."
        ),
        note=(
            "This is project evidence for synthetic demos, not legal, clinical, "
            "regulatory, or security certification."
        ),
    ),
    CapabilitySpec(
        id="audit-evidence-bundle",
        capability="Audit chain, release audit, safety scan, and evidence bundle",
        source_tools=("RSNA CTP", "Orthanc"),
        evidence_files=(
            "src/ddpt/audit_chain.py",
            "src/ddpt/release.py",
            "src/ddpt/safety.py",
            "src/ddpt/evidence.py",
            "docs/evidence-bundle.md",
        ),
        command="ddpt evidence bundle . --out evidence-run",
        differentiator=(
            "One command produces MacBook-verifiable proof artifacts for demos and review."
        ),
        note=(
            "Combines technical checks, safety boundaries, reports, workflow output, "
            "and package proof."
        ),
    ),
    CapabilitySpec(
        id="objective-completion-audit",
        capability="Original objective completion audit with requirement-level evidence",
        source_tools=(
            "RSNA DICOM Anonymizer",
            "PixelMed DicomCleaner",
            "Orthanc",
            "RSNA CTP",
            "DCMTK dcmodify",
            "pydicom anonymization example",
        ),
        evidence_files=(
            "src/ddpt/completion.py",
            "docs/objective-completion-audit.md",
            "tests/test_cli_workflow.py",
        ),
        command="ddpt completion audit . --json objective-audit.json --html objective-audit.html",
        differentiator=(
            "The project can audit itself against the original competitor-learning objective."
        ),
        note=(
            "Maps each named reference tool, inherited capability, and differentiator "
            "to files, terms, capability IDs, and release gates."
        ),
    ),
    CapabilitySpec(
        id="bilingual-discoverability",
        capability="Bilingual GitHub discoverability and synthetic-data safety positioning",
        source_tools=("RSNA DICOM Anonymizer", "pydicom anonymization example"),
        evidence_files=(
            "README.md",
            "docs/discoverability.md",
            "docs/data-safety.md",
            "CITATION.cff",
        ),
        command=None,
        differentiator="English repo slug with Chinese/English naming, keywords, and topics.",
        note="Designed for stars, citations, dental collaborators, and safe public demonstration.",
    ),
]


def build_capability_matrix(root_dir: Path) -> CapabilityMatrixReport:
    root_dir = root_dir.resolve()
    items = [_build_item(root_dir, spec) for spec in CAPABILITY_SPECS]
    implemented = sum(1 for item in items if item.status == "implemented")
    partial = sum(1 for item in items if item.status == "partial")
    missing = sum(1 for item in items if item.status == "missing")
    return CapabilityMatrixReport(
        root_dir=str(root_dir),
        passed=missing == 0 and partial == 0,
        implemented_items=implemented,
        partial_items=partial,
        missing_items=missing,
        total_items=len(items),
        references=REFERENCE_TOOLS,
        items=items,
    )


def _build_item(root_dir: Path, spec: CapabilitySpec) -> CapabilityMatrixItem:
    missing_files = [path for path in spec.evidence_files if not (root_dir / path).is_file()]
    if not missing_files:
        status = "implemented"
    elif len(missing_files) == len(spec.evidence_files):
        status = "missing"
    else:
        status = "partial"
    evidence = [f"file:{path}" for path in spec.evidence_files]
    if spec.command:
        evidence.append(f"command:{spec.command}")
    return CapabilityMatrixItem(
        id=spec.id,
        capability=spec.capability,
        source_tools=list(spec.source_tools),
        status=status,
        evidence=evidence,
        missing_evidence=[f"file:{path}" for path in missing_files],
        command=spec.command,
        differentiator=spec.differentiator,
        note=spec.note,
    )
