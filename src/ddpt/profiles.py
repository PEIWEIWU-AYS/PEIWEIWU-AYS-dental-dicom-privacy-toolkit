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
        "ReferringPhysicianName",
        "RequestingPhysician",
        "OperatorsName",
        "InstitutionAddress",
        "DeviceSerialNumber",
        "StationName",
    ],
    "regenerate_uids": [
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "SOPInstanceUID",
    ],
    "remove_private_tags": True,
}


def load_profile(name_or_path: str) -> dict[str, Any]:
    candidate = Path(name_or_path)
    if candidate.exists():
        with candidate.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    if name_or_path == "dental-basic":
        return DEFAULT_PROFILE

    raise ValueError(f"Unknown anonymization profile: {name_or_path}")


def built_in_profiles() -> list[str]:
    return ["dental-basic"]


def describe_profile(name_or_path: str) -> dict[str, Any]:
    profile = load_profile(name_or_path)
    return {
        "name": profile.get("name", name_or_path),
        "replace_keywords": sorted(profile.get("replace", {}).keys()),
        "blank_keywords": sorted(profile.get("blank", [])),
        "regenerate_uid_keywords": sorted(profile.get("regenerate_uids", [])),
        "remove_private_tags": bool(profile.get("remove_private_tags", True)),
        "raw": profile,
    }
