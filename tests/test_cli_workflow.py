from __future__ import annotations

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
    assert len(verified_manifest.entries) == 1

    result = runner.invoke(
        app,
        ["decrypt", str(package), "--out", str(decrypted), "--key", str(key)],
    )
    assert result.exit_code == 0, result.output
    assert (decrypted / "sample.anonymized.dcm").exists()


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
