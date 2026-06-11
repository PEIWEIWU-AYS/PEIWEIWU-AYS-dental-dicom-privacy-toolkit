from __future__ import annotations

import csv
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pydicom
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from typer.testing import CliRunner

from ddpt.api import create_api_app
from ddpt.cli import app
from ddpt.sharing import create_package, verify_package

runner = CliRunner()


def test_full_synthetic_privacy_workflow(tmp_path: Path) -> None:
    source = tmp_path / "sample.dcm"
    inspect_json = tmp_path / "reports" / "inspect.json"
    inspect_html = tmp_path / "reports" / "inspect.html"
    anonymized = tmp_path / "outputs" / "sample.anonymized.dcm"
    audit_json = tmp_path / "reports" / "audit.json"
    audit_html = tmp_path / "reports" / "audit.html"
    validation_json = tmp_path / "reports" / "validation.json"
    redacted = tmp_path / "outputs" / "sample.redacted.dcm"
    redaction_audit = tmp_path / "reports" / "redaction.json"
    package = tmp_path / "share" / "package.ddpt"
    manifest = tmp_path / "share" / "manifest.json"
    key = tmp_path / "share" / "package.key"
    decrypted = tmp_path / "restored"

    result = runner.invoke(app, ["synthetic", str(source)])
    assert result.exit_code == 0, result.output
    assert source.exists()

    result = runner.invoke(
        app,
        [
            "inspect",
            str(source),
            "--json",
            str(inspect_json),
            "--html",
            str(inspect_html),
        ],
    )
    assert result.exit_code == 0, result.output
    assert inspect_json.exists()
    assert inspect_html.exists()
    inspection = json.loads(inspect_json.read_text())
    patient_name_finding = next(
        item for item in inspection["findings"] if item["keyword"] == "PatientName"
    )
    assert patient_name_finding["risk"] == "high"
    assert patient_name_finding["recommended_action"] == "replace"
    assert patient_name_finding["dicom_action_code"] == "D"
    source_dataset = pydicom.dcmread(source)

    result = runner.invoke(
        app,
        [
            "anonymize",
            str(source),
            "--out",
            str(anonymized),
            "--audit",
            str(audit_json),
            "--html",
            str(audit_html),
        ],
    )
    assert result.exit_code == 0, result.output
    assert audit_json.exists()
    assert audit_html.exists()

    dataset = pydicom.dcmread(anonymized)
    assert str(dataset.PatientName) == "ANONYMIZED^DENTAL"
    assert dataset.PatientID == "DDPT-SYNTHETIC-ID"
    assert dataset.PatientBirthDate == ""
    assert dataset.PatientAddress == ""
    assert dataset.StudyInstanceUID != source_dataset.StudyInstanceUID
    assert dataset.SeriesInstanceUID != source_dataset.SeriesInstanceUID
    assert dataset.SOPInstanceUID != source_dataset.SOPInstanceUID
    assert dataset.file_meta.MediaStorageSOPInstanceUID == dataset.SOPInstanceUID

    result = runner.invoke(app, ["validate", str(anonymized), "--json", str(validation_json)])
    assert result.exit_code == 0, result.output
    assert validation_json.exists()

    result = runner.invoke(app, ["validate", str(source)])
    assert result.exit_code == 1

    result = runner.invoke(
        app,
        [
            "redact-pixels",
            str(anonymized),
            "--out",
            str(redacted),
            "--rect",
            "1,0,1,1",
            "--audit",
            str(redaction_audit),
        ],
    )
    assert result.exit_code == 0, result.output
    assert redaction_audit.exists()
    redacted_dataset = pydicom.dcmread(redacted)
    assert int(dataset.pixel_array[0, 1]) == 64
    assert int(redacted_dataset.pixel_array[0, 1]) == 0

    result = runner.invoke(
        app,
        [
            "package",
            str(anonymized.parent),
            "--out",
            str(package),
            "--manifest",
            str(manifest),
            "--encrypt",
            "--key-out",
            str(key),
        ],
    )
    assert result.exit_code == 0, result.output
    assert package.exists()
    assert manifest.exists()
    assert key.exists()

    result = runner.invoke(app, ["verify", str(package), "--key", str(key)])
    assert result.exit_code == 0, result.output
    verified_manifest = verify_package(package, key)
    assert len(verified_manifest.entries) == 2

    result = runner.invoke(
        app,
        ["decrypt", str(package), "--out", str(decrypted), "--key", str(key)],
    )
    assert result.exit_code == 0, result.output
    assert (decrypted / "sample.anonymized.dcm").exists()


def test_anonymize_dry_run_previews_changes_without_writing_dicom(tmp_path: Path) -> None:
    source = tmp_path / "sample.dcm"
    audit_json = tmp_path / "reports" / "dry-run-audit.json"
    audit_html = tmp_path / "reports" / "dry-run-audit.html"
    missing_output = tmp_path / "outputs" / "should-not-exist.dcm"

    assert runner.invoke(app, ["synthetic", str(source)]).exit_code == 0

    result = runner.invoke(app, ["anonymize", str(source)])
    assert result.exit_code == 1
    assert "--out is required" in result.output

    result = runner.invoke(
        app,
        [
            "anonymize",
            str(source),
            "--dry-run",
            "--audit",
            str(audit_json),
            "--html",
            str(audit_html),
        ],
    )

    assert result.exit_code == 0, result.output
    assert audit_json.exists()
    assert audit_html.exists()
    assert not missing_output.exists()
    assert str(pydicom.dcmread(source).PatientName) == "SYNTHETIC^DENTAL"
    audit = json.loads(audit_json.read_text())
    assert audit["output_path"] == ""
    assert any(item["keyword"] == "PatientName" for item in audit["actions"])
    uid_actions = [
        item for item in audit["actions"] if item["action"] == "regenerate_uid"
    ]
    assert uid_actions
    assert all(item["after"] == "<generated-uid>" for item in uid_actions)


def test_demo_pipeline_command(tmp_path: Path) -> None:
    demo_dir = tmp_path / "demo"

    result = runner.invoke(app, ["demo", str(demo_dir)])

    assert result.exit_code == 0, result.output
    assert (demo_dir / "input" / "sample.synthetic.dcm").exists()
    assert (demo_dir / "reports" / "inventory.json").exists()
    assert (demo_dir / "reports" / "inventory.csv").exists()
    assert (demo_dir / "reports" / "inventory.html").exists()
    assert (demo_dir / "reports" / "input-preview.png").exists()
    assert (demo_dir / "reports" / "anonymized-preview.png").exists()
    assert (demo_dir / "reports" / "redacted-preview.png").exists()
    assert (demo_dir / "outputs" / "sample.anonymized.dcm").exists()
    assert (demo_dir / "outputs" / "sample.redacted.dcm").exists()
    assert (demo_dir / "reports" / "inspect.html").exists()
    assert (demo_dir / "reports" / "audit.html").exists()
    assert (demo_dir / "reports" / "validation.json").exists()
    assert (demo_dir / "reports" / "redaction.json").exists()
    assert (demo_dir / "reports" / "demo-summary.html").exists()
    assert (demo_dir / "reports" / "audit-chain.json").exists()
    assert (demo_dir / "reports" / "audit-chain-verify.json").exists()
    assert (demo_dir / "share" / "package.ddpt").exists()
    assert (demo_dir / "share" / "manifest.json").exists()
    assert (demo_dir / "share" / "package.key").exists()


def test_workflow_recipe_command_runs_multistage_pipeline(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflow-run"
    workflow_json = workflow_dir / "reports" / "workflow-run.json"
    workflow_html = workflow_dir / "reports" / "workflow-run.html"

    result = runner.invoke(
        app,
        [
            "workflow",
            "run",
            "recipes/dental-demo-workflow.yml",
            "--root",
            str(workflow_dir),
            "--json",
            str(workflow_json),
            "--html",
            str(workflow_html),
        ],
    )

    assert result.exit_code == 0, result.output
    assert workflow_json.exists()
    assert workflow_html.exists()
    assert (workflow_dir / "input" / "sample.synthetic.dcm").exists()
    assert (workflow_dir / "reports" / "inventory.json").exists()
    assert (workflow_dir / "reports" / "inspect.html").exists()
    assert (workflow_dir / "outputs" / "sample.anonymized.dcm").exists()
    assert (workflow_dir / "outputs" / "sample.redacted.dcm").exists()
    assert (workflow_dir / "share" / "package.ddpt").exists()
    assert (workflow_dir / "share" / "package.key").exists()
    assert (workflow_dir / "reports" / "audit-chain.json").exists()
    assert (workflow_dir / "reports" / "audit-chain-verify.json").exists()
    report = json.loads(workflow_json.read_text())
    assert report["passed"] is True
    assert [step["id"] for step in report["steps"]] == [
        "create-synthetic",
        "inventory-input",
        "inspect-input",
        "anonymize",
        "validate",
        "preview-anonymized",
        "redact-known-pixels",
        "package",
        "verify-package",
        "audit-chain",
        "audit-verify",
    ]
    html = workflow_html.read_text()
    assert "Dental DICOM Workflow Report" in html
    assert "create-synthetic" in html
    assert "audit-chain" in html


def test_workflow_recipe_accepts_relative_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipe_path = Path("recipes/dental-demo-workflow.yml").resolve()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        [
            "workflow",
            "run",
            str(recipe_path),
            "--root",
            "relative-workflow",
                "--json",
                "relative-workflow/reports/workflow-run.json",
                "--html",
                "relative-workflow/reports/workflow-run.html",
            ],
        )

    assert result.exit_code == 0, result.output
    report = json.loads(Path("relative-workflow/reports/workflow-run.json").read_text())
    assert report["passed"] is True
    assert Path("relative-workflow/reports/audit-chain-verify.json").exists()
    assert Path("relative-workflow/reports/workflow-run.html").exists()


def test_inventory_command_exports_safe_directory_report(tmp_path: Path) -> None:
    input_dir = tmp_path / "inventory-input"
    nested_dir = input_dir / "nested"
    first = input_dir / "first.dcm"
    second = nested_dir / "second.dicom"
    broken = input_dir / "broken.dcm"
    inventory_json = tmp_path / "reports" / "inventory.json"
    inventory_csv = tmp_path / "reports" / "inventory.csv"
    inventory_html = tmp_path / "reports" / "inventory.html"
    nested_dir.mkdir(parents=True)

    assert runner.invoke(app, ["synthetic", str(first)]).exit_code == 0
    assert runner.invoke(app, ["synthetic", str(second)]).exit_code == 0
    broken.write_text("not a dicom file", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "inventory",
            str(input_dir),
            "--json",
            str(inventory_json),
            "--csv",
            str(inventory_csv),
            "--html",
            str(inventory_html),
        ],
    )

    assert result.exit_code == 0, result.output
    assert inventory_json.exists()
    assert inventory_csv.exists()
    assert inventory_html.exists()
    report = json.loads(inventory_json.read_text())
    assert report["total_files"] == 3
    assert report["readable_files"] == 2
    assert report["unreadable_files"] == 1
    assert report["modalities"] == {"DX": 2}
    assert report["high_risk_tags"] >= 6
    assert "SYNTHETIC^DENTAL" not in inventory_json.read_text()
    readable = [item for item in report["files"] if item["readable"]]
    assert all(item["patient_name_present"] for item in readable)
    assert all(item["study_instance_uid_hash"] for item in readable)
    assert any(item["error"] for item in report["files"])

    with inventory_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    first_row = next(row for row in rows if row["path"] == "first.dcm")
    assert first_row["patient_name_present"] == "True"


def test_preview_command_exports_png_and_metadata(tmp_path: Path) -> None:
    source = tmp_path / "sample.dcm"
    preview_png = tmp_path / "reports" / "sample-preview.png"
    preview_json = tmp_path / "reports" / "sample-preview.json"

    assert runner.invoke(app, ["synthetic", str(source)]).exit_code == 0
    result = runner.invoke(
        app,
        [
            "preview",
            str(source),
            "--out",
            str(preview_png),
            "--json",
            str(preview_json),
        ],
    )

    assert result.exit_code == 0, result.output
    assert preview_png.exists()
    assert preview_json.exists()
    report = json.loads(preview_json.read_text())
    assert report["rows"] == 2
    assert report["columns"] == 2
    assert report["rendered_width"] >= report["columns"]
    assert report["rendered_height"] >= report["rows"]
    with Image.open(preview_png) as image:
        assert image.mode == "L"
        assert image.size == (report["rendered_width"], report["rendered_height"])


def test_redaction_plan_commands_and_plan_based_redaction(tmp_path: Path) -> None:
    source = tmp_path / "sample.dcm"
    redacted = tmp_path / "outputs" / "sample.plan-redacted.dcm"
    audit_json = tmp_path / "reports" / "redaction-plan-audit.json"
    plan_json = tmp_path / "reports" / "redaction-plan.json"
    custom_plan = tmp_path / "plans" / "custom-redaction.yml"

    assert runner.invoke(app, ["synthetic", str(source)]).exit_code == 0

    result = runner.invoke(app, ["redaction-plan", "init", str(custom_plan)])
    assert result.exit_code == 0, result.output
    assert custom_plan.exists()

    result = runner.invoke(app, ["redaction-plan", "init", str(custom_plan)])
    assert result.exit_code == 1

    result = runner.invoke(
        app,
        [
            "redaction-plan",
            "show",
            "profiles/dental-pixel-redaction.yml",
            "--json",
            str(plan_json),
        ],
    )
    assert result.exit_code == 0, result.output
    plan = json.loads(plan_json.read_text())
    assert plan["name"] == "dental-burned-in-banner"
    assert plan["regions"][0]["unit"] == "percent"

    result = runner.invoke(
        app,
        [
            "redact-pixels",
            str(source),
            "--out",
            str(redacted),
            "--plan",
            "profiles/dental-pixel-redaction.yml",
            "--audit",
            str(audit_json),
        ],
    )

    assert result.exit_code == 0, result.output
    assert redacted.exists()
    assert audit_json.exists()
    source_dataset = pydicom.dcmread(source)
    redacted_dataset = pydicom.dcmread(redacted)
    assert int(source_dataset.pixel_array[0, 1]) == 64
    assert int(redacted_dataset.pixel_array[0, 1]) == 0
    audit = json.loads(audit_json.read_text())
    assert audit["rectangles"][0] == {"x": 0, "y": 0, "width": 2, "height": 1}


def test_tag_commands_dump_set_blank_and_delete(tmp_path: Path) -> None:
    source = tmp_path / "sample.dcm"
    dump_json = tmp_path / "reports" / "tag-dump.json"
    set_output = tmp_path / "outputs" / "tag-set.dcm"
    set_audit = tmp_path / "reports" / "tag-set.json"
    blank_output = tmp_path / "outputs" / "tag-blank.dcm"
    blank_audit = tmp_path / "reports" / "tag-blank.json"
    delete_output = tmp_path / "outputs" / "tag-delete.dcm"
    delete_audit = tmp_path / "reports" / "tag-delete.json"
    insert_output = tmp_path / "outputs" / "tag-insert.dcm"
    insert_audit = tmp_path / "reports" / "tag-insert.json"

    assert runner.invoke(app, ["synthetic", str(source)]).exit_code == 0

    result = runner.invoke(app, ["tag", "dump", str(source), "--json", str(dump_json)])
    assert result.exit_code == 0, result.output
    dump = json.loads(dump_json.read_text())
    assert any(item["keyword"] == "PatientName" for item in dump["tags"])
    assert not any(item["keyword"] == "PixelData" for item in dump["tags"])

    result = runner.invoke(
        app,
        [
            "tag",
            "set",
            str(source),
            "PatientName",
            "LOWLEVEL^EDIT",
            "--out",
            str(set_output),
            "--audit",
            str(set_audit),
        ],
    )
    assert result.exit_code == 0, result.output
    assert str(pydicom.dcmread(set_output).PatientName) == "LOWLEVEL^EDIT"
    set_report = json.loads(set_audit.read_text())
    assert set_report["actions"][0]["action"] == "set"
    assert set_report["actions"][0]["before"] == "SYNTHETIC^DENTAL"

    result = runner.invoke(
        app,
        [
            "tag",
            "blank",
            str(set_output),
            "0010,1040",
            "--out",
            str(blank_output),
            "--audit",
            str(blank_audit),
        ],
    )
    assert result.exit_code == 0, result.output
    assert pydicom.dcmread(blank_output).PatientAddress == ""
    blank_report = json.loads(blank_audit.read_text())
    assert blank_report["actions"][0]["keyword"] == "PatientAddress"

    result = runner.invoke(
        app,
        [
            "tag",
            "delete",
            str(blank_output),
            "PatientTelephoneNumbers",
            "--out",
            str(delete_output),
            "--audit",
            str(delete_audit),
        ],
    )
    assert result.exit_code == 0, result.output
    deleted_dataset = pydicom.dcmread(delete_output)
    assert "PatientTelephoneNumbers" not in deleted_dataset
    delete_report = json.loads(delete_audit.read_text())
    assert delete_report["actions"][0]["action"] == "delete"
    assert delete_report["actions"][0]["after"] == ""

    result = runner.invoke(
        app,
        [
            "tag",
            "set",
            str(delete_output),
            "ImageComments",
            "Synthetic low-level insert",
            "--out",
            str(insert_output),
            "--audit",
            str(insert_audit),
        ],
    )
    assert result.exit_code == 0, result.output
    assert pydicom.dcmread(insert_output).ImageComments == "Synthetic low-level insert"
    insert_report = json.loads(insert_audit.read_text())
    assert insert_report["actions"][0]["existed_before"] is False


def test_local_api_workflow_and_path_safety(tmp_path: Path) -> None:
    source = tmp_path / "input" / "api.synthetic.dcm"
    anonymized = "outputs/api.anonymized.dcm"
    preview_png = "reports/api-preview.png"

    assert runner.invoke(app, ["synthetic", str(source)]).exit_code == 0
    client = TestClient(create_api_app(tmp_path))

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True

    response = client.post("/inventory", json={"path": "input"})
    assert response.status_code == 200
    inventory = response.json()
    assert inventory["total_files"] == 1
    assert inventory["readable_files"] == 1

    response = client.post("/inspect", json={"path": "input/api.synthetic.dcm"})
    assert response.status_code == 200
    inspection = response.json()
    assert inspection["patient_name_present"] is True

    response = client.post(
        "/anonymize",
        json={
            "input_path": "input/api.synthetic.dcm",
            "output_path": anonymized,
            "profile": "dental-basic",
        },
    )
    assert response.status_code == 200
    audit = response.json()
    assert audit["actions"]
    assert pydicom.dcmread(tmp_path / anonymized).PatientID == "DDPT-SYNTHETIC-ID"

    response = client.post("/validate", json={"path": anonymized})
    assert response.status_code == 200
    assert response.json()["passed"] is True

    response = client.post(
        "/preview",
        json={"input_path": anonymized, "output_path": preview_png},
    )
    assert response.status_code == 200
    assert (tmp_path / preview_png).exists()

    response = client.post("/inspect", json={"path": "../outside.dcm"})
    assert response.status_code == 400


def test_doctor_command_reports_environment(tmp_path: Path) -> None:
    doctor_json = tmp_path / "reports" / "doctor.json"

    result = runner.invoke(app, ["doctor", "--json", str(doctor_json)])

    assert result.exit_code == 0, result.output
    assert doctor_json.exists()
    report = json.loads(doctor_json.read_text())
    assert report["passed"] is True
    check_names = {item["name"] for item in report["checks"]}
    assert "python-version" in check_names
    assert "module:pydicom" in check_names
    assert "module:PIL" in check_names
    assert "module:fastapi" in check_names
    assert "module:uvicorn" in check_names


def test_safety_scan_passes_current_repository(tmp_path: Path) -> None:
    safety_json = tmp_path / "reports" / "safety.json"

    result = runner.invoke(app, ["safety", "scan", ".", "--json", str(safety_json)])

    assert result.exit_code == 0, result.output
    report = json.loads(safety_json.read_text())
    assert report["passed"] is True
    assert report["findings"] == []
    assert report["scanned_files"] > 0


def test_safety_scan_flags_private_material(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Safe public docs\n", encoding="utf-8")
    (tmp_path / "examples" / "synthetic-dicom").mkdir(parents=True)
    (tmp_path / "examples" / "synthetic-dicom" / "synthetic-example.dcm").write_bytes(
        b"synthetic-placeholder"
    )
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "real-patient.dcm").write_bytes(b"not public")
    (tmp_path / "clinic-exports").mkdir()
    (tmp_path / "clinic-exports" / "appointments.csv").write_text(
        "name,phone\nPatient,555-0100\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "generated-preview.png").write_bytes(b"ignored generated file")
    safety_json = tmp_path / "safety.json"

    result = runner.invoke(app, ["safety", "scan", str(tmp_path), "--json", str(safety_json)])

    assert result.exit_code == 1
    report = json.loads(safety_json.read_text())
    assert report["passed"] is False
    finding_paths = {item["path"] for item in report["findings"]}
    assert ".env" in finding_paths
    assert "private/real-patient.dcm" in finding_paths
    assert "clinic-exports/appointments.csv" in finding_paths
    assert "examples/synthetic-dicom/synthetic-example.dcm" not in finding_paths
    assert "reports/generated-preview.png" not in finding_paths


def test_audit_chain_detects_tampering(tmp_path: Path) -> None:
    demo_dir = tmp_path / "demo"
    chain_json = demo_dir / "reports" / "audit-chain.json"
    verify_json = demo_dir / "reports" / "manual-chain-verify.json"

    result = runner.invoke(app, ["demo", str(demo_dir)])
    assert result.exit_code == 0, result.output

    result = runner.invoke(app, ["audit", "verify", str(chain_json), "--json", str(verify_json)])
    assert result.exit_code == 0, result.output
    assert json.loads(verify_json.read_text())["passed"] is True

    (demo_dir / "reports" / "validation.json").write_text('{"tampered": true}')

    result = runner.invoke(app, ["audit", "verify", str(chain_json)])
    assert result.exit_code == 1
    assert "mismatch" in result.output


def test_batch_workflow_command(tmp_path: Path) -> None:
    input_dir = tmp_path / "batch-input"
    nested_dir = input_dir / "nested"
    output_dir = tmp_path / "batch-output"
    first = input_dir / "first.dcm"
    second = nested_dir / "second.dicom"
    nested_dir.mkdir(parents=True)

    assert runner.invoke(app, ["synthetic", str(first)]).exit_code == 0
    assert runner.invoke(app, ["synthetic", str(second)]).exit_code == 0

    result = runner.invoke(app, ["batch", str(input_dir), "--out", str(output_dir)])

    assert result.exit_code == 0, result.output
    assert (output_dir / "dicom" / "first.anonymized.dcm").exists()
    assert (output_dir / "dicom" / "nested" / "second.anonymized.dcm").exists()
    assert (output_dir / "batch-summary.json").exists()
    assert (output_dir / "batch-summary.html").exists()
    summary = json.loads((output_dir / "batch-summary.json").read_text())
    assert summary["total_files"] == 2
    assert summary["processed_files"] == 2
    assert summary["failed_files"] == 0
    assert summary["validation_failures"] == 0


def test_demo_asset_script(tmp_path: Path) -> None:
    output_dir = tmp_path / "script-demo"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_demo_assets.py",
            "--out",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Validation passed: True" in result.stdout
    assert (output_dir / "reports" / "demo-summary.html").exists()
    assert (output_dir / "reports" / "audit-chain.json").exists()
    assert (output_dir / "share" / "package.ddpt").exists()


def test_profile_commands(tmp_path: Path) -> None:
    profile_json = tmp_path / "profile.json"
    coverage_json = tmp_path / "coverage.json"
    custom_profile = tmp_path / "custom-profile.yml"
    custom_source = tmp_path / "custom-source.dcm"
    custom_output = tmp_path / "custom-output.dcm"

    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0, result.output
    assert "dental-basic" in result.output

    result = runner.invoke(app, ["profile", "show", "dental-basic", "--json", str(profile_json)])
    assert result.exit_code == 0, result.output
    assert profile_json.exists()
    assert "PatientName" in profile_json.read_text()

    result = runner.invoke(
        app,
        ["profile", "coverage", "dental-basic", "--json", str(coverage_json)],
    )
    assert result.exit_code == 0, result.output
    coverage = json.loads(coverage_json.read_text())
    assert coverage["high_risk_uncovered"] == []
    assert coverage["medium_risk_uncovered"] == []
    assert coverage["covered_items"] == coverage["total_items"]

    result = runner.invoke(app, ["profile", "init", str(custom_profile)])
    assert result.exit_code == 0, result.output
    assert custom_profile.exists()

    result = runner.invoke(app, ["profile", "init", str(custom_profile)])
    assert result.exit_code == 1

    result = runner.invoke(
        app,
        ["profile", "show", str(custom_profile), "--json", str(tmp_path / "custom.json")],
    )
    assert result.exit_code == 0, result.output

    result = runner.invoke(app, ["synthetic", str(custom_source)])
    assert result.exit_code == 0, result.output
    result = runner.invoke(
        app,
        [
            "anonymize",
            str(custom_source),
            "--out",
            str(custom_output),
            "--profile",
            str(custom_profile),
        ],
    )
    assert result.exit_code == 0, result.output
    assert pydicom.dcmread(custom_output).PatientID == "DDPT-SYNTHETIC-ID"


def test_package_rejects_empty_directory(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(ValueError, match="No files found"):
        create_package(empty, tmp_path / "share" / "empty.ddpt")


def test_verify_rejects_unsafe_zip_path(tmp_path: Path) -> None:
    package = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("../escape.txt", "bad")
        archive.writestr(
            "manifest.json",
            '{"package_name":"unsafe.zip","encrypted":false,"entries":[]}',
        )

    with pytest.raises(ValueError, match="Unsafe path"):
        verify_package(package)
