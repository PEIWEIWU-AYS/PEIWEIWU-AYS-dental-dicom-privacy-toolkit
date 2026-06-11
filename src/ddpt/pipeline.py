from __future__ import annotations

from pathlib import Path

from ddpt.anonymize import anonymize_dicom
from ddpt.inspection import inspect_dicom
from ddpt.models import DemoPipelineResult
from ddpt.pixels import parse_rectangle, redact_pixels
from ddpt.reports import (
    model_to_dict,
    write_audit_html,
    write_demo_summary_html,
    write_inspection_html,
)
from ddpt.sharing import create_package, verify_package
from ddpt.synthetic import create_synthetic_dicom
from ddpt.utils import write_json
from ddpt.validation import validate_anonymized_dicom


def run_demo_pipeline(
    output_dir: Path,
    profile: str = "dental-basic",
    rectangle: str = "1,0,1,1",
) -> DemoPipelineResult:
    input_dir = output_dir / "input"
    reports_dir = output_dir / "reports"
    outputs_dir = output_dir / "outputs"
    share_dir = output_dir / "share"

    input_dicom = input_dir / "sample.synthetic.dcm"
    anonymized_dicom = outputs_dir / "sample.anonymized.dcm"
    redacted_dicom = outputs_dir / "sample.redacted.dcm"
    inspection_json = reports_dir / "inspect.json"
    inspection_html = reports_dir / "inspect.html"
    audit_json = reports_dir / "audit.json"
    audit_html = reports_dir / "audit.html"
    validation_json = reports_dir / "validation.json"
    redaction_json = reports_dir / "redaction.json"
    summary_json = reports_dir / "demo-summary.json"
    summary_html = reports_dir / "demo-summary.html"
    manifest_json = share_dir / "manifest.json"
    package_path = share_dir / "package.ddpt"
    key_path = share_dir / "package.key"

    create_synthetic_dicom(input_dicom)

    inspection = inspect_dicom(input_dicom)
    write_json(inspection_json, model_to_dict(inspection))
    write_inspection_html(inspection_html, inspection)

    audit = anonymize_dicom(input_dicom, anonymized_dicom, profile)
    write_json(audit_json, model_to_dict(audit))
    write_audit_html(audit_html, audit)

    validation = validate_anonymized_dicom(anonymized_dicom)
    write_json(validation_json, model_to_dict(validation))

    redaction = redact_pixels(anonymized_dicom, redacted_dicom, [parse_rectangle(rectangle)])
    write_json(redaction_json, model_to_dict(redaction))

    manifest = create_package(
        outputs_dir,
        package_path,
        manifest_path=manifest_json,
        encrypt=True,
        key_output=key_path,
    )
    verify_package(package_path, key_path)

    result = DemoPipelineResult(
        output_dir=str(output_dir),
        input_dicom=str(input_dicom),
        anonymized_dicom=str(anonymized_dicom),
        redacted_dicom=str(redacted_dicom),
        inspection_json=str(inspection_json),
        inspection_html=str(inspection_html),
        audit_json=str(audit_json),
        audit_html=str(audit_html),
        validation_json=str(validation_json),
        redaction_json=str(redaction_json),
        manifest_json=str(manifest_json),
        package_path=str(package_path),
        key_path=str(key_path),
        summary_html=str(summary_html),
        validation_passed=validation.passed,
        package_entries=len(manifest.entries),
    )
    write_json(summary_json, model_to_dict(result))
    write_demo_summary_html(summary_html, result)
    return result
