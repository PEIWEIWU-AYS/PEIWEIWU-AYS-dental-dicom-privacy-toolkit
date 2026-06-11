from __future__ import annotations

from pathlib import Path
from typing import Any

import pydicom
from pydicom.uid import UID

from ddpt.anonymize import _date_shift_config, _pseudonymize_value, _shift_dicom_date
from ddpt.models import ProfileConformanceCheck, ProfileConformanceReport
from ddpt.profiles import load_profile
from ddpt.utils import value_to_text


def verify_profile_conformance(
    source_path: Path,
    anonymized_path: Path,
    profile_name: str = "dental-basic",
) -> ProfileConformanceReport:
    source = pydicom.dcmread(source_path)
    anonymized = pydicom.dcmread(anonymized_path)
    profile = load_profile(profile_name)
    checks: list[ProfileConformanceCheck] = []

    for keyword, config in profile.get("pseudonymize", {}).items():
        if keyword not in source:
            checks.append(_skip(keyword, "pseudonymize", "source keyword not present"))
            continue
        expected = _pseudonymize_value(source, keyword, config)
        checks.append(
            _value_check(
                source,
                anonymized,
                keyword,
                "pseudonymize",
                expected,
                "deterministic pseudonym must match profile configuration",
            )
        )

    for keyword, replacement in profile.get("replace", {}).items():
        if keyword not in source:
            checks.append(_skip(keyword, "replace", "source keyword not present"))
            continue
        checks.append(
            _value_check(
                source,
                anonymized,
                keyword,
                "replace",
                str(replacement),
                "replacement must match profile configuration",
            )
        )

    for keyword in profile.get("blank", []):
        if keyword not in source and keyword not in anonymized:
            checks.append(_skip(keyword, "blank", "keyword not present"))
            continue
        actual = _dataset_value(anonymized, keyword)
        checks.append(
            _check(
                keyword=keyword,
                action="blank",
                passed=actual == "",
                original=_dataset_value(source, keyword),
                expected="",
                actual=actual,
                message=(
                    "value is blank or absent"
                    if actual == ""
                    else "value should be blank or absent"
                ),
            )
        )

    date_shift = _date_shift_config(profile)
    for keyword in date_shift["keywords"]:
        if keyword not in source:
            checks.append(_skip(keyword, "date_shift", "source keyword not present"))
            continue
        original = _dataset_value(source, keyword)
        expected = _shift_dicom_date(original, int(date_shift["offset_days"]))
        checks.append(
            _value_check(
                source,
                anonymized,
                keyword,
                "date_shift",
                expected,
                "shifted date must match profile offset",
            )
        )

    for keyword in profile.get("regenerate_uids", []):
        if keyword not in source:
            checks.append(_skip(keyword, "regenerate_uid", "source keyword not present"))
            continue
        original = _dataset_value(source, keyword)
        actual = _dataset_value(anonymized, keyword)
        passed = bool(actual) and actual != original and _is_valid_uid(actual)
        checks.append(
            _check(
                keyword=keyword,
                action="regenerate_uid",
                passed=passed,
                original=original,
                expected="new valid UID different from source",
                actual=actual,
                message=(
                    "UID was regenerated and remains valid"
                    if passed
                    else "UID should be regenerated, non-empty, valid, and different"
                ),
            )
        )

    remove_private_tags = bool(profile.get("remove_private_tags", True))
    if remove_private_tags:
        private_tags = [
            str(element.tag) for element in anonymized.iterall() if element.tag.is_private
        ]
        checks.append(
            _check(
                keyword="PrivateTags",
                action="remove_private_tags",
                passed=not private_tags,
                original=str(
                    sum(1 for element in source.iterall() if element.tag.is_private)
                ),
                expected="0",
                actual=str(len(private_tags)),
                message=(
                    "private tags removed"
                    if not private_tags
                    else f"private tags remain: {', '.join(private_tags)}"
                ),
            )
        )
    else:
        checks.append(
            _skip("PrivateTags", "remove_private_tags", "profile does not require removal")
        )

    failed = sum(1 for item in checks if item.status == "fail")
    passed = sum(1 for item in checks if item.status == "pass")
    skipped = sum(1 for item in checks if item.status == "skip")
    return ProfileConformanceReport(
        source_path=str(source_path.resolve()),
        anonymized_path=str(anonymized_path.resolve()),
        profile=str(profile.get("name", profile_name)),
        passed=failed == 0,
        total_checks=len(checks),
        passed_checks=passed,
        failed_checks=failed,
        skipped_checks=skipped,
        checks=checks,
    )


def _value_check(
    source: Any,
    anonymized: Any,
    keyword: str,
    action: str,
    expected: str,
    success_message: str,
) -> ProfileConformanceCheck:
    actual = _dataset_value(anonymized, keyword)
    passed = actual == expected
    return _check(
        keyword=keyword,
        action=action,
        passed=passed,
        original=_dataset_value(source, keyword),
        expected=expected,
        actual=actual,
        message=success_message if passed else "actual value does not match profile",
    )


def _dataset_value(dataset: Any, keyword: str) -> str:
    if keyword in dataset:
        return value_to_text(dataset.data_element(keyword).value)
    return ""


def _is_valid_uid(value: str) -> bool:
    try:
        return bool(UID(value).is_valid)
    except (TypeError, ValueError):
        return False


def _check(
    keyword: str,
    action: str,
    passed: bool,
    original: str,
    expected: str,
    actual: str,
    message: str,
) -> ProfileConformanceCheck:
    return ProfileConformanceCheck(
        keyword=keyword,
        action=action,
        status="pass" if passed else "fail",
        passed=passed,
        original=original,
        expected=expected,
        actual=actual,
        message=message,
    )


def _skip(keyword: str, action: str, message: str) -> ProfileConformanceCheck:
    return ProfileConformanceCheck(
        keyword=keyword,
        action=action,
        status="skip",
        passed=True,
        original="",
        expected="",
        actual="",
        message=message,
    )
