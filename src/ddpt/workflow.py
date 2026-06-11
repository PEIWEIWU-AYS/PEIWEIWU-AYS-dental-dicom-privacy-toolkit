from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ddpt.anonymize import anonymize_dicom
from ddpt.audit_chain import create_audit_chain, verify_audit_chain
from ddpt.inspection import inspect_dicom
from ddpt.inventory import build_inventory, write_inventory_csv
from ddpt.models import WorkflowRunReport, WorkflowStepResult
from ddpt.pixels import parse_rectangle, redact_pixels
from ddpt.preview import render_dicom_preview
from ddpt.reports import (
    model_to_dict,
    write_audit_html,
    write_inspection_html,
    write_inventory_html,
)
from ddpt.sharing import create_package, verify_package
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
        verify_package(_path(root_dir, step["package"]), _optional_path(root_dir, step.get("key")))
        return []

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
