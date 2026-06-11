from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ddpt import __version__
from ddpt.anonymize import anonymize_dicom, plan_anonymization_actions
from ddpt.api import create_api_app
from ddpt.audit_chain import create_audit_chain, verify_audit_chain
from ddpt.batch import run_batch_workflow
from ddpt.capability import build_capability_matrix
from ddpt.certificate import build_deidentification_certificate
from ddpt.completion import run_objective_audit
from ddpt.dashboard import build_review_dashboard_report
from ddpt.deid_compare import compare_deidentification
from ddpt.doctor import run_doctor
from ddpt.evidence import run_evidence_bundle
from ddpt.inspection import inspect_dicom
from ddpt.inventory import build_inventory, write_inventory_csv
from ddpt.pipeline import run_demo_pipeline
from ddpt.pixel_review import create_pixel_review
from ddpt.pixels import parse_rectangle, redact_pixels
from ddpt.policy import (
    compare_profiles,
    policy_registry_report,
    profile_coverage,
    write_policy_registry_csv,
)
from ddpt.preview import render_dicom_preview
from ddpt.profiles import (
    built_in_profiles,
    describe_profile,
    lint_profile,
    write_profile_template,
)
from ddpt.quality_gate import run_workflow_quality_gate
from ddpt.redaction_plan import (
    load_redaction_plan,
    rectangles_from_plan,
    write_redaction_plan_template,
)
from ddpt.release import run_release_audit
from ddpt.reports import (
    model_to_dict,
    write_audit_html,
    write_capability_matrix_html,
    write_deid_certificate_html,
    write_deid_comparison_html,
    write_inspection_html,
    write_inventory_html,
    write_objective_audit_html,
    write_package_receipt_html,
    write_pixel_review_html,
    write_policy_registry_html,
    write_profile_comparison_html,
    write_profile_lint_html,
    write_release_audit_html,
    write_review_dashboard_html,
    write_share_readiness_html,
    write_workflow_html,
    write_workflow_quality_gate_html,
)
from ddpt.safety import scan_repository_safety
from ddpt.share_readiness import run_share_readiness
from ddpt.sharing import create_package, create_verification_receipt, decrypt_package
from ddpt.synthetic import create_synthetic_dicom, create_synthetic_study
from ddpt.tag_ops import blank_tag_value, delete_tag, dump_tags, set_tag_value
from ddpt.utils import write_json
from ddpt.validation import validate_anonymized_dicom
from ddpt.workflow import run_workflow

app = typer.Typer(help="Dental DICOM Privacy Toolkit", invoke_without_command=True)
profile_app = typer.Typer(help="Inspect anonymization profiles.")
policy_app = typer.Typer(help="Inspect the DICOM privacy policy registry.")
audit_app = typer.Typer(help="Create and verify audit chains.")
safety_app = typer.Typer(help="Run public repository safety checks.")
redaction_plan_app = typer.Typer(help="Create and inspect pixel redaction plans.")
tag_app = typer.Typer(help="Inspect and edit individual DICOM tags.")
api_app = typer.Typer(help="Run local REST API demo.")
workflow_app = typer.Typer(help="Run YAML privacy workflow recipes.")
release_app = typer.Typer(help="Audit local release readiness.")
evidence_app = typer.Typer(help="Build local demonstration evidence bundles.")
capability_app = typer.Typer(help="Audit competitor-informed project capabilities.")
certificate_app = typer.Typer(help="Create de-identification certificates.")
completion_app = typer.Typer(help="Audit original project objective completion.")
dashboard_app = typer.Typer(help="Build static local review dashboards.")
compare_app = typer.Typer(help="Compare DICOM privacy outputs.")
share_app = typer.Typer(help="Check sharing readiness gates.")
quality_app = typer.Typer(help="Run workflow quality gates.")
app.add_typer(profile_app, name="profile")
app.add_typer(policy_app, name="policy")
app.add_typer(audit_app, name="audit")
app.add_typer(safety_app, name="safety")
app.add_typer(redaction_plan_app, name="redaction-plan")
app.add_typer(tag_app, name="tag")
app.add_typer(api_app, name="api")
app.add_typer(workflow_app, name="workflow")
app.add_typer(release_app, name="release")
app.add_typer(evidence_app, name="evidence")
app.add_typer(capability_app, name="capability")
app.add_typer(certificate_app, name="certificate")
app.add_typer(completion_app, name="completion")
app.add_typer(dashboard_app, name="dashboard")
app.add_typer(compare_app, name="compare")
app.add_typer(share_app, name="share")
app.add_typer(quality_app, name="quality")
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


@app.command("synthetic-study")
def synthetic_study(
    output_dir: Annotated[Path, typer.Argument(help="Output synthetic study directory.")],
    patients: Annotated[int, typer.Option(help="Number of synthetic patients.")] = 2,
    files_per_patient: Annotated[
        int,
        typer.Option(help="Number of synthetic DICOM files per patient."),
    ] = 2,
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write synthetic study manifest JSON.")
    ] = None,
) -> None:
    try:
        report = create_synthetic_study(
            output_dir,
            patient_count=patients,
            files_per_patient=files_per_patient,
        )
    except ValueError as exc:
        console.print(str(exc))
        raise typer.Exit(1) from exc
    if json_output:
        write_json(json_output, model_to_dict(report))

    table = Table(title="Synthetic Dental Study")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Output directory", report.output_dir)
    table.add_row("Patients", str(report.patient_count))
    table.add_row("Files per patient", str(report.files_per_patient))
    table.add_row("Total files", str(report.total_files))
    table.add_row(
        "Modalities",
        ", ".join(f"{key}:{value}" for key, value in report.modalities.items()),
    )
    console.print(table)


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
def batch(
    input_dir: Annotated[Path, typer.Argument(help="Directory containing DICOM files.")],
    output_dir: Annotated[Path, typer.Option("--out", help="Output batch directory.")],
    profile: Annotated[str, typer.Option(help="Profile name or YAML path.")] = "dental-basic",
    recursive: Annotated[
        bool, typer.Option("--recursive/--no-recursive", help="Recurse through input directory.")
    ] = True,
) -> None:
    summary = run_batch_workflow(input_dir, output_dir, profile=profile, recursive=recursive)
    console.print(f"Batch processed: {summary.processed_files}/{summary.total_files}")
    console.print(f"Failed files: {summary.failed_files}")
    console.print(f"Validation failures: {summary.validation_failures}")
    console.print(f"De-identification comparison failures: {summary.comparison_failures}")
    console.print(f"Summary HTML: {output_dir / 'batch-summary.html'}")
    if summary.failed_files or summary.validation_failures or summary.comparison_failures:
        raise typer.Exit(1)


@app.command()
def inventory(
    input_dir: Annotated[Path, typer.Argument(help="Directory containing DICOM files.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write inventory JSON.")
    ] = None,
    csv_output: Annotated[
        Path | None, typer.Option("--csv", help="Write inventory CSV.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write inventory HTML.")
    ] = None,
    recursive: Annotated[
        bool, typer.Option("--recursive/--no-recursive", help="Recurse through input directory.")
    ] = True,
    include_hash: Annotated[
        bool, typer.Option("--hash/--no-hash", help="Include SHA-256 file hashes.")
    ] = True,
) -> None:
    report = build_inventory(input_dir, recursive=recursive, include_hash=include_hash)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if csv_output:
        write_inventory_csv(csv_output, report)
    if html_output:
        write_inventory_html(html_output, report)

    table = Table(title="DICOM Directory Inventory")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Total files", str(report.total_files))
    table.add_row("Readable files", str(report.readable_files))
    table.add_row("Unreadable files", str(report.unreadable_files))
    table.add_row("High-risk tags", str(report.high_risk_tags))
    table.add_row("Medium-risk tags", str(report.medium_risk_tags))
    modalities = ", ".join(f"{key}:{value}" for key, value in report.modalities.items())
    table.add_row("Modalities", modalities)
    console.print(table)


@app.command()
def doctor(
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write environment report JSON.")
    ] = None,
) -> None:
    report = run_doctor()
    if json_output:
        write_json(json_output, model_to_dict(report))

    table = Table(title="Dental DICOM Privacy Toolkit Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Message")
    for check in report.checks:
        table.add_row(check.name, "PASS" if check.passed else "FAIL", check.message)
    console.print(table)
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@api_app.command("serve")
def api_serve(
    root_dir: Annotated[Path, typer.Argument(help="Local API workspace root.")],
    host: Annotated[str, typer.Option(help="Bind host.")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Bind port.")] = 8765,
) -> None:
    import uvicorn

    application = create_api_app(root_dir)
    console.print(f"Serving local DDPT API at http://{host}:{port}")
    console.print(f"Workbench: http://{host}:{port}/workbench")
    console.print("Synthetic or explicitly approved test DICOM files only.")
    uvicorn.run(application, host=host, port=port)


@workflow_app.command("run")
def workflow_run(
    recipe_path: Annotated[Path, typer.Argument(help="YAML workflow recipe path.")],
    root_dir: Annotated[Path, typer.Option("--root", help="Workflow output root.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write workflow report JSON.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write workflow report HTML.")
    ] = None,
) -> None:
    report = run_workflow(recipe_path, root_dir)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_workflow_html(html_output, report)

    table = Table(title=f"Workflow: {report.name}")
    table.add_column("Step")
    table.add_column("Action")
    table.add_column("Status")
    table.add_column("Message")
    for step in report.steps:
        table.add_row(step.id, step.action, "PASS" if step.passed else "FAIL", step.message)
    console.print(table)
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@safety_app.command("scan")
def safety_scan(
    root_dir: Annotated[Path, typer.Argument(help="Repository root to scan.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write safety scan JSON.")
    ] = None,
) -> None:
    report = scan_repository_safety(root_dir)
    if json_output:
        write_json(json_output, model_to_dict(report))

    table = Table(title="Public Repository Safety Scan")
    table.add_column("Severity")
    table.add_column("Rule")
    table.add_column("Path")
    table.add_column("Message")
    for finding in report.findings:
        table.add_row(finding.severity, finding.rule_id, finding.path, finding.message)
    console.print(table)
    console.print(f"Scanned files: {report.scanned_files}")
    console.print(f"Findings: {len(report.findings)}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@release_app.command("audit")
def release_audit(
    root_dir: Annotated[Path, typer.Argument(help="Repository root to audit.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write release audit JSON.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write release audit HTML.")
    ] = None,
) -> None:
    report = run_release_audit(root_dir)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_release_audit_html(html_output, report)

    table = Table(title="Public Release Readiness Audit")
    table.add_column("Status")
    table.add_column("Check")
    table.add_column("Category")
    table.add_column("Message")
    for check in report.checks:
        table.add_row(
            "PASS" if check.passed else "FAIL",
            check.id,
            check.category,
            check.message,
        )
    console.print(table)
    console.print(f"Passed checks: {report.passed_checks}/{len(report.checks)}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@evidence_app.command("bundle")
def evidence_bundle(
    repository_root: Annotated[Path, typer.Argument(help="Repository root to validate.")],
    output_dir: Annotated[
        Path, typer.Option("--out", help="Output evidence bundle directory.")
    ],
) -> None:
    result = run_evidence_bundle(repository_root, output_dir)
    table = Table(title="Dental DICOM Evidence Bundle")
    table.add_column("Category")
    table.add_column("Artifact")
    table.add_column("Path")
    for artifact in result.artifacts:
        table.add_row(artifact.category, artifact.label, artifact.path)
    console.print(table)
    console.print(f"Evidence bundle: {result.output_dir}")
    console.print(f"Summary HTML: {Path(result.output_dir) / 'reports' / 'evidence-bundle.html'}")
    console.print(f"Overall: {'PASS' if result.passed else 'FAIL'}")
    if not result.passed:
        raise typer.Exit(1)


@capability_app.command("matrix")
def capability_matrix(
    root: Annotated[
        Path, typer.Option("--root", help="Repository root to audit.")
    ] = Path("."),
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON capability matrix.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write HTML capability matrix.")
    ] = None,
) -> None:
    report = build_capability_matrix(root)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_capability_matrix_html(html_output, report)

    table = Table(title="Competitor-Informed Capability Matrix")
    table.add_column("Status")
    table.add_column("Capability")
    table.add_column("Learned From")
    table.add_column("Differentiator")
    for item in report.items:
        table.add_row(
            item.status,
            item.capability,
            ", ".join(item.source_tools),
            item.differentiator,
        )
    console.print(table)
    console.print(f"Implemented: {report.implemented_items}/{report.total_items}")
    console.print(f"Partial: {report.partial_items}")
    console.print(f"Missing: {report.missing_items}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@certificate_app.command("create")
def certificate_create(
    root_dir: Annotated[
        Path, typer.Argument(help="Demo or workflow output directory with reports.")
    ],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write certificate JSON.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write certificate HTML.")
    ] = None,
) -> None:
    certificate = build_deidentification_certificate(root_dir)
    if json_output:
        write_json(json_output, model_to_dict(certificate))
    if html_output:
        write_deid_certificate_html(html_output, certificate)

    table = Table(title="Dental DICOM De-identification Certificate")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Summary")
    for check in certificate.checks:
        table.add_row(
            check.id,
            "PASS" if check.passed else "FAIL",
            check.summary,
        )
    console.print(table)
    console.print(f"Profile: {certificate.profile}")
    console.print(f"Checks: {certificate.passed_checks}/{certificate.total_checks}")
    console.print(f"Overall: {'PASS' if certificate.passed else 'FAIL'}")
    if not certificate.passed:
        raise typer.Exit(1)


@completion_app.command("audit")
def completion_audit(
    root: Annotated[
        Path, typer.Argument(help="Repository root to audit against the original objective.")
    ] = Path("."),
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON objective audit.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write HTML objective audit.")
    ] = None,
) -> None:
    report = run_objective_audit(root)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_objective_audit_html(html_output, report)

    table = Table(title="Original Objective Completion Audit")
    table.add_column("Status")
    table.add_column("Category")
    table.add_column("Requirement")
    table.add_column("Missing")
    for item in report.items:
        table.add_row(
            "PASS" if item.passed else "FAIL",
            item.category,
            item.requirement,
            ", ".join(item.missing_evidence),
        )
    console.print(table)
    console.print(f"Passed: {report.passed_items}/{report.total_items}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@dashboard_app.command("build")
def dashboard_build(
    evidence_dir: Annotated[
        Path,
        typer.Argument(help="Evidence bundle directory generated by `ddpt evidence bundle`."),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option("--out", help="Output dashboard HTML path."),
    ] = None,
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON dashboard report.")
    ] = None,
) -> None:
    output_path = output_path or evidence_dir / "reports" / "review-dashboard.html"
    try:
        report = build_review_dashboard_report(evidence_dir, output_path)
    except FileNotFoundError as exc:
        console.print(str(exc))
        raise typer.Exit(1) from exc
    if json_output:
        write_json(json_output, model_to_dict(report))
    write_review_dashboard_html(output_path, report)

    console.print(f"Review dashboard: {output_path}")
    console.print(f"Artifacts available: {report.available_artifacts}/{report.total_artifacts}")
    console.print(f"Missing artifacts: {report.missing_artifacts}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@compare_app.command("deid")
def compare_deid(
    source_path: Annotated[Path, typer.Argument(help="Original source DICOM path.")],
    anonymized_path: Annotated[
        Path, typer.Argument(help="Anonymized DICOM path to compare.")
    ],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON comparison report.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write HTML comparison report.")
    ] = None,
) -> None:
    report = compare_deidentification(source_path, anonymized_path)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_deid_comparison_html(html_output, report)

    table = Table(title="DICOM De-identification Comparison")
    table.add_column("Pass")
    table.add_column("Risk")
    table.add_column("Keyword")
    table.add_column("Status")
    table.add_column("Note")
    for item in report.items:
        table.add_row(
            "yes" if item.passed else "no",
            item.risk,
            item.keyword,
            item.status,
            item.note,
        )
    console.print(table)
    console.print(f"Passed items: {report.passed_items}/{report.total_items}")
    console.print(f"Private tags after: {report.private_tags_after}")
    console.print(f"Pixel data changed: {report.pixel_data_changed}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@share_app.command("readiness")
def share_readiness(
    root_dir: Annotated[Path, typer.Argument(help="Demo or workflow output directory.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON readiness report.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write HTML readiness report.")
    ] = None,
) -> None:
    report = run_share_readiness(root_dir)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_share_readiness_html(html_output, report)

    table = Table(title="Dental DICOM Share Readiness")
    table.add_column("Status")
    table.add_column("Check")
    table.add_column("Category")
    table.add_column("Message")
    for check in report.checks:
        table.add_row(
            "PASS" if check.passed else "FAIL",
            check.id,
            check.category,
            check.message,
        )
    console.print(table)
    console.print(f"Passed checks: {report.passed_checks}/{len(report.checks)}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@quality_app.command("gate")
def quality_gate(
    root_dir: Annotated[Path, typer.Argument(help="Demo or workflow output directory.")],
    workflow_report: Annotated[
        Path | None,
        typer.Option("--workflow-report", help="Optional workflow run JSON report."),
    ] = None,
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON quality gate report.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write HTML quality gate report.")
    ] = None,
) -> None:
    report = run_workflow_quality_gate(root_dir, workflow_report_path=workflow_report)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_workflow_quality_gate_html(html_output, report)

    table = Table(title="Dental DICOM Workflow Quality Gate")
    table.add_column("Status")
    table.add_column("Required")
    table.add_column("Check")
    table.add_column("Stage")
    table.add_column("Message")
    for check in report.checks:
        table.add_row(
            "PASS" if check.passed else "FAIL",
            "yes" if check.required else "optional",
            check.id,
            check.stage,
            check.message,
        )
    console.print(table)
    console.print(f"Required checks: {report.passed_checks}/{report.required_checks}")
    console.print(f"Failed required checks: {report.failed_checks}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@redaction_plan_app.command("init")
def redaction_plan_init(
    output_path: Annotated[Path, typer.Argument(help="Output YAML redaction plan path.")],
    overwrite: Annotated[
        bool, typer.Option("--overwrite", help="Overwrite existing file.")
    ] = False,
) -> None:
    try:
        path = write_redaction_plan_template(output_path, overwrite=overwrite)
    except FileExistsError as exc:
        console.print(str(exc))
        raise typer.Exit(1) from exc
    console.print(f"Redaction plan template written to: {path}")


@redaction_plan_app.command("show")
def redaction_plan_show(
    plan_path: Annotated[Path, typer.Argument(help="YAML redaction plan path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write redaction plan JSON.")
    ] = None,
) -> None:
    plan = load_redaction_plan(plan_path)
    if json_output:
        write_json(json_output, model_to_dict(plan))

    table = Table(title=f"Pixel Redaction Plan: {plan.name}")
    table.add_column("Label")
    table.add_column("Unit")
    table.add_column("X")
    table.add_column("Y")
    table.add_column("Width")
    table.add_column("Height")
    for region in plan.regions:
        table.add_row(
            region.label,
            region.unit,
            str(region.x),
            str(region.y),
            str(region.width),
            str(region.height),
        )
    console.print(table)


@tag_app.command("dump")
def tag_dump(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write tag dump JSON.")
    ] = None,
    include_pixel_data: Annotated[
        bool, typer.Option("--include-pixel-data", help="Include PixelData in dump.")
    ] = False,
) -> None:
    report = dump_tags(input_path, include_pixel_data=include_pixel_data)
    if json_output:
        write_json(json_output, model_to_dict(report))

    table = Table(title="DICOM Tag Dump")
    table.add_column("Tag")
    table.add_column("Keyword")
    table.add_column("VR")
    table.add_column("Value")
    for item in report.tags:
        table.add_row(item.tag, item.keyword, item.vr, item.value)
    console.print(table)
    console.print(f"Tags: {len(report.tags)}")


@tag_app.command("set")
def tag_set(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    tag_identifier: Annotated[str, typer.Argument(help="DICOM keyword or tag.")],
    value: Annotated[str, typer.Argument(help="New tag value.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output DICOM path.")],
    vr: Annotated[
        str | None, typer.Option("--vr", help="VR for adding unknown tags.")
    ] = None,
    audit_json: Annotated[Path | None, typer.Option("--audit", help="Write audit JSON.")] = None,
) -> None:
    audit = set_tag_value(input_path, output_path, tag_identifier, value, vr=vr)
    _write_tag_audit(audit, audit_json)


@tag_app.command("blank")
def tag_blank(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    tag_identifier: Annotated[str, typer.Argument(help="DICOM keyword or tag.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output DICOM path.")],
    audit_json: Annotated[Path | None, typer.Option("--audit", help="Write audit JSON.")] = None,
) -> None:
    audit = blank_tag_value(input_path, output_path, tag_identifier)
    _write_tag_audit(audit, audit_json)


@tag_app.command("delete")
def tag_delete(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    tag_identifier: Annotated[str, typer.Argument(help="DICOM keyword or tag.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output DICOM path.")],
    audit_json: Annotated[Path | None, typer.Option("--audit", help="Write audit JSON.")] = None,
) -> None:
    audit = delete_tag(input_path, output_path, tag_identifier)
    _write_tag_audit(audit, audit_json)


@profile_app.command("list")
def profile_list() -> None:
    for profile in built_in_profiles():
        console.print(profile)


@profile_app.command("show")
def profile_show(
    profile: Annotated[str, typer.Argument(help="Profile name or YAML path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON profile summary.")
    ] = None,
) -> None:
    summary = describe_profile(profile)
    if json_output:
        write_json(json_output, summary)

    table = Table(title=f"Profile: {summary['name']}")
    table.add_column("Action")
    table.add_column("Keywords")
    table.add_row("pseudonymize", ", ".join(summary["pseudonymize_keywords"]) or "-")
    table.add_row("replace", ", ".join(summary["replace_keywords"]) or "-")
    table.add_row("blank", ", ".join(summary["blank_keywords"]) or "-")
    table.add_row(
        f"date_shift ({summary['date_shift_offset_days']} days)",
        ", ".join(summary["date_shift_keywords"]) or "-",
    )
    table.add_row("regenerate_uid", ", ".join(summary["regenerate_uid_keywords"]) or "-")
    table.add_row("remove_private_tags", str(summary["remove_private_tags"]))
    console.print(table)


@profile_app.command("init")
def profile_init(
    output_path: Annotated[Path, typer.Argument(help="Output YAML profile path.")],
    overwrite: Annotated[
        bool, typer.Option("--overwrite", help="Overwrite existing file.")
    ] = False,
) -> None:
    try:
        path = write_profile_template(output_path, overwrite=overwrite)
    except FileExistsError as exc:
        console.print(str(exc))
        raise typer.Exit(1) from exc
    console.print(f"Profile template written to: {path}")


@profile_app.command("coverage")
def profile_coverage_command(
    profile: Annotated[str, typer.Argument(help="Profile name or YAML path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON coverage report.")
    ] = None,
) -> None:
    report = profile_coverage(profile)
    if json_output:
        write_json(json_output, model_to_dict(report))

    table = Table(title=f"Profile Coverage: {report.profile}")
    table.add_column("Risk")
    table.add_column("Keyword")
    table.add_column("Recommended")
    table.add_column("Profile")
    table.add_column("Covered")
    for item in report.items:
        table.add_row(
            item.risk,
            item.keyword,
            item.recommended_action,
            item.profile_action,
            "yes" if item.covered else "no",
        )
    console.print(table)
    console.print(f"Covered: {report.covered_items}/{report.total_items}")
    console.print(f"High-risk uncovered: {len(report.high_risk_uncovered)}")
    console.print(f"Medium-risk uncovered: {len(report.medium_risk_uncovered)}")


@profile_app.command("lint")
def profile_lint_command(
    profile: Annotated[str, typer.Argument(help="Profile name or YAML path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON lint report.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write HTML lint report.")
    ] = None,
) -> None:
    report = lint_profile(profile)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_profile_lint_html(html_output, report)

    table = Table(title=f"Profile Lint: {report.profile}")
    table.add_column("Severity")
    table.add_column("Rule")
    table.add_column("Keyword")
    table.add_column("Message")
    for finding in report.findings:
        table.add_row(
            finding.severity,
            finding.rule_id,
            finding.keyword or "",
            finding.message,
        )
    console.print(table)
    console.print(f"Errors: {report.error_count}")
    console.print(f"Warnings: {report.warning_count}")
    console.print(f"Coverage: {report.covered_items}/{report.total_policy_items}")
    console.print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise typer.Exit(1)


@profile_app.command("compare")
def profile_compare_command(
    baseline_profile: Annotated[str, typer.Argument(help="Baseline profile name or YAML path.")],
    candidate_profile: Annotated[str, typer.Argument(help="Candidate profile name or YAML path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write JSON comparison report.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write HTML comparison report.")
    ] = None,
) -> None:
    report = compare_profiles(baseline_profile, candidate_profile)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_profile_comparison_html(html_output, report)

    table = Table(
        title=f"Profile Compare: {report.baseline_profile} -> {report.candidate_profile}"
    )
    table.add_column("Changed")
    table.add_column("Risk")
    table.add_column("Keyword")
    table.add_column("Baseline")
    table.add_column("Candidate")
    table.add_column("Note")
    for item in report.items:
        if item.changed:
            table.add_row(
                "yes",
                item.risk,
                item.keyword,
                item.baseline_action,
                item.candidate_action,
                item.note,
            )
    console.print(table)
    console.print(f"Changed: {report.changed_items}/{report.total_items}")
    console.print(
        f"Coverage: {report.baseline_profile} "
        f"{report.baseline_covered_items}/{report.total_items}; "
        f"{report.candidate_profile} {report.candidate_covered_items}/{report.total_items}"
    )


@policy_app.command("export")
def policy_export_command(
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write policy registry JSON.")
    ] = None,
    csv_output: Annotated[
        Path | None, typer.Option("--csv", help="Write policy registry CSV.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write policy registry HTML.")
    ] = None,
    risk: Annotated[
        list[str] | None,
        typer.Option("--risk", help="Filter by risk: high, medium, or low. Can repeat."),
    ] = None,
) -> None:
    risks = _validate_policy_risks(risk or [])
    report = policy_registry_report(risks)
    if json_output:
        write_json(json_output, model_to_dict(report))
    if csv_output:
        write_policy_registry_csv(csv_output, report)
    if html_output:
        write_policy_registry_html(html_output, report)

    table = Table(title="Dental DICOM Policy Registry")
    table.add_column("Risk")
    table.add_column("Keyword")
    table.add_column("Recommended")
    table.add_column("DICOM Code")
    table.add_column("Reason")
    for item in report.items:
        table.add_row(
            item.risk,
            item.keyword,
            item.recommended_action,
            item.dicom_action_code,
            item.reason,
        )
    console.print(table)
    console.print(f"Total: {report.total_items}")
    console.print(
        f"High: {report.high_risk_items}; "
        f"Medium: {report.medium_risk_items}; Low: {report.low_risk_items}"
    )


@audit_app.command("chain")
def audit_chain_command(
    root_dir: Annotated[Path, typer.Argument(help="Directory of artifacts to hash.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output audit chain JSON.")],
    include_keys: Annotated[
        bool, typer.Option("--include-keys", help="Include .key files in the chain.")
    ] = False,
) -> None:
    manifest = create_audit_chain(root_dir, output_path, include_key_files=include_keys)
    console.print(f"Audit chain written to: {output_path}")
    console.print(f"Files chained: {len(manifest.entries)}")
    console.print(f"Root hash: {manifest.root_hash}")


@audit_app.command("verify")
def audit_verify_command(
    manifest_path: Annotated[Path, typer.Argument(help="Audit chain JSON path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write verification JSON.")
    ] = None,
) -> None:
    result = verify_audit_chain(manifest_path)
    if json_output:
        write_json(json_output, model_to_dict(result))
    console.print(f"Audit chain passed: {result.passed}")
    console.print(f"Checked files: {result.checked_files}")
    for error in result.errors:
        console.print(f"ERROR {error}")
    if not result.passed:
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
    output_path: Annotated[
        Path | None, typer.Option("--out", help="Output anonymized DICOM path.")
    ] = None,
    profile: Annotated[str, typer.Option(help="Profile name or YAML path.")] = "dental-basic",
    audit_json: Annotated[Path | None, typer.Option("--audit", help="Write audit JSON.")] = None,
    audit_html: Annotated[Path | None, typer.Option("--html", help="Write audit HTML.")] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview changes without writing DICOM.")
    ] = False,
) -> None:
    if dry_run:
        audit = plan_anonymization_actions(input_path, profile, output_path)
    else:
        if output_path is None:
            console.print("--out is required unless --dry-run is used.")
            raise typer.Exit(1)
        audit = anonymize_dicom(input_path, output_path, profile)
    if audit_json:
        write_json(audit_json, model_to_dict(audit))
    if audit_html:
        write_audit_html(audit_html, audit)
    if dry_run:
        console.print("Dry run only. No DICOM file was written.")
    else:
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
        list[str] | None,
        typer.Option(
            "--rect",
            help="Rectangle to redact in x,y,width,height format. Can be repeated.",
        ),
    ] = None,
    plan: Annotated[
        Path | None,
        typer.Option("--plan", help="YAML redaction plan with pixel or percent regions."),
    ] = None,
    fill_value: Annotated[int, typer.Option(help="Pixel fill value.")] = 0,
    audit_json: Annotated[Path | None, typer.Option("--audit", help="Write audit JSON.")] = None,
) -> None:
    rectangles = [parse_rectangle(value) for value in rect or []]
    if plan:
        rectangles.extend(rectangles_from_plan(input_path, plan))
    audit = redact_pixels(input_path, output_path, rectangles, fill_value)
    if audit_json:
        write_json(audit_json, model_to_dict(audit))
    console.print(f"Pixel-redacted DICOM written to: {output_path}")
    console.print(f"Rectangles redacted: {len(rectangles)}")


@app.command("pixel-review")
def pixel_review_command(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    output_dir: Annotated[Path, typer.Option("--out-dir", help="Output review directory.")],
    rect: Annotated[
        list[str] | None,
        typer.Option(
            "--rect",
            help="Manual rectangle in x,y,width,height format. Can be repeated.",
        ),
    ] = None,
    plan: Annotated[
        Path | None,
        typer.Option("--plan", help="YAML redaction plan with pixel or percent regions."),
    ] = None,
    fill_value: Annotated[int, typer.Option(help="Preview redaction fill value.")] = 0,
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write pixel review JSON.")
    ] = None,
    html_output: Annotated[
        Path | None, typer.Option("--html", help="Write pixel review HTML.")
    ] = None,
    max_size: Annotated[int, typer.Option(help="Maximum rendered side length.")] = 512,
) -> None:
    rectangles = [parse_rectangle(value) for value in rect or []]
    report = create_pixel_review(
        input_path,
        output_dir,
        rectangles=rectangles,
        plan_path=plan,
        fill_value=fill_value,
        max_size=max_size,
    )
    if json_output:
        write_json(json_output, model_to_dict(report))
    if html_output:
        write_pixel_review_html(html_output, report)
    console.print(f"Pixel review directory: {output_dir}")
    console.print(f"Regions reviewed: {len(report.regions)}")
    console.print(f"Overlay preview: {report.overlay_preview_png}")


@app.command()
def preview(
    input_path: Annotated[Path, typer.Argument(help="Input DICOM path.")],
    output_path: Annotated[Path, typer.Option("--out", help="Output PNG preview path.")],
    json_output: Annotated[
        Path | None, typer.Option("--json", help="Write preview metadata JSON.")
    ] = None,
    max_size: Annotated[int, typer.Option(help="Maximum rendered side length.")] = 512,
) -> None:
    report = render_dicom_preview(input_path, output_path, max_size=max_size)
    if json_output:
        write_json(json_output, model_to_dict(report))
    console.print(f"Preview written to: {output_path}")
    console.print(f"Rendered size: {report.rendered_width} x {report.rendered_height}")


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
    receipt_json: Annotated[
        Path | None, typer.Option("--receipt", help="Write verification receipt JSON.")
    ] = None,
    receipt_html: Annotated[
        Path | None, typer.Option("--html", help="Write verification receipt HTML.")
    ] = None,
) -> None:
    receipt = create_verification_receipt(package_path, key)
    if receipt_json:
        write_json(receipt_json, model_to_dict(receipt))
    if receipt_html:
        write_package_receipt_html(receipt_html, receipt)
    if not receipt.passed:
        for error in receipt.errors:
            console.print(f"ERROR {error}")
        raise typer.Exit(1)
    console.print(f"Verification passed for {len(receipt.entries)} file(s).")
    console.print(f"Package SHA-256: {receipt.package_sha256}")


@app.command()
def decrypt(
    package_path: Annotated[Path, typer.Argument(help="Encrypted package path.")],
    output_dir: Annotated[Path, typer.Option("--out", help="Output directory.")],
    key: Annotated[Path, typer.Option("--key", help="Encryption key path.")],
) -> None:
    manifest = decrypt_package(package_path, output_dir, key)
    console.print(f"Decrypted package to: {output_dir}")
    console.print(f"Files in manifest: {len(manifest.entries)}")


def _write_tag_audit(audit, audit_json: Path | None) -> None:
    if audit_json:
        write_json(audit_json, model_to_dict(audit))
    console.print(f"Tag-edited DICOM written to: {audit.output_path}")
    console.print(f"Actions: {len(audit.actions)}")
    for action in audit.actions:
        console.print(
            f"{action.action} {action.tag} {action.keyword}: "
            f"{action.before!r} -> {action.after!r}"
        )


def _validate_policy_risks(values: list[str]) -> list[str]:
    allowed = {"high", "medium", "low", "unknown"}
    risks = []
    for value in values:
        normalized = value.lower()
        if normalized not in allowed:
            console.print(f"Unsupported risk filter: {value}")
            raise typer.Exit(1)
        risks.append(normalized)
    return risks


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
