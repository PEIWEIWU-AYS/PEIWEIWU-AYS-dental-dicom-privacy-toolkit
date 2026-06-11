from __future__ import annotations

from pathlib import Path

from ddpt.capability import build_capability_matrix
from ddpt.dashboard import build_review_dashboard_report
from ddpt.doctor import run_doctor
from ddpt.models import EvidenceArtifact, EvidenceBundleResult
from ddpt.pipeline import run_demo_pipeline
from ddpt.policy import policy_registry_report, write_policy_registry_csv
from ddpt.profiles import lint_profile
from ddpt.release import run_release_audit
from ddpt.reports import (
    model_to_dict,
    write_capability_matrix_html,
    write_evidence_bundle_html,
    write_policy_registry_html,
    write_profile_lint_html,
    write_release_audit_html,
    write_review_dashboard_html,
    write_workflow_html,
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

    output_dir.mkdir(parents=True, exist_ok=True)

    doctor_report = run_doctor()
    safety_report = scan_repository_safety(repository_root)
    release_report = run_release_audit(repository_root)
    policy_report = policy_registry_report()
    capability_report = build_capability_matrix(repository_root)
    basic_lint_report = lint_profile("dental-basic")
    research_lint_report = lint_profile("dental-research-sharing")

    doctor_json = reports_dir / "doctor.json"
    safety_json = reports_dir / "safety-scan.json"
    release_json = reports_dir / "release-audit.json"
    release_html = reports_dir / "release-audit.html"
    policy_json = reports_dir / "policy-registry.json"
    policy_csv = reports_dir / "policy-registry.csv"
    policy_html = reports_dir / "policy-registry.html"
    capability_json = reports_dir / "capability-matrix.json"
    capability_html = reports_dir / "capability-matrix.html"
    basic_lint_json = reports_dir / "profile-lint-dental-basic.json"
    basic_lint_html = reports_dir / "profile-lint-dental-basic.html"
    research_lint_json = reports_dir / "profile-lint-dental-research-sharing.json"
    research_lint_html = reports_dir / "profile-lint-dental-research-sharing.html"
    write_json(doctor_json, model_to_dict(doctor_report))
    write_json(safety_json, model_to_dict(safety_report))
    write_json(release_json, model_to_dict(release_report))
    write_release_audit_html(release_html, release_report)
    write_json(policy_json, model_to_dict(policy_report))
    write_policy_registry_csv(policy_csv, policy_report)
    write_policy_registry_html(policy_html, policy_report)
    write_json(capability_json, model_to_dict(capability_report))
    write_capability_matrix_html(capability_html, capability_report)
    write_json(basic_lint_json, model_to_dict(basic_lint_report))
    write_profile_lint_html(basic_lint_html, basic_lint_report)
    write_json(research_lint_json, model_to_dict(research_lint_report))
    write_profile_lint_html(research_lint_html, research_lint_report)

    demo_result = run_demo_pipeline(demo_dir)

    workflow_report = run_workflow(
        repository_root / "recipes" / "dental-demo-workflow.yml",
        workflow_dir,
    )
    workflow_json = reports_dir / "workflow-run.json"
    workflow_html = reports_dir / "workflow-run.html"
    write_json(workflow_json, model_to_dict(workflow_report))
    write_workflow_html(workflow_html, workflow_report)

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
            capability_html,
            "Capability matrix HTML",
            "strategy",
            "Competitor-informed capability and evidence report.",
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
            and capability_report.passed
            and basic_lint_report.passed
            and research_lint_report.passed
            and demo_result.validation_passed
            and demo_result.audit_chain_passed
            and workflow_report.passed
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
