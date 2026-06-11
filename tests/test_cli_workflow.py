from __future__ import annotations

import csv
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pydicom
import pytest
from typer.testing import CliRunner

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


def test_demo_pipeline_command(tmp_path: Path) -> None:
    demo_dir = tmp_path / "demo"

    result = runner.invoke(app, ["demo", str(demo_dir)])

    assert result.exit_code == 0, result.output
    assert (demo_dir / "input" / "sample.synthetic.dcm").exists()
    assert (demo_dir / "reports" / "inventory.json").exists()
    assert (demo_dir / "reports" / "inventory.csv").exists()
    assert (demo_dir / "reports" / "inventory.html").exists()
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
