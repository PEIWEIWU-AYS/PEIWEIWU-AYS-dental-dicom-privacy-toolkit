from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydicom.datadict import tag_for_keyword

from ddpt.models import ProfileLintFinding, ProfileLintReport

DEFAULT_PROFILE = {
    "name": "dental-basic",
    "replace": {
        "PatientName": "ANONYMIZED^DENTAL",
        "PatientID": "DDPT-SYNTHETIC-ID",
        "AccessionNumber": "DDPT-ACCESSION",
        "StudyDescription": "Synthetic Dental Imaging Study",
        "SeriesDescription": "Synthetic Dental Imaging Series",
        "InstitutionName": "Synthetic Dental Clinic",
    },
    "blank": [
        "PatientBirthDate",
        "PatientAddress",
        "PatientTelephoneNumbers",
        "OtherPatientIDs",
        "OtherPatientNames",
        "PatientMotherBirthName",
        "ReferringPhysicianName",
        "RequestingPhysician",
        "OperatorsName",
        "PhysiciansOfRecord",
        "PerformingPhysicianName",
        "InstitutionAddress",
        "DeviceSerialNumber",
        "StationName",
        "ProtocolName",
        "StudyDate",
        "SeriesDate",
        "AcquisitionDate",
        "ContentDate",
        "StudyTime",
        "SeriesTime",
        "AcquisitionTime",
        "ContentTime",
    ],
    "regenerate_uids": [
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "SOPInstanceUID",
        "FrameOfReferenceUID",
    ],
    "remove_private_tags": True,
}

RESEARCH_SHARING_PROFILE = {
    "name": "dental-research-sharing",
    "description": "Dental research sharing profile with deterministic date shifting.",
    "replace": {
        "PatientName": "ANONYMIZED^DENTAL",
        "PatientID": "DDPT-SYNTHETIC-ID",
        "AccessionNumber": "DDPT-RES-ACC",
        "StudyDescription": "Research Dental Imaging Study",
        "SeriesDescription": "Research Dental Imaging Series",
        "InstitutionName": "Research Dental Institution",
    },
    "blank": [
        "PatientBirthDate",
        "PatientAddress",
        "PatientTelephoneNumbers",
        "OtherPatientIDs",
        "OtherPatientNames",
        "PatientMotherBirthName",
        "ReferringPhysicianName",
        "RequestingPhysician",
        "OperatorsName",
        "PhysiciansOfRecord",
        "PerformingPhysicianName",
        "InstitutionAddress",
        "DeviceSerialNumber",
        "StationName",
        "ProtocolName",
        "StudyTime",
        "SeriesTime",
        "AcquisitionTime",
        "ContentTime",
    ],
    "date_shift": {
        "offset_days": -3650,
        "keywords": [
            "StudyDate",
            "SeriesDate",
            "AcquisitionDate",
            "ContentDate",
        ],
    },
    "regenerate_uids": [
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "SOPInstanceUID",
        "FrameOfReferenceUID",
    ],
    "remove_private_tags": True,
}

LINKABLE_RESEARCH_PROFILE = {
    "name": "dental-linkable-research",
    "description": (
        "Dental research profile with deterministic patient pseudonyms for "
        "synthetic longitudinal demos."
    ),
    "pseudonymize": {
        "PatientName": {
            "source": "PatientID",
            "prefix": "ANONYMIZED^",
            "length": 12,
            "namespace": "ddpt-linkable-research-v1",
        },
        "PatientID": {
            "source": "PatientID",
            "prefix": "DDPT-LINK-",
            "length": 12,
            "namespace": "ddpt-linkable-research-v1",
        },
    },
    "replace": {
        "AccessionNumber": "DDPT-LINK-ACC",
        "StudyDescription": "Linkable Research Dental Imaging Study",
        "SeriesDescription": "Linkable Research Dental Imaging Series",
        "InstitutionName": "Linkable Research Dental Institution",
    },
    "blank": [
        "PatientBirthDate",
        "PatientAddress",
        "PatientTelephoneNumbers",
        "OtherPatientIDs",
        "OtherPatientNames",
        "PatientMotherBirthName",
        "ReferringPhysicianName",
        "RequestingPhysician",
        "OperatorsName",
        "PhysiciansOfRecord",
        "PerformingPhysicianName",
        "InstitutionAddress",
        "DeviceSerialNumber",
        "StationName",
        "ProtocolName",
        "StudyTime",
        "SeriesTime",
        "AcquisitionTime",
        "ContentTime",
    ],
    "date_shift": {
        "offset_days": -3650,
        "keywords": [
            "StudyDate",
            "SeriesDate",
            "AcquisitionDate",
            "ContentDate",
        ],
    },
    "regenerate_uids": [
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "SOPInstanceUID",
        "FrameOfReferenceUID",
    ],
    "remove_private_tags": True,
}

BUILT_IN_PROFILE_MAP = {
    "dental-basic": DEFAULT_PROFILE,
    "dental-linkable-research": LINKABLE_RESEARCH_PROFILE,
    "dental-research-sharing": RESEARCH_SHARING_PROFILE,
}


def load_profile(name_or_path: str) -> dict[str, Any]:
    candidate = Path(name_or_path)
    if candidate.exists():
        with candidate.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    if name_or_path in BUILT_IN_PROFILE_MAP:
        return BUILT_IN_PROFILE_MAP[name_or_path]

    raise ValueError(f"Unknown anonymization profile: {name_or_path}")


def built_in_profiles() -> list[str]:
    return sorted(BUILT_IN_PROFILE_MAP)


def write_profile_template(output_path: Path, overwrite: bool = False) -> Path:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Profile already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(DEFAULT_PROFILE, handle, sort_keys=False, allow_unicode=True)
    return output_path


def describe_profile(name_or_path: str) -> dict[str, Any]:
    profile = load_profile(name_or_path)
    date_shift = profile.get("date_shift", {})
    return {
        "name": profile.get("name", name_or_path),
        "pseudonymize_keywords": sorted(profile.get("pseudonymize", {}).keys()),
        "replace_keywords": sorted(profile.get("replace", {}).keys()),
        "blank_keywords": sorted(profile.get("blank", [])),
        "date_shift_keywords": sorted(date_shift.get("keywords", [])),
        "date_shift_offset_days": int(date_shift.get("offset_days", 0) or 0),
        "regenerate_uid_keywords": sorted(profile.get("regenerate_uids", [])),
        "remove_private_tags": bool(profile.get("remove_private_tags", True)),
        "raw": profile,
    }


def lint_profile(name_or_path: str) -> ProfileLintReport:
    from ddpt.policy import profile_coverage

    findings: list[ProfileLintFinding] = []
    try:
        profile = load_profile(name_or_path)
    except Exception as exc:
        finding = ProfileLintFinding(
            severity="error",
            rule_id="profile-load-error",
            message=str(exc),
        )
        return ProfileLintReport(
            profile=name_or_path,
            passed=False,
            error_count=1,
            warning_count=0,
            covered_items=0,
            total_policy_items=0,
            high_risk_uncovered=[],
            medium_risk_uncovered=[],
            findings=[finding],
        )

    profile_name = (
        str(profile.get("name", name_or_path)) if isinstance(profile, dict) else name_or_path
    )
    if not isinstance(profile, dict):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="profile-shape",
                message="Profile must be a YAML mapping.",
            )
        )
        return _profile_lint_report(profile_name, findings, None)

    _lint_replace(profile, findings)
    _lint_pseudonymize(profile, findings)
    _lint_keyword_list(profile, "blank", findings)
    _lint_keyword_list(profile, "regenerate_uids", findings)
    _lint_date_shift(profile, findings)
    _lint_remove_private_tags(profile, findings)
    _lint_action_conflicts(profile, findings)

    coverage = None
    try:
        coverage = profile_coverage(name_or_path)
        for keyword in coverage.high_risk_uncovered:
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="high-risk-uncovered",
                    keyword=keyword,
                    message=f"High-risk policy item is not covered: {keyword}",
                )
            )
        for keyword in coverage.medium_risk_uncovered:
            findings.append(
                ProfileLintFinding(
                    severity="warning",
                    rule_id="medium-risk-uncovered",
                    keyword=keyword,
                    message=f"Medium-risk policy item is not covered: {keyword}",
                )
            )
    except Exception as exc:
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="coverage-error",
                message=str(exc),
            )
        )

    return _profile_lint_report(profile_name, findings, coverage)


def _lint_replace(profile: dict[str, Any], findings: list[ProfileLintFinding]) -> None:
    replace = profile.get("replace", {})
    if not isinstance(replace, dict):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="replace-shape",
                message="replace must be a mapping of DICOM keyword to replacement value.",
            )
        )
        return
    for keyword, value in replace.items():
        _lint_keyword(keyword, findings)
        if value is None:
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="replace-empty",
                    keyword=str(keyword),
                    message="Replacement value must not be null.",
                )
            )
        if isinstance(value, str) and len(value) > 64:
            findings.append(
                ProfileLintFinding(
                    severity="warning",
                    rule_id="replace-long-value",
                    keyword=str(keyword),
                    message="Replacement value is longer than 64 characters.",
                )
            )


def _lint_pseudonymize(profile: dict[str, Any], findings: list[ProfileLintFinding]) -> None:
    pseudonymize = profile.get("pseudonymize", {})
    if pseudonymize in (None, ""):
        return
    if not isinstance(pseudonymize, dict):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="pseudonymize-shape",
                message=(
                    "pseudonymize must be a mapping of target DICOM keyword to "
                    "source keyword or configuration."
                ),
            )
        )
        return

    allowed_keys = {"source", "prefix", "length", "namespace"}
    for keyword, config in pseudonymize.items():
        _lint_keyword(keyword, findings)
        if isinstance(config, str):
            _lint_keyword(config, findings)
            continue
        if not isinstance(config, dict):
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="pseudonymize-config-shape",
                    keyword=str(keyword),
                    message="pseudonymize values must be a source keyword or mapping.",
                )
            )
            continue

        unknown_keys = sorted(set(config) - allowed_keys)
        for unknown_key in unknown_keys:
            findings.append(
                ProfileLintFinding(
                    severity="warning",
                    rule_id="pseudonymize-unknown-key",
                    keyword=str(keyword),
                    message=f"Unknown pseudonymize option: {unknown_key}",
                )
            )

        source = config.get("source")
        if not isinstance(source, str) or not source:
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="pseudonymize-source",
                    keyword=str(keyword),
                    message="pseudonymize.source must be a DICOM keyword.",
                )
            )
        else:
            _lint_keyword(source, findings)

        prefix = config.get("prefix", "")
        if not isinstance(prefix, str):
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="pseudonymize-prefix",
                    keyword=str(keyword),
                    message="pseudonymize.prefix must be a string.",
                )
            )

        namespace = config.get("namespace", "")
        if not isinstance(namespace, str):
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="pseudonymize-namespace",
                    keyword=str(keyword),
                    message="pseudonymize.namespace must be a string.",
                )
            )

        length = config.get("length", 12)
        if not isinstance(length, int) or length < 6 or length > 48:
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="pseudonymize-length",
                    keyword=str(keyword),
                    message="pseudonymize.length must be an integer from 6 to 48.",
                )
            )


def _lint_keyword_list(
    profile: dict[str, Any],
    field: str,
    findings: list[ProfileLintFinding],
) -> None:
    values = profile.get(field, [])
    if not isinstance(values, list):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id=f"{field}-shape",
                message=f"{field} must be a list of DICOM keywords.",
            )
        )
        return
    for keyword in values:
        _lint_keyword(keyword, findings)


def _lint_date_shift(profile: dict[str, Any], findings: list[ProfileLintFinding]) -> None:
    config = profile.get("date_shift")
    if config is None or config == "":
        return
    if not isinstance(config, dict):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="date-shift-shape",
                message="date_shift must be a mapping with offset_days and keywords.",
            )
        )
        return
    offset = config.get("offset_days")
    if not isinstance(offset, int):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="date-shift-offset",
                message="date_shift.offset_days must be an integer.",
            )
        )
    keywords = config.get("keywords", [])
    if not isinstance(keywords, list):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="date-shift-keywords",
                message="date_shift.keywords must be a list of DICOM date keywords.",
            )
        )
        return
    for keyword in keywords:
        _lint_keyword(keyword, findings)
        if isinstance(keyword, str) and not keyword.endswith("Date"):
            findings.append(
                ProfileLintFinding(
                    severity="warning",
                    rule_id="date-shift-non-date-keyword",
                    keyword=keyword,
                    message="date_shift should normally be used with DICOM date keywords.",
                )
            )


def _lint_remove_private_tags(
    profile: dict[str, Any],
    findings: list[ProfileLintFinding],
) -> None:
    value = profile.get("remove_private_tags", True)
    if not isinstance(value, bool):
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="remove-private-tags-shape",
                message="remove_private_tags must be true or false.",
            )
        )
    elif value is False:
        findings.append(
            ProfileLintFinding(
                severity="warning",
                rule_id="private-tags-retained",
                message="Private tags are retained; review vendor-specific identifying risk.",
            )
        )


def _lint_action_conflicts(
    profile: dict[str, Any],
    findings: list[ProfileLintFinding],
) -> None:
    action_map: dict[str, list[str]] = {}
    replace = profile.get("replace", {}) or {}
    if isinstance(replace, dict):
        for keyword in replace.keys():
            action_map.setdefault(str(keyword), []).append("replace")
    pseudonymize = profile.get("pseudonymize", {}) or {}
    if isinstance(pseudonymize, dict):
        for keyword in pseudonymize.keys():
            action_map.setdefault(str(keyword), []).append("pseudonymize")
    for field in ("blank", "regenerate_uids"):
        values = profile.get(field, []) or []
        if isinstance(values, list):
            for keyword in values:
                action_map.setdefault(str(keyword), []).append(field)
    date_shift = profile.get("date_shift", {}) or {}
    if isinstance(date_shift, dict) and isinstance(date_shift.get("keywords", []), list):
        for keyword in date_shift.get("keywords", []) or []:
            action_map.setdefault(str(keyword), []).append("date_shift")

    for keyword, actions in action_map.items():
        if len(actions) > 1:
            findings.append(
                ProfileLintFinding(
                    severity="error",
                    rule_id="conflicting-actions",
                    keyword=keyword,
                    message=f"Keyword appears in multiple actions: {', '.join(actions)}",
                )
            )


def _lint_keyword(keyword: Any, findings: list[ProfileLintFinding]) -> None:
    if not isinstance(keyword, str) or not keyword:
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="keyword-shape",
                message=f"Invalid DICOM keyword: {keyword!r}",
            )
        )
        return
    if tag_for_keyword(keyword) is None:
        findings.append(
            ProfileLintFinding(
                severity="error",
                rule_id="unknown-keyword",
                keyword=keyword,
                message=f"Unknown DICOM keyword: {keyword}",
            )
        )


def _profile_lint_report(profile_name: str, findings, coverage) -> ProfileLintReport:
    error_count = sum(1 for finding in findings if finding.severity == "error")
    warning_count = sum(1 for finding in findings if finding.severity == "warning")
    return ProfileLintReport(
        profile=profile_name,
        passed=error_count == 0,
        error_count=error_count,
        warning_count=warning_count,
        covered_items=coverage.covered_items if coverage else 0,
        total_policy_items=coverage.total_items if coverage else 0,
        high_risk_uncovered=coverage.high_risk_uncovered if coverage else [],
        medium_risk_uncovered=coverage.medium_risk_uncovered if coverage else [],
        findings=findings,
    )
