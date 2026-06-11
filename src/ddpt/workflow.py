from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ddpt.anonymize import anonymize_dicom
from ddpt.audit_chain import create_audit_chain, verify_audit_chain
from ddpt.certificate import build_deidentification_certificate
from ddpt.confidentiality import build_confidentiality_alignment
from ddpt.dcmodify_plan import build_dcmodify_plan, write_dcmodify_script
from ddpt.deid_compare import compare_deidentification
from ddpt.dicom_json import export_dicom_json
from ddpt.filename_privacy import scan_filename_privacy
from ddpt.inspection import inspect_dicom
from ddpt.intake import triage_clinic_export
from ddpt.inventory import build_inventory, write_inventory_csv
from ddpt.models import WorkflowRunReport, WorkflowStepResult
from ddpt.orthanc_plan import build_orthanc_anonymize_plan
from ddpt.pixel_review import create_pixel_review
from ddpt.pixel_risk import scan_pixel_risk
from ddpt.pixels import parse_rectangle, redact_pixels
from ddpt.preview import render_dicom_preview
from ddpt.profile_verify import verify_profile_conformance
from ddpt.quality_gate import run_workflow_quality_gate
from ddpt.reference_export import build_reference_tool_export_pack
from ddpt.remediation import build_privacy_remediation_plan
from ddpt.reports import (
    model_to_dict,
    write_audit_html,
    write_clinic_export_intake_html,
    write_confidentiality_alignment_html,
    write_dcmodify_plan_html,
    write_deid_certificate_html,
    write_deid_comparison_html,
    write_dicom_json_html,
    write_filename_privacy_html,
    write_inspection_html,
    write_inventory_html,
    write_orthanc_plan_html,
    write_package_receipt_html,
    write_pixel_review_html,
    write_pixel_risk_scan_html,
    write_privacy_remediation_html,
    write_profile_conformance_html,
    write_reference_tool_export_html,
    write_residual_risk_html,
    write_share_readiness_html,
    write_workflow_quality_gate_html,
)
from ddpt.residual_risk import score_residual_privacy_risk
from ddpt.share_readiness import run_share_readiness
from ddpt.sharing import create_package, create_verification_receipt
from ddpt.synthetic import create_synthetic_dicom
from ddpt.utils import write_json
from ddpt.validation import validate_anonymized_dicom


def run_workflow(recipe_path: Path, root_dir: Path) -> WorkflowRunReport:
    recipe = _load_recipe(recipe_path)
    root_dir = root_dir.resolve()
    root_dir.mkdir(parents=True, exist_ok=True)
    results: list[WorkflowStepResult] = []

    for index, step in enumerate(recipe["steps"], start=1):
        step_id = str(step.get("id") or f"step-{index}")
        action = str(step["action"])
        try:
            artifacts = _run_step(action, step, root_dir)
            results.append(
                WorkflowStepResult(
                    id=step_id,
                    action=action,
                    passed=True,
                    message="completed",
                    artifacts=[str(path.relative_to(root_dir)) for path in artifacts],
                )
            )
        except Exception as exc:
            results.append(
                WorkflowStepResult(
                    id=step_id,
                    action=action,
                    passed=False,
                    message=str(exc),
                )
            )
            break

    passed = all(step.passed for step in results) and len(results) == len(recipe["steps"])
    return WorkflowRunReport(
        recipe_path=str(recipe_path),
        root_dir=str(root_dir),
        name=str(recipe.get("name", recipe_path.stem)),
        passed=passed,
        steps=results,
    )


def _load_recipe(recipe_path: Path) -> dict[str, Any]:
    data = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Workflow recipe must contain a mapping")
    if not isinstance(data.get("steps"), list) or not data["steps"]:
        raise ValueError("Workflow recipe must contain at least one step")
    return data


def _run_step(action: str, step: dict[str, Any], root_dir: Path) -> list[Path]:
    if action == "synthetic":
        output = _path(root_dir, step["output"])
        create_synthetic_dicom(
            output,
            patient_name=str(step.get("patient_name", "SYNTHETIC^DENTAL")),
            patient_id=str(step.get("patient_id", "SYNTHETIC-001")),
            modality=str(step.get("modality", "DX")),
            study_description=str(step.get("study_description", "Synthetic Dental Radiograph")),
        )
        return [output]

    if action == "inventory":
        input_dir = _path(root_dir, step["input_dir"])
        report = build_inventory(input_dir, recursive=bool(step.get("recursive", True)))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("csv"):
            csv_path = _path(root_dir, step["csv"])
            write_inventory_csv(csv_path, report)
            artifacts.append(csv_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_inventory_html(html_path, report)
            artifacts.append(html_path)
        return artifacts

    if action == "filename-scan":
        report = scan_filename_privacy(
            _path(root_dir, step["input"]),
            recursive=bool(step.get("recursive", True)),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_filename_privacy_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Filename privacy scan requires review")
        return artifacts

    if action == "intake-triage":
        report = triage_clinic_export(
            _path(root_dir, step["input"]),
            recursive=bool(step.get("recursive", True)),
            max_archive_member_bytes=int(
                step.get("max_archive_member_bytes", 16 * 1024 * 1024)
            ),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_clinic_export_intake_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed and bool(step.get("require_pass", True)):
            raise ValueError("Clinic export intake triage requires review")
        return artifacts

    if action == "inspect":
        report = inspect_dicom(_path(root_dir, step["input"]))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_inspection_html(html_path, report)
            artifacts.append(html_path)
        return artifacts

    if action == "dicom-json-export":
        report = export_dicom_json(
            _path(root_dir, step["input"]),
            include_values=bool(step.get("include_values", False)),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_dicom_json_html(html_path, report)
            artifacts.append(html_path)
        return artifacts

    if action == "remediation-plan":
        report = build_privacy_remediation_plan(
            _path(root_dir, step["input"]),
            profile=str(step.get("profile", "dental-basic")),
            recursive=bool(step.get("recursive", True)),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_privacy_remediation_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Privacy remediation plan requires review")
        return artifacts

    if action == "confidentiality-alignment":
        report = build_confidentiality_alignment(str(step.get("profile", "dental-basic")))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_confidentiality_alignment_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Confidentiality alignment failed")
        return artifacts

    if action == "dcmodify-plan":
        report = build_dcmodify_plan(
            _path(root_dir, step["input"]),
            profile=str(step.get("profile", "dental-basic")),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_dcmodify_plan_html(html_path, report)
            artifacts.append(html_path)
        if step.get("script"):
            script_path = _path(root_dir, step["script"])
            write_dcmodify_script(script_path, report)
            artifacts.append(script_path)
        return artifacts

    if action == "orthanc-plan":
        report = build_orthanc_anonymize_plan(
            _path(root_dir, step["input"]),
            profile=str(step.get("profile", "dental-basic")),
            resource_id=str(step.get("resource_id", "<orthanc-resource-id>")),
            orthanc_base_url=str(step.get("base_url", "http://localhost:8042")),
            dicom_version=str(step.get("dicom_version", "2023b")),
            force=bool(step.get("force", True)),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_orthanc_plan_html(html_path, report)
            artifacts.append(html_path)
        return artifacts

    if action == "reference-tool-export":
        report = build_reference_tool_export_pack(
            _path(root_dir, step["input"]),
            _path(root_dir, step["out"]),
            profile=str(step.get("profile", "dental-basic")),
            resource_id=str(step.get("resource_id", "<orthanc-resource-id>")),
            orthanc_base_url=str(step.get("base_url", "http://localhost:8042")),
        )
        artifacts = [Path(artifact.path) for artifact in report.artifacts]
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_reference_tool_export_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Reference tool export pack failed")
        return artifacts

    if action == "anonymize":
        output = _path(root_dir, step["output"])
        audit = anonymize_dicom(
            _path(root_dir, step["input"]),
            output,
            str(step.get("profile", "dental-basic")),
        )
        artifacts = [output]
        if step.get("audit"):
            audit_path = _path(root_dir, step["audit"])
            write_json(audit_path, model_to_dict(audit))
            artifacts.append(audit_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_audit_html(html_path, audit)
            artifacts.append(html_path)
        return artifacts

    if action == "validate":
        report = validate_anonymized_dicom(_path(root_dir, step["input"]))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if not report.passed:
            raise ValueError("Validation failed")
        return artifacts

    if action == "profile-verify":
        report = verify_profile_conformance(
            _path(root_dir, step["source"]),
            _path(root_dir, step["anonymized"]),
            profile_name=str(step.get("profile", "dental-basic")),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_profile_conformance_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Profile conformance failed")
        return artifacts

    if action == "compare-deid":
        report = compare_deidentification(
            _path(root_dir, step["source"]),
            _path(root_dir, step["anonymized"]),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_deid_comparison_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("De-identification comparison failed")
        return artifacts

    if action == "preview":
        output = _path(root_dir, step["output"])
        report = render_dicom_preview(
            _path(root_dir, step["input"]),
            output,
            max_size=int(step.get("max_size", 512)),
        )
        artifacts = [output]
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        return artifacts

    if action == "pixel-risk-scan":
        report = scan_pixel_risk(_path(root_dir, step["input"]))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_pixel_risk_scan_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Pixel risk scan requires review")
        return artifacts

    if action == "redact-pixels":
        rectangles = [parse_rectangle(value) for value in step.get("rects", [])]
        output = _path(root_dir, step["output"])
        audit = redact_pixels(
            _path(root_dir, step["input"]),
            output,
            rectangles,
            fill_value=int(step.get("fill_value", 0)),
        )
        artifacts = [output]
        if step.get("audit"):
            audit_path = _path(root_dir, step["audit"])
            write_json(audit_path, model_to_dict(audit))
            artifacts.append(audit_path)
        return artifacts

    if action == "pixel-review":
        rectangles = [parse_rectangle(value) for value in step.get("rects", [])]
        report = create_pixel_review(
            _path(root_dir, step["input"]),
            _path(root_dir, step["out_dir"]),
            rectangles=rectangles,
            plan_path=_optional_path(root_dir, step.get("plan")),
            fill_value=int(step.get("fill_value", 0)),
            max_size=int(step.get("max_size", 512)),
        )
        artifacts = [
            Path(report.original_preview_png),
            Path(report.overlay_preview_png),
            Path(report.redacted_preview_png),
        ]
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_pixel_review_html(html_path, report)
            artifacts.append(html_path)
        return artifacts

    if action == "package":
        output = _path(root_dir, step["output"])
        manifest_path = _optional_path(root_dir, step.get("manifest"))
        key_path = _optional_path(root_dir, step.get("key_out"))
        create_package(
            _path(root_dir, step["input_dir"]),
            output,
            manifest_path=manifest_path,
            encrypt=bool(step.get("encrypt", False)),
            key_output=key_path,
        )
        return [path for path in [output, manifest_path, key_path] if path is not None]

    if action == "verify-package":
        receipt = create_verification_receipt(
            _path(root_dir, step["package"]),
            _optional_path(root_dir, step.get("key")),
        )
        artifacts = []
        if step.get("receipt"):
            receipt_path = _path(root_dir, step["receipt"])
            write_json(receipt_path, model_to_dict(receipt))
            artifacts.append(receipt_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_package_receipt_html(html_path, receipt)
            artifacts.append(html_path)
        if not receipt.passed:
            raise ValueError("Package verification failed")
        return artifacts

    if action == "audit-chain":
        output = _path(root_dir, step["output"])
        create_audit_chain(
            _path(root_dir, step.get("root", ".")),
            output,
            include_key_files=bool(step.get("include_keys", False)),
        )
        return [output]

    if action == "audit-verify":
        verification = verify_audit_chain(_path(root_dir, step["manifest"]))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(verification))
            artifacts.append(json_path)
        if not verification.passed:
            raise ValueError("Audit chain verification failed")
        return artifacts

    if action == "share-readiness":
        report = run_share_readiness(_path(root_dir, step.get("root", ".")))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_share_readiness_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Share readiness failed")
        return artifacts

    if action == "certificate":
        certificate = build_deidentification_certificate(
            _path(root_dir, step.get("root", "."))
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(certificate))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_deid_certificate_html(html_path, certificate)
            artifacts.append(html_path)
        if not certificate.passed:
            raise ValueError("De-identification certificate failed")
        return artifacts

    if action == "quality-gate":
        report = run_workflow_quality_gate(
            _path(root_dir, step.get("root", ".")),
            workflow_report_path=_optional_path(root_dir, step.get("workflow_report")),
        )
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_workflow_quality_gate_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Workflow quality gate failed")
        return artifacts

    if action == "risk-score":
        report = score_residual_privacy_risk(_path(root_dir, step.get("root", ".")))
        artifacts = []
        if step.get("json"):
            json_path = _path(root_dir, step["json"])
            write_json(json_path, model_to_dict(report))
            artifacts.append(json_path)
        if step.get("html"):
            html_path = _path(root_dir, step["html"])
            write_residual_risk_html(html_path, report)
            artifacts.append(html_path)
        if not report.passed:
            raise ValueError("Residual privacy risk score failed")
        return artifacts

    raise ValueError(f"Unsupported workflow action: {action}")


def _path(root_dir: Path, value: str | Path) -> Path:
    candidate = (root_dir / Path(value)).resolve()
    root = root_dir.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Workflow path escapes root: {value}") from exc
    return candidate


def _optional_path(root_dir: Path, value: Any) -> Path | None:
    if value in {None, ""}:
        return None
    return _path(root_dir, str(value))
