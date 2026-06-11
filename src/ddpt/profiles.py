from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

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

BUILT_IN_PROFILE_MAP = {
    "dental-basic": DEFAULT_PROFILE,
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
        "replace_keywords": sorted(profile.get("replace", {}).keys()),
        "blank_keywords": sorted(profile.get("blank", [])),
        "date_shift_keywords": sorted(date_shift.get("keywords", [])),
        "date_shift_offset_days": int(date_shift.get("offset_days", 0) or 0),
        "regenerate_uid_keywords": sorted(profile.get("regenerate_uids", [])),
        "remove_private_tags": bool(profile.get("remove_private_tags", True)),
        "raw": profile,
    }
