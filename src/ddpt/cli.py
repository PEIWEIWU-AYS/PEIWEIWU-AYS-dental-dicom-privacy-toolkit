from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ddpt import __version__
from ddpt.anonymize import anonymize_dicom
from ddpt.inspection import inspect_dicom
from ddpt.reports import model_to_dict, write_audit_html, write_inspection_html
from ddpt.sharing import create_package, decrypt_package, verify_package
from ddpt.synthetic import create_synthetic_dicom
from ddpt.utils import write_json

app = typer.Typer(help="Dental DICOM Privacy Toolkit", invoke_without_command=True)
console = Console()


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", help="Show version and exit.")
    ] = False,
) -> None:
    if version:
        console.print(f"ddpt {__version__}")
        raise typer.Exit()


@app.command()
def synthetic(
    output: Annotated[Path, typer.Argument(help="Output synthetic DICOM path.")],
    patient_name: Annotated[
        str, typer.Option(help="Synthetic patient name.")
    ] = "SYNTHETIC^DENTAL",
    patient_id: Annotated[str, typer.Option(help="Synthetic patient ID.")] = "SYNTHETIC-001",
    modality: Annotated[str, typer.Option(help="Synthetic modality.")] = "DX",
    study_description: Annotated[
        str, typer.Option(help="Synthetic study description.")
    ] = "Synthetic Dental Radiograph",
) -> None:
    path = create_synthetic_dicom(output, patient_name, patient_id, modality, study_description)
    console.print(f"Created synthetic DICOM: {path}")


@app.command()
def inspect(
    dicom_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    json_output: Annotated[Path | None, typer.Option("--json", help="Write JSON report.")] = None,
    html_output: Annotated[Path | None, typer.Option("--html", help="Write HTML report.")] = None,
) -> None:
    report = inspect_dicom(dicom_path)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_inspection_html(html_output, report)
    _print_inspection_table(report)


@app.command()
def anonymize(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output anonymized DICOM path.")],
    profile: Annotated[str, typer.Option(help="Profile name or YAML path.")] = "dental-basic",
    audit_json: Annotated[Path | None, typer.Option("--audit", help="Write audit JSON.")] = None,
    audit_html: Annotated[Path | None, typer.Option("--html", help="Write audit HTML.")] = None,
) -> None:
    audit = anonymize_dicom(input_path, output_path, profile)
    if audit_json:
        write_json(audit_json, model_to_dict(audit))
    if audit_html:
        write_audit_html(audit_html, audit)
    console.print(f"Anonymized DICOM written to: {output_path}")
    console.print(f"Actions: {len(audit.actions)}")


@app.command("package")
def package_command(
    input_dir: Annotated[Path, typer.Argument(help="Directory containing anonymized files.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output package path.")],
    manifest: Annotated[
        Path | None, typer.Option("--manifest", help="Write manifest JSON.")
    ] = None,
    encrypt: Annotated[bool, typer.Option("--encrypt", help="Encrypt the package.")] = False,
    key_out: Annotated[
        Path | None, typer.Option("--key-out", help="Write generated encryption key.")
    ] = None,
) -> None:
    package_manifest = create_package(input_dir, output_path, manifest, encrypt, key_out)
    console.print(f"Package written to: {output_path}")
    console.print(f"Files packaged: {len(package_manifest.entries)}")


@app.command()
def verify(
    package_path: Annotated[Path, typer.Argument(help="Package path.")],
    key: Annotated[Path | None, typer.Option("--key", help="Encryption key path.")] = None,
) -> None:
    manifest = verify_package(package_path, key)
    console.print(f"Verification passed for {len(manifest.entries)} file(s).")


@app.command()
def decrypt(
    package_path: Annotated[Path, typer.Argument(help="Encrypted package path.")],
    output_dir: Annotated[Path, typer.Option("--out", help="Output directory.")],
    key: Annotated[Path, typer.Option("--key", help="Encryption key path.")],
) -> None:
    manifest = decrypt_package(package_path, output_dir, key)
    console.print(f"Decrypted package to: {output_dir}")
    console.print(f"Files in manifest: {len(manifest.entries)}")


def _print_inspection_table(report) -> None:
    table = Table(title="DICOM Privacy Inspection")
    table.add_column("Risk")
    table.add_column("Tag")
    table.add_column("Keyword")
    table.add_column("Value")
    for item in report.findings:
        if item.risk in {"high", "medium"}:
            table.add_row(item.risk, item.tag, item.keyword, item.value)
    console.print(table)
    console.print(f"High-risk tags: {report.high_risk_count}")
    console.print(f"Medium-risk tags: {report.medium_risk_count}")
