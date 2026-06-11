from __future__ import annotations

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

    for keyword, replacement in profile.get("replace", {}).items():
        if keyword in dataset:
            actions.append(_action(dataset, keyword, "replace", replacement))
            dataset.data_element(keyword).value = replacement

    for keyword in profile.get("blank", []):
        if keyword in dataset:
            actions.append(_action(dataset, keyword, "blank", ""))
            dataset.data_element(keyword).value = ""

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


def _action(dataset: Any, keyword: str, action: str, after: Any) -> AnonymizationAction:
    element = dataset.data_element(keyword)
    return AnonymizationAction(
        tag=str(element.tag),
        keyword=keyword,
        action=action,
        before=value_to_text(element.value),
        after=value_to_text(after),
    )
