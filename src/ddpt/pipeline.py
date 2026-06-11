from __future__ import annotations

from pathlib import Path

from ddpt.anonymize import anonymize_dicom
from ddpt.audit_chain import create_audit_chain, verify_audit_chain
from ddpt.deid_compare import compare_deidentification
from ddpt.inspection import inspect_dicom
from ddpt.inventory import build_inventory, write_inventory_csv
from ddpt.models import DemoPipelineResult
from ddpt.pixel_review import create_pixel_review
from ddpt.pixels import parse_rectangle, redact_pixels
from ddpt.preview import render_dicom_preview
from ddpt.reports import (
    model_to_dict,
    write_audit_html,
    write_deid_comparison_html,
    write_demo_summary_html,
    write_inspection_html,
    write_inventory_html,
    write_package_receipt_html,
    write_pixel_review_html,
    write_share_readiness_html,
)
from ddpt.share_readiness import run_share_readiness
from ddpt.sharing import create_package, create_verification_receipt
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
    inventory_json = reports_dir / "inventory.json"
    inventory_csv = reports_dir / "inventory.csv"
    inventory_html = reports_dir / "inventory.html"
    input_preview_png = reports_dir / "input-preview.png"
    anonymized_preview_png = reports_dir / "anonymized-preview.png"
    redacted_preview_png = reports_dir / "redacted-preview.png"
    inspection_json = reports_dir / "inspect.json"
    inspection_html = reports_dir / "inspect.html"
    audit_json = reports_dir / "audit.json"
    audit_html = reports_dir / "audit.html"
    deid_comparison_json = reports_dir / "deid-comparison.json"
    deid_comparison_html = reports_dir / "deid-comparison.html"
    validation_json = reports_dir / "validation.json"
    pixel_review_json = reports_dir / "pixel-review.json"
    pixel_review_html = reports_dir / "pixel-review.html"
    pixel_review_dir = reports_dir / "pixel-review"
    redaction_json = reports_dir / "redaction.json"
    summary_json = reports_dir / "demo-summary.json"
    summary_html = reports_dir / "demo-summary.html"
    audit_chain_json = reports_dir / "audit-chain.json"
    audit_chain_verify_json = reports_dir / "audit-chain-verify.json"
    manifest_json = share_dir / "manifest.json"
    package_path = share_dir / "package.ddpt"
    key_path = share_dir / "package.key"
    package_receipt_json = reports_dir / "package-receipt.json"
    package_receipt_html = reports_dir / "package-receipt.html"
    share_readiness_json = reports_dir / "share-readiness.json"
    share_readiness_html = reports_dir / "share-readiness.html"

    create_synthetic_dicom(input_dicom)
    render_dicom_preview(input_dicom, input_preview_png)

    inventory = build_inventory(input_dir)
    write_json(inventory_json, model_to_dict(inventory))
    write_inventory_csv(inventory_csv, inventory)
    write_inventory_html(inventory_html, inventory)

    inspection = inspect_dicom(input_dicom)
    write_json(inspection_json, model_to_dict(inspection))
    write_inspection_html(inspection_html, inspection)

    audit = anonymize_dicom(input_dicom, anonymized_dicom, profile)
    render_dicom_preview(anonymized_dicom, anonymized_preview_png)
    write_json(audit_json, model_to_dict(audit))
    write_audit_html(audit_html, audit)

    deid_comparison = compare_deidentification(input_dicom, anonymized_dicom)
    write_json(deid_comparison_json, model_to_dict(deid_comparison))
    write_deid_comparison_html(deid_comparison_html, deid_comparison)

    validation = validate_anonymized_dicom(anonymized_dicom)
    write_json(validation_json, model_to_dict(validation))

    redaction_rectangle = parse_rectangle(rectangle)
    pixel_review = create_pixel_review(
        anonymized_dicom,
        pixel_review_dir,
        rectangles=[redaction_rectangle],
    )
    write_json(pixel_review_json, model_to_dict(pixel_review))
    write_pixel_review_html(pixel_review_html, pixel_review)

    redaction = redact_pixels(anonymized_dicom, redacted_dicom, [redaction_rectangle])
    render_dicom_preview(redacted_dicom, redacted_preview_png)
    write_json(redaction_json, model_to_dict(redaction))

    manifest = create_package(
        outputs_dir,
        package_path,
        manifest_path=manifest_json,
        encrypt=True,
        key_output=key_path,
    )
    package_receipt = create_verification_receipt(package_path, key_path)
    write_json(package_receipt_json, model_to_dict(package_receipt))
    write_package_receipt_html(package_receipt_html, package_receipt)
    if not package_receipt.passed:
        raise ValueError("Package verification receipt failed")

    create_audit_chain(output_dir, audit_chain_json)
    audit_chain_verification = verify_audit_chain(audit_chain_json)
    write_json(audit_chain_verify_json, model_to_dict(audit_chain_verification))

    share_readiness = run_share_readiness(output_dir)
    write_json(share_readiness_json, model_to_dict(share_readiness))
    write_share_readiness_html(share_readiness_html, share_readiness)

    result = DemoPipelineResult(
        output_dir=str(output_dir),
        input_dicom=str(input_dicom),
        inventory_json=str(inventory_json),
        inventory_csv=str(inventory_csv),
        inventory_html=str(inventory_html),
        input_preview_png=str(input_preview_png),
        anonymized_preview_png=str(anonymized_preview_png),
        redacted_preview_png=str(redacted_preview_png),
        anonymized_dicom=str(anonymized_dicom),
        redacted_dicom=str(redacted_dicom),
        inspection_json=str(inspection_json),
        inspection_html=str(inspection_html),
        audit_json=str(audit_json),
        audit_html=str(audit_html),
        deid_comparison_json=str(deid_comparison_json),
        deid_comparison_html=str(deid_comparison_html),
        validation_json=str(validation_json),
        share_readiness_json=str(share_readiness_json),
        share_readiness_html=str(share_readiness_html),
        pixel_review_json=str(pixel_review_json),
        pixel_review_html=str(pixel_review_html),
        redaction_json=str(redaction_json),
        manifest_json=str(manifest_json),
        package_path=str(package_path),
        key_path=str(key_path),
        package_receipt_json=str(package_receipt_json),
        package_receipt_html=str(package_receipt_html),
        audit_chain_json=str(audit_chain_json),
        audit_chain_verify_json=str(audit_chain_verify_json),
        summary_html=str(summary_html),
        validation_passed=validation.passed,
        audit_chain_passed=audit_chain_verification.passed,
        package_entries=len(manifest.entries),
    )
    write_json(summary_json, model_to_dict(result))
    write_demo_summary_html(summary_html, result)
    return result
