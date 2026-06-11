from __future__ import annotations

from pathlib import Path

import pydicom

from ddpt.anonymize import anonymize_dicom
from ddpt.deid_compare import compare_deidentification
from ddpt.filename_privacy import scan_filename_privacy
from ddpt.models import (
    PrivacyRegressionCaseResult,
    PrivacyRegressionCheck,
    PrivacyRegressionSuiteReport,
)
from ddpt.pixel_review import create_pixel_review
from ddpt.pixel_risk import scan_pixel_risk
from ddpt.pixels import parse_rectangle
from ddpt.profile_verify import verify_profile_conformance
from ddpt.remediation import build_privacy_remediation_plan
from ddpt.reports import (
    model_to_dict,
    write_deid_comparison_html,
    write_filename_privacy_html,
    write_pixel_review_html,
    write_pixel_risk_scan_html,
    write_privacy_remediation_html,
    write_profile_conformance_html,
)
from ddpt.synthetic import create_synthetic_dicom
from ddpt.utils import write_json

BOUNDARY_NOTES = [
    "Synthetic regression fixtures only; do not place real patient DICOM in this suite.",
    "A passing regression suite means expected guardrails fired on known synthetic cases.",
    (
        "This is not legal, regulatory, clinical, security, or complete "
        "de-identification certification."
    ),
]


def run_privacy_regression_suite(output_dir: Path) -> PrivacyRegressionSuiteReport:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = [
        _metadata_case(output_dir),
        _filename_private_tag_case(output_dir),
        _pixel_risk_case(output_dir),
        _linkable_pseudonym_case(output_dir),
    ]
    passed_cases = sum(1 for case in cases if case.passed)
    return PrivacyRegressionSuiteReport(
        output_dir=str(output_dir),
        passed=passed_cases == len(cases),
        total_cases=len(cases),
        passed_cases=passed_cases,
        failed_cases=len(cases) - passed_cases,
        cases=cases,
        boundary_notes=BOUNDARY_NOTES,
    )


def _metadata_case(output_dir: Path) -> PrivacyRegressionCaseResult:
    case_dir = output_dir / "metadata-direct-identifiers"
    input_path = case_dir / "input" / "metadata-direct.dcm"
    anonymized_path = case_dir / "outputs" / "metadata-direct.anonymized.dcm"
    reports_dir = case_dir / "reports"
    create_synthetic_dicom(
        input_path,
        patient_name="DOE^JANE",
        patient_id="MRN-123456",
        study_description="Jane Doe Mandibular CBCT",
    )

    remediation = build_privacy_remediation_plan(input_path, profile="dental-basic")
    remediation_json = reports_dir / "remediation-plan.json"
    remediation_html = reports_dir / "remediation-plan.html"
    write_json(remediation_json, model_to_dict(remediation))
    write_privacy_remediation_html(remediation_html, remediation)

    anonymize_dicom(input_path, anonymized_path, "dental-basic")
    comparison = compare_deidentification(input_path, anonymized_path)
    comparison_json = reports_dir / "deid-comparison.json"
    comparison_html = reports_dir / "deid-comparison.html"
    write_json(comparison_json, model_to_dict(comparison))
    write_deid_comparison_html(comparison_html, comparison)

    conformance = verify_profile_conformance(
        input_path,
        anonymized_path,
        profile_name="dental-basic",
    )
    conformance_json = reports_dir / "profile-conformance.json"
    conformance_html = reports_dir / "profile-conformance.html"
    write_json(conformance_json, model_to_dict(conformance))
    write_profile_conformance_html(conformance_html, conformance)

    checks = [
        _check(
            "metadata-risk-covered",
            remediation.passed and remediation.covered_items > 0,
            "High/medium synthetic metadata findings are covered by the profile.",
            [
                str(remediation_json),
                f"covered={remediation.covered_items}/{remediation.total_items}",
            ],
        ),
        _check(
            "deid-comparison-clean",
            comparison.passed
            and not comparison.residual_high_risk_keywords
            and not comparison.residual_medium_risk_keywords,
            "Before/after comparison has no residual high/medium policy keywords.",
            [
                str(comparison_json),
                f"residual_high={len(comparison.residual_high_risk_keywords)}",
                f"residual_medium={len(comparison.residual_medium_risk_keywords)}",
            ],
        ),
        _check(
            "profile-conformance",
            conformance.passed,
            "Anonymized output conforms to the selected profile.",
            [str(conformance_json), f"failed_checks={conformance.failed_checks}"],
        ),
    ]
    return _case(
        "metadata-direct-identifiers",
        "Metadata direct identifier removal",
        [input_path],
        [
            remediation_json,
            remediation_html,
            comparison_json,
            comparison_html,
            conformance_json,
            conformance_html,
        ],
        checks,
    )


def _filename_private_tag_case(output_dir: Path) -> PrivacyRegressionCaseResult:
    case_dir = output_dir / "filename-private-tags"
    input_path = case_dir / "input" / "patient-123456" / "case-20260101.dcm"
    anonymized_path = case_dir / "outputs" / "filename-private.anonymized.dcm"
    reports_dir = case_dir / "reports"
    create_synthetic_dicom(
        input_path,
        patient_name="PRIVATE^TAG",
        patient_id="CASE-123456",
    )
    _add_private_tag(input_path)

    filename_report = scan_filename_privacy(case_dir / "input")
    filename_json = reports_dir / "filename-privacy.json"
    filename_html = reports_dir / "filename-privacy.html"
    write_json(filename_json, model_to_dict(filename_report))
    write_filename_privacy_html(filename_html, filename_report)

    anonymize_dicom(input_path, anonymized_path, "dental-basic")
    comparison = compare_deidentification(input_path, anonymized_path)
    comparison_json = reports_dir / "deid-comparison.json"
    comparison_html = reports_dir / "deid-comparison.html"
    write_json(comparison_json, model_to_dict(comparison))
    write_deid_comparison_html(comparison_html, comparison)
    private_after = _private_tag_count(anonymized_path)

    checks = [
        _check(
            "filename-risk-detected",
            not filename_report.passed and filename_report.findings_count > 0,
            "Filename scanner detects synthetic patient/case identifiers in paths.",
            [
                str(filename_json),
                f"findings={filename_report.findings_count}",
                f"high={filename_report.high_findings}",
                f"medium={filename_report.medium_findings}",
            ],
        ),
        _check(
            "private-tags-removed",
            private_after == 0 and comparison.private_tags_after == 0,
            "Anonymization removes synthetic private tags.",
            [
                str(comparison_json),
                f"private_after={private_after}",
                f"comparison_private_after={comparison.private_tags_after}",
            ],
        ),
    ]
    return _case(
        "filename-private-tags",
        "Filename risk and private tag removal",
        [input_path],
        [filename_json, filename_html, comparison_json, comparison_html],
        checks,
    )


def _pixel_risk_case(output_dir: Path) -> PrivacyRegressionCaseResult:
    case_dir = output_dir / "pixel-burned-in-risk"
    input_path = case_dir / "input" / "pixel-risk.dcm"
    reports_dir = case_dir / "reports"
    create_synthetic_dicom(input_path)
    dataset = pydicom.dcmread(input_path)
    dataset.BurnedInAnnotation = "YES"
    dataset.save_as(input_path, enforce_file_format=True)

    pixel_risk = scan_pixel_risk(input_path)
    pixel_json = reports_dir / "pixel-risk.json"
    pixel_html = reports_dir / "pixel-risk.html"
    write_json(pixel_json, model_to_dict(pixel_risk))
    write_pixel_risk_scan_html(pixel_html, pixel_risk)

    pixel_review = create_pixel_review(
        input_path,
        reports_dir / "pixel-review",
        rectangles=[parse_rectangle("1,0,1,1")],
    )
    review_json = reports_dir / "pixel-review.json"
    review_html = reports_dir / "pixel-review.html"
    write_json(review_json, model_to_dict(pixel_review))
    write_pixel_review_html(review_html, pixel_review)

    burned_in_signal = next(
        signal for signal in pixel_risk.signals if signal.id == "burned-in-annotation"
    )
    checks = [
        _check(
            "pixel-risk-detected",
            not pixel_risk.passed and not burned_in_signal.passed,
            "Pixel risk scan flags BurnedInAnnotation=YES as requiring review.",
            [
                str(pixel_json),
                f"burned_in={pixel_risk.burned_in_annotation}",
                f"signal_passed={burned_in_signal.passed}",
            ],
        ),
        _check(
            "pixel-review-evidence",
            bool(pixel_review.regions)
            and Path(pixel_review.overlay_preview_png).is_file()
            and Path(pixel_review.redacted_preview_png).is_file(),
            "Pixel review creates overlay and redacted PNG evidence.",
            [
                str(review_json),
                pixel_review.overlay_preview_png,
                pixel_review.redacted_preview_png,
            ],
        ),
    ]
    return _case(
        "pixel-burned-in-risk",
        "Burned-in pixel risk signal",
        [input_path],
        [pixel_json, pixel_html, review_json, review_html],
        checks,
    )


def _linkable_pseudonym_case(output_dir: Path) -> PrivacyRegressionCaseResult:
    case_dir = output_dir / "linkable-pseudonym"
    first = case_dir / "input" / "first.dcm"
    second = case_dir / "input" / "second.dcm"
    first_out = case_dir / "outputs" / "first.linkable.dcm"
    second_out = case_dir / "outputs" / "second.linkable.dcm"
    reports_dir = case_dir / "reports"
    create_synthetic_dicom(first, patient_name="ALPHA^ONE", patient_id="CLINIC-777")
    create_synthetic_dicom(second, patient_name="BETA^TWO", patient_id="CLINIC-777")

    anonymize_dicom(first, first_out, "dental-linkable-research")
    anonymize_dicom(second, second_out, "dental-linkable-research")
    first_comparison = compare_deidentification(first, first_out)
    second_comparison = compare_deidentification(second, second_out)
    first_json = reports_dir / "first-deid-comparison.json"
    second_json = reports_dir / "second-deid-comparison.json"
    write_json(first_json, model_to_dict(first_comparison))
    write_json(second_json, model_to_dict(second_comparison))

    first_dataset = pydicom.dcmread(first_out, stop_before_pixels=True)
    second_dataset = pydicom.dcmread(second_out, stop_before_pixels=True)
    first_name = str(first_dataset.PatientName)
    second_name = str(second_dataset.PatientName)
    first_id = str(first_dataset.PatientID)
    second_id = str(second_dataset.PatientID)

    checks = [
        _check(
            "stable-pseudonym",
            first_name == second_name
            and first_id == second_id
            and first_id.startswith("DDPT-LINK-"),
            "Same synthetic source PatientID maps to a stable linkable pseudonym.",
            [f"first_id={first_id}", f"second_id={second_id}"],
        ),
        _check(
            "source-names-removed",
            "ALPHA" not in first_name and "BETA" not in second_name,
            "Original synthetic names are not retained in anonymized outputs.",
            [f"first_name={first_name}", f"second_name={second_name}"],
        ),
        _check(
            "linkable-comparisons-clean",
            first_comparison.passed and second_comparison.passed,
            "Both linkable pseudonymization outputs pass de-identification comparison.",
            [str(first_json), str(second_json)],
        ),
    ]
    return _case(
        "linkable-pseudonym",
        "Stable linkable research pseudonym",
        [first, second],
        [first_json, second_json],
        checks,
    )


def _add_private_tag(path: Path) -> None:
    dataset = pydicom.dcmread(path)
    dataset.add_new((0x0011, 0x0010), "LO", "DDPT_PRIVATE_CREATOR")
    dataset.add_new((0x0011, 0x1001), "LO", "SYNTHETIC-PRIVATE-ID")
    dataset.save_as(path, enforce_file_format=True)


def _private_tag_count(path: Path) -> int:
    dataset = pydicom.dcmread(path, stop_before_pixels=True)
    return sum(1 for element in dataset.iterall() if element.tag.is_private)


def _case(
    case_id: str,
    title: str,
    input_paths: list[Path],
    artifact_paths: list[Path],
    checks: list[PrivacyRegressionCheck],
) -> PrivacyRegressionCaseResult:
    return PrivacyRegressionCaseResult(
        id=case_id,
        title=title,
        passed=all(check.passed for check in checks),
        input_paths=[str(path) for path in input_paths],
        artifact_paths=[str(path) for path in artifact_paths],
        checks=checks,
    )


def _check(
    check_id: str,
    passed: bool,
    message: str,
    evidence: list[str],
) -> PrivacyRegressionCheck:
    return PrivacyRegressionCheck(
        id=check_id,
        passed=passed,
        message=message,
        evidence=evidence,
    )
