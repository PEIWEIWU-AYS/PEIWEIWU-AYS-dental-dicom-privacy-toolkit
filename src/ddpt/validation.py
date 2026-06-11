from __future__ import annotations

from pathlib import Path

import pydicom

from ddpt.models import ValidationCheck, ValidationReport
from ddpt.utils import value_to_text

EXPECTED_REPLACEMENTS = {
    "PatientName": ("ANONYMIZED^DENTAL", "ANONYMIZED^"),
    "PatientID": ("DDPT-SYNTHETIC-ID", "DDPT-LINK-"),
}

EXPECTED_BLANKS = [
    "PatientBirthDate",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "ReferringPhysicianName",
    "RequestingPhysician",
    "OperatorsName",
    "InstitutionAddress",
    "DeviceSerialNumber",
    "StationName",
]


def validate_anonymized_dicom(path: Path) -> ValidationReport:
    dataset = pydicom.dcmread(path)
    checks: list[ValidationCheck] = []
    warnings: list[str] = []

    for keyword, allowed_values in EXPECTED_REPLACEMENTS.items():
        actual = value_to_text(dataset.get(keyword, ""))
        expected_exact, allowed_prefix = allowed_values
        passed = actual == expected_exact or actual.startswith(allowed_prefix)
        checks.append(
            ValidationCheck(
                name=f"{keyword} replacement",
                passed=passed,
                message=(
                    f"expected {expected_exact!r} or prefix {allowed_prefix!r}, "
                    f"found {actual!r}"
                ),
            )
        )

    for keyword in EXPECTED_BLANKS:
        actual = value_to_text(dataset.get(keyword, ""))
        checks.append(
            ValidationCheck(
                name=f"{keyword} blank",
                passed=actual == "",
                message=f"expected blank value, found {actual!r}",
            )
        )

    private_tags = [str(element.tag) for element in dataset.iterall() if element.tag.is_private]
    checks.append(
        ValidationCheck(
            name="private tags removed",
            passed=not private_tags,
            message="no private tags found" if not private_tags else ", ".join(private_tags),
        )
    )

    burned_in = value_to_text(dataset.get("BurnedInAnnotation", ""))
    if burned_in and burned_in.upper() != "NO":
        warnings.append(
            "BurnedInAnnotation is not NO. Pixel-level identifiers require separate review."
        )
    elif not burned_in:
        warnings.append("BurnedInAnnotation is missing. Pixel-level review may still be needed.")

    passed = all(check.passed for check in checks)
    return ValidationReport(
        file_path=str(path),
        passed=passed,
        checks=checks,
        warnings=warnings,
    )
