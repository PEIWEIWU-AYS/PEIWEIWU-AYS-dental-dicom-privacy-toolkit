from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ddpt import __version__
from ddpt.anonymize import anonymize_dicom
from ddpt.inspection import inspect_dicom
from ddpt.pipeline import run_demo_pipeline
from ddpt.pixels import parse_rectangle, redact_pixels
from ddpt.reports import model_to_dict, write_audit_html, write_inspection_html
from ddpt.sharing import create_package, decrypt_package, verify_package
from ddpt.synthetic import create_synthetic_dicom
from ddpt.utils import write_json
from ddpt.validation import validate_anonymized_dicom

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
def demo(
    output_dir: Annotated[Path, typer.Argument(help="Output demo directory.")],
    profile: Annotated[str, typer.Option(help="Profile name or YAML path.")] = "dental-basic",
    rect: Annotated[
        str,
        typer.Option(
            "--rect",
            help="Demo redaction rectangle in x,y,width,height format.",
        ),
    ] = "1,0,1,1",
) -> None:
    result = run_demo_pipeline(output_dir, profile, rect)
    console.print(f"Demo pipeline written to: {result.output_dir}")
    console.print(f"Summary HTML: {result.summary_html}")
    console.print(f"Package entries: {result.package_entries}")
    if not result.validation_passed:
        raise typer.Exit(1)


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


@app.command()
def validate(
    dicom_path: Annotated[Path, typer.Argument(help="Anonymized DICOM path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write validation JSON.")
    ] = None,
) -> None:
    report = validate_anonymized_dicom(dicom_path)
    if json_output:
        write_json(json_output, model_to_dict(report))

    for check in report.checks:
        mark = "PASS" if check.passed else "FAIL"
        console.print(f"{mark} {check.name}: {check.message}")
    for warning in report.warnings:
        console.print(f"WARNING {warning}")

    if not report.passed:
        raise typer.Exit(1)


@app.command("redact-pixels")
def redact_pixels_command(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output redacted DICOM path.")],
    rect: Annotated[
        list[str],
        typer.Option(
            "--rect",
            help="Rectangle to redact in x,y,width,height format. Can be repeated.",
        ),
    ],
    fill_value: Annotated[int, typer.Option(help="Pixel fill value.")] = 0,
    audit_json: Annotated[Path | None, typer.Option("--audit", help="Write audit JSON.")] = None,
) -> None:
    rectangles = [parse_rectangle(value) for value in rect]
    audit = redact_pixels(input_path, output_path, rectangles, fill_value)
    if audit_json:
        write_json(audit_json, model_to_dict(audit))
    console.print(f"Pixel-redacted DICOM written to: {output_path}")
    console.print(f"Rectangles redacted: {len(rectangles)}")


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
