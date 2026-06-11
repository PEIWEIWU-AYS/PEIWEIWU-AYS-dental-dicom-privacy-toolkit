from __future__ import annotations

from pathlib import Path

from ddpt.doctor import run_doctor
from ddpt.models import EvidenceArtifact, EvidenceBundleResult
from ddpt.pipeline import run_demo_pipeline
from ddpt.release import run_release_audit
from ddpt.reports import (
    model_to_dict,
    write_evidence_bundle_html,
    write_release_audit_html,
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

    doctor_json = reports_dir / "doctor.json"
    safety_json = reports_dir / "safety-scan.json"
    release_json = reports_dir / "release-audit.json"
    release_html = reports_dir / "release-audit.html"
    write_json(doctor_json, model_to_dict(doctor_report))
    write_json(safety_json, model_to_dict(safety_report))
    write_json(release_json, model_to_dict(release_report))
    write_release_audit_html(release_html, release_report)

    demo_result = run_demo_pipeline(demo_dir)

    workflow_report = run_workflow(
        repository_root / "recipes" / "dental-demo-workflow.yml",
        workflow_dir,
    )
    workflow_json = reports_dir / "workflow-run.json"
    workflow_html = reports_dir / "workflow-run.html"
    write_json(workflow_json, model_to_dict(workflow_report))
    write_workflow_html(workflow_html, workflow_report)

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
