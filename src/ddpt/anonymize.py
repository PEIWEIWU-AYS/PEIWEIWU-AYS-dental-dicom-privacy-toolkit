from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pydicom
from pydicom.uid import generate_uid

from ddpt.models import AnonymizationAction, AnonymizationAudit
from ddpt.profiles import load_profile
from ddpt.utils import ensure_parent, value_to_text


def anonymize_dicom(input_path: Path, output_path: Path, profile_name: str) -> AnonymizationAudit:
    dataset = pydicom.dcmread(input_path)
    profile = load_profile(profile_name)
    actions: list[AnonymizationAction] = []

    for keyword, config in profile.get("pseudonymize", {}).items():
        if keyword in dataset:
            replacement = _pseudonymize_value(dataset, keyword, config)
            actions.append(_action(dataset, keyword, "pseudonymize", replacement))
            dataset.data_element(keyword).value = replacement

    for keyword, replacement in profile.get("replace", {}).items():
        if keyword in dataset:
            actions.append(_action(dataset, keyword, "replace", replacement))
            dataset.data_element(keyword).value = replacement

    for keyword in profile.get("blank", []):
        if keyword in dataset:
            actions.append(_action(dataset, keyword, "blank", ""))
            dataset.data_element(keyword).value = ""

    date_shift = _date_shift_config(profile)
    for keyword in date_shift["keywords"]:
        if keyword in dataset:
            shifted = _shift_dicom_date(
                value_to_text(dataset.data_element(keyword).value),
                date_shift["offset_days"],
            )
            actions.append(_action(dataset, keyword, "date_shift", shifted))
            dataset.data_element(keyword).value = shifted

    for keyword in profile.get("regenerate_uids", []):
        if keyword in dataset:
            replacement = generate_uid()
            actions.append(_action(dataset, keyword, "regenerate_uid", replacement))
            dataset.data_element(keyword).value = replacement
            if keyword == "SOPInstanceUID" and getattr(dataset, "file_meta", None):
                dataset.file_meta.MediaStorageSOPInstanceUID = replacement

    remove_private_tags = bool(profile.get("remove_private_tags", True))
    if remove_private_tags:
        dataset.remove_private_tags()

    ensure_parent(output_path)
    dataset.save_as(output_path, enforce_file_format=True)

    return AnonymizationAudit(
        input_path=str(input_path),
        output_path=str(output_path),
        profile=str(profile.get("name", profile_name)),
        actions=actions,
        private_tags_removed=remove_private_tags,
    )


def plan_anonymization_actions(
    input_path: Path,
    profile_name: str,
    output_path: Path | None = None,
) -> AnonymizationAudit:
    dataset = pydicom.dcmread(input_path)
    profile = load_profile(profile_name)
    actions: list[AnonymizationAction] = []

    for keyword, config in profile.get("pseudonymize", {}).items():
        if keyword in dataset:
            replacement = _pseudonymize_value(dataset, keyword, config)
            actions.append(_action(dataset, keyword, "pseudonymize", replacement))

    for keyword, replacement in profile.get("replace", {}).items():
        if keyword in dataset:
            actions.append(_action(dataset, keyword, "replace", replacement))

    for keyword in profile.get("blank", []):
        if keyword in dataset:
            actions.append(_action(dataset, keyword, "blank", ""))

    date_shift = _date_shift_config(profile)
    for keyword in date_shift["keywords"]:
        if keyword in dataset:
            shifted = _shift_dicom_date(
                value_to_text(dataset.data_element(keyword).value),
                date_shift["offset_days"],
            )
            actions.append(_action(dataset, keyword, "date_shift", shifted))

    for keyword in profile.get("regenerate_uids", []):
        if keyword in dataset:
            actions.append(_action(dataset, keyword, "regenerate_uid", "<generated-uid>"))

    remove_private_tags = bool(profile.get("remove_private_tags", True))
    return AnonymizationAudit(
        input_path=str(input_path),
        output_path=str(output_path or ""),
        profile=str(profile.get("name", profile_name)),
        actions=actions,
        private_tags_removed=remove_private_tags,
    )


def _action(dataset: Any, keyword: str, action: str, after: Any) -> AnonymizationAction:
    element = dataset.data_element(keyword)
    return AnonymizationAction(
        tag=str(element.tag),
        keyword=keyword,
        action=action,
        before=value_to_text(element.value),
        after=value_to_text(after),
    )


def _pseudonymize_value(dataset: Any, target_keyword: str, config: Any) -> str:
    if isinstance(config, str):
        source_keyword = config
        prefix = ""
        length = 12
        namespace = ""
    elif isinstance(config, dict):
        source_keyword = str(config.get("source") or target_keyword)
        prefix = str(config.get("prefix", ""))
        length = int(config.get("length", 12) or 12)
        namespace = str(config.get("namespace", ""))
    else:
        source_keyword = target_keyword
        prefix = ""
        length = 12
        namespace = ""

    source_value = _dataset_value(dataset, source_keyword) or _dataset_value(
        dataset,
        target_keyword,
    )
    digest = hashlib.sha256(f"{namespace}|{source_keyword}|{source_value}".encode()).hexdigest()
    return f"{prefix}{digest[:length].upper()}"


def _dataset_value(dataset: Any, keyword: str) -> str:
    if keyword in dataset:
        return value_to_text(dataset.data_element(keyword).value)
    return ""


def _date_shift_config(profile: dict[str, Any]) -> dict[str, Any]:
    config = profile.get("date_shift") or {}
    if not isinstance(config, dict):
        return {"offset_days": 0, "keywords": []}
    return {
        "offset_days": int(config.get("offset_days", 0) or 0),
        "keywords": list(config.get("keywords", [])),
    }


def _shift_dicom_date(value: str, offset_days: int) -> str:
    if not value or len(value) != 8 or not value.isdigit():
        return ""
    try:
        date_value = datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        return ""
    shifted = date_value + timedelta(days=offset_days)
    return shifted.strftime("%Y%m%d")
