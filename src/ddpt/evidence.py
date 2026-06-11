from __future__ import annotations

from pathlib import Path

from ddpt.capability import build_capability_matrix
from ddpt.competitor import build_competitor_coverage
from ddpt.completion import run_objective_audit
from ddpt.confidentiality import build_confidentiality_alignment
from ddpt.dashboard import build_review_dashboard_report
from ddpt.doctor import run_doctor
from ddpt.models import EvidenceArtifact, EvidenceBundleResult
from ddpt.pipeline import run_demo_pipeline
from ddpt.policy import policy_registry_report, write_policy_registry_csv
from ddpt.profiles import lint_profile
from ddpt.quality_gate import run_workflow_quality_gate
from ddpt.regression import run_privacy_regression_suite
from ddpt.release import run_release_audit
from ddpt.reports import (
    model_to_dict,
    write_capability_matrix_html,
    write_competitor_coverage_html,
    write_confidentiality_alignment_html,
    write_evidence_bundle_html,
    write_objective_audit_html,
    write_policy_registry_html,
    write_privacy_regression_html,
    write_profile_lint_html,
    write_release_audit_html,
    write_review_dashboard_html,
    write_workflow_html,
    write_workflow_quality_gate_html,
)
from ddpt.safety import scan_repository_safety
from ddpt.utils import write_json
from ddpt.workflow import run_workflow


def run_evidence_bundle(repository_root: Path, output_dir: Path) -> EvidenceBundleResult:
    repository_root = repository_root.resolve()
    output_dir = output_dir.resolve()
    reports_dir = output_dir / "reports"
    workflow_dir = output_dir / "workflow-run"
    demo_dir = output_dir / "demo-run"
    regression_dir = output_dir / "regression-run"

    output_dir.mkdir(parents=True, exist_ok=True)

    doctor_report = run_doctor()
    safety_report = scan_repository_safety(repository_root)
    release_report = run_release_audit(repository_root)
    policy_report = policy_registry_report()
    confidentiality_report = build_confidentiality_alignment("dental-basic")
    capability_report = build_capability_matrix(repository_root)
    competitor_report = build_competitor_coverage(repository_root)
    objective_report = run_objective_audit(repository_root)
    basic_lint_report = lint_profile("dental-basic")
    research_lint_report = lint_profile("dental-research-sharing")
    linkable_lint_report = lint_profile("dental-linkable-research")

    doctor_json = reports_dir / "doctor.json"
    safety_json = reports_dir / "safety-scan.json"
    release_json = reports_dir / "release-audit.json"
    release_html = reports_dir / "release-audit.html"
    policy_json = reports_dir / "policy-registry.json"
    policy_csv = reports_dir / "policy-registry.csv"
    policy_html = reports_dir / "policy-registry.html"
    confidentiality_json = reports_dir / "confidentiality-alignment.json"
    confidentiality_html = reports_dir / "confidentiality-alignment.html"
    capability_json = reports_dir / "capability-matrix.json"
    capability_html = reports_dir / "capability-matrix.html"
    competitor_json = reports_dir / "competitor-coverage.json"
    competitor_html = reports_dir / "competitor-coverage.html"
    objective_json = reports_dir / "objective-audit.json"
    objective_html = reports_dir / "objective-audit.html"
    basic_lint_json = reports_dir / "profile-lint-dental-basic.json"
    basic_lint_html = reports_dir / "profile-lint-dental-basic.html"
    research_lint_json = reports_dir / "profile-lint-dental-research-sharing.json"
    research_lint_html = reports_dir / "profile-lint-dental-research-sharing.html"
    linkable_lint_json = reports_dir / "profile-lint-dental-linkable-research.json"
    linkable_lint_html = reports_dir / "profile-lint-dental-linkable-research.html"
    write_json(doctor_json, model_to_dict(doctor_report))
    write_json(safety_json, model_to_dict(safety_report))
    write_json(release_json, model_to_dict(release_report))
    write_release_audit_html(release_html, release_report)
    write_json(policy_json, model_to_dict(policy_report))
    write_policy_registry_csv(policy_csv, policy_report)
    write_policy_registry_html(policy_html, policy_report)
    write_json(confidentiality_json, model_to_dict(confidentiality_report))
    write_confidentiality_alignment_html(confidentiality_html, confidentiality_report)
    write_json(capability_json, model_to_dict(capability_report))
    write_capability_matrix_html(capability_html, capability_report)
    write_json(competitor_json, model_to_dict(competitor_report))
    write_competitor_coverage_html(competitor_html, competitor_report)
    write_json(objective_json, model_to_dict(objective_report))
    write_objective_audit_html(objective_html, objective_report)
    write_json(basic_lint_json, model_to_dict(basic_lint_report))
    write_profile_lint_html(basic_lint_html, basic_lint_report)
    write_json(research_lint_json, model_to_dict(research_lint_report))
    write_profile_lint_html(research_lint_html, research_lint_report)
    write_json(linkable_lint_json, model_to_dict(linkable_lint_report))
    write_profile_lint_html(linkable_lint_html, linkable_lint_report)

    demo_result = run_demo_pipeline(demo_dir)
    quality_report = run_workflow_quality_gate(demo_dir)
    quality_json = demo_dir / "reports" / "quality-gate.json"
    quality_html = demo_dir / "reports" / "quality-gate.html"
    write_json(quality_json, model_to_dict(quality_report))
    write_workflow_quality_gate_html(quality_html, quality_report)

    workflow_report = run_workflow(
        repository_root / "recipes" / "dental-demo-workflow.yml",
        workflow_dir,
    )
    workflow_json = reports_dir / "workflow-run.json"
    workflow_html = reports_dir / "workflow-run.html"
    write_json(workflow_json, model_to_dict(workflow_report))
    write_workflow_html(workflow_html, workflow_report)

    regression_report = run_privacy_regression_suite(regression_dir)
    regression_json = reports_dir / "privacy-regression-suite.json"
    regression_html = reports_dir / "privacy-regression-suite.html"
    write_json(regression_json, model_to_dict(regression_report))
    write_privacy_regression_html(regression_html, regression_report)

    dashboard_json = reports_dir / "review-dashboard.json"
    dashboard_html = reports_dir / "review-dashboard.html"
    evidence_json = reports_dir / "evidence-bundle.json"
    evidence_html = reports_dir / "evidence-bundle.html"
    artifacts = [
        _artifact(
            output_dir,
            doctor_json,
            "Environment doctor",
            "quality",
            "Local runtime checks.",
        ),
        _artifact(
            output_dir,
            safety_json,
            "Repository safety scan",
            "safety",
            "Synthetic-only public repository safety gate.",
        ),
        _artifact(
            output_dir,
            release_json,
            "Release audit JSON",
            "release",
            "Machine-readable release-readiness checks.",
        ),
        _artifact(
            output_dir,
            release_html,
            "Release audit HTML",
            "release",
            "Human-readable release-readiness report.",
        ),
        _artifact(
            output_dir,
            dashboard_html,
            "Review dashboard HTML",
            "dashboard",
            "MacBook-friendly static dashboard for opening the strongest reports.",
        ),
        _artifact(
            output_dir,
            policy_html,
            "Policy registry HTML",
            "policy",
            "Human-readable DICOM privacy policy registry.",
        ),
        _artifact(
            output_dir,
            confidentiality_html,
            "DICOM confidentiality alignment HTML",
            "standards",
            "DICOM PS3.15-inspired profile alignment report.",
        ),
        _artifact(
            output_dir,
            capability_html,
            "Capability matrix HTML",
            "strategy",
            "Competitor-informed capability and evidence report.",
        ),
        _artifact(
            output_dir,
            competitor_html,
            "Competitor coverage HTML",
            "strategy",
            "Reference-tool coverage report with differentiators and boundaries.",
        ),
        _artifact(
            output_dir,
            objective_html,
            "Objective completion audit HTML",
            "strategy",
            "Requirement-level proof against the original competitor-learning objective.",
        ),
        _artifact(
            output_dir,
            basic_lint_html,
            "Basic profile lint HTML",
            "profile",
            "Configuration lint report for dental-basic.",
        ),
        _artifact(
            output_dir,
            research_lint_html,
            "Research profile lint HTML",
            "profile",
            "Configuration lint report for dental-research-sharing.",
        ),
        _artifact(
            output_dir,
            linkable_lint_html,
            "Linkable research profile lint HTML",
            "profile",
            "Configuration lint report for dental-linkable-research.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.summary_html),
            "Demo summary HTML",
            "demo",
            "One-command synthetic demo with embedded PNG previews.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.audit_chain_json),
            "Demo audit chain",
            "audit",
            "Tamper-evident hash chain for generated demo artifacts.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.deid_comparison_html),
            "De-identification comparison HTML",
            "comparison",
            "Before/after privacy policy comparison for synthetic DICOM metadata.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.confidentiality_alignment_html),
            "Demo DICOM confidentiality alignment HTML",
            "standards",
            "DICOM PS3.15-inspired alignment report from the one-command demo.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.profile_conformance_html),
            "Profile conformance HTML",
            "profile",
            "Post-anonymization verification against the selected profile.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.pixel_review_html),
            "Pixel review HTML",
            "pixel-review",
            "Human-readable burned-in annotation redaction review.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.package_path),
            "Encrypted package",
            "sharing",
            "Encrypted sharing package generated from anonymized synthetic DICOM files.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.package_receipt_html),
            "Package verification receipt",
            "sharing",
            "Human-readable verification receipt for the encrypted package.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.share_readiness_html),
            "Share readiness HTML",
            "sharing",
            "Final local gate for synthetic package sharing readiness.",
        ),
        _artifact(
            output_dir,
            Path(demo_result.deid_certificate_html),
            "De-identification certificate HTML",
            "certificate",
            "Portable certificate summarizing de-identification handoff evidence.",
        ),
        _artifact(
            output_dir,
            quality_html,
            "Workflow quality gate HTML",
            "quality",
            "Final reproducibility gate over demo privacy, pixel, package, and audit evidence.",
        ),
        _artifact(
            output_dir,
            workflow_json,
            "Workflow report JSON",
            "workflow",
            "Machine-readable staged YAML workflow result.",
        ),
        _artifact(
            output_dir,
            workflow_html,
            "Workflow report HTML",
            "workflow",
            "Human-readable staged YAML workflow result.",
        ),
        _artifact(
            output_dir,
            regression_html,
            "Privacy regression suite HTML",
            "quality",
            "Synthetic adversarial privacy regression evidence.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "remediation-plan.html",
            "Privacy remediation plan HTML",
            "planning",
            "Pre-anonymization metadata remediation plan from the staged workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "dcmodify-plan.html",
            "dcmodify plan HTML",
            "expert-review",
            "DCMTK dcmodify-style low-level operation plan from the workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "orthanc-plan.html",
            "Orthanc anonymization plan HTML",
            "integration",
            "Review-only Orthanc REST anonymization payload from the workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "confidentiality-alignment.html",
            "Workflow DICOM confidentiality alignment HTML",
            "standards",
            "DICOM PS3.15-inspired alignment report from the staged workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "profile-conformance.html",
            "Workflow profile conformance HTML",
            "profile",
            "Profile verification report from the staged workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "dicom-json.html",
            "DICOM JSON export HTML",
            "integration",
            "Orthanc-inspired safe metadata JSON export from the workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "filename-privacy.html",
            "Filename privacy scan HTML",
            "path-privacy",
            "Path-level privacy guardrail from the staged workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "pixel-risk.html",
            "Pixel risk scan HTML",
            "pixel-risk",
            "Conservative burned-in identifier triage from the staged workflow.",
        ),
        _artifact(
            output_dir,
            workflow_dir / "reports" / "residual-risk.html",
            "Residual privacy risk HTML",
            "risk-score",
            "100-point residual privacy risk summary from the staged workflow.",
        ),
        _artifact(
            output_dir,
            evidence_json,
            "Evidence bundle JSON",
            "evidence",
            "Machine-readable index for this evidence bundle.",
        ),
        _artifact(
            output_dir,
            evidence_html,
            "Evidence bundle HTML",
            "evidence",
            "Human-readable index for this evidence bundle.",
        ),
    ]

    result = EvidenceBundleResult(
        repository_root=str(repository_root),
        output_dir=str(output_dir),
        passed=(
            doctor_report.passed
            and safety_report.passed
            and release_report.passed
            and confidentiality_report.passed
            and capability_report.passed
            and competitor_report.passed
            and objective_report.passed
            and basic_lint_report.passed
            and research_lint_report.passed
            and linkable_lint_report.passed
            and demo_result.validation_passed
            and demo_result.audit_chain_passed
            and quality_report.passed
            and workflow_report.passed
            and regression_report.passed
        ),
        doctor_passed=doctor_report.passed,
        safety_passed=safety_report.passed,
        release_audit_passed=release_report.passed,
        demo_passed=demo_result.validation_passed and demo_result.audit_chain_passed,
        workflow_passed=workflow_report.passed,
        artifacts=artifacts,
    )
    write_json(evidence_json, model_to_dict(result))
    write_evidence_bundle_html(evidence_html, result)
    dashboard_report = build_review_dashboard_report(output_dir, dashboard_html, result)
    write_json(dashboard_json, model_to_dict(dashboard_report))
    write_review_dashboard_html(dashboard_html, dashboard_report)
    return result


def _artifact(
    output_dir: Path,
    path: Path,
    label: str,
    category: str,
    description: str,
) -> EvidenceArtifact:
    return EvidenceArtifact(
        label=label,
        category=category,
        path=_relative_path(output_dir, path),
        description=description,
    )


def _relative_path(output_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(output_dir))
    except ValueError:
        return str(path)
