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


def write_profile_template(output_path: Path, overwrite: bool = False) -> Path:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Profile already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(DEFAULT_PROFILE, handle, sort_keys=False, allow_unicode=True)
    return output_path


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
