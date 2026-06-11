from __future__ import annotations

from pathlib import Path

import pydicom
from pydicom.datadict import (
    dictionary_description,
    dictionary_VR,
    keyword_for_tag,
    tag_for_keyword,
)
from pydicom.tag import BaseTag, Tag

from ddpt.models import DicomTagRecord, TagDumpReport, TagEditAction, TagEditAudit
from ddpt.utils import ensure_parent, value_to_text


def dump_tags(input_path: Path, include_pixel_data: bool = False) -> TagDumpReport:
    dataset = pydicom.dcmread(input_path, stop_before_pixels=not include_pixel_data)
    records: list[DicomTagRecord] = []
    for element in dataset.iterall():
        if element.keyword == "PixelData" and not include_pixel_data:
            continue
        records.append(
            DicomTagRecord(
                tag=str(element.tag),
                keyword=element.keyword or "",
                name=element.name,
                vr=element.VR,
                value=value_to_text(element.value),
            )
        )
    return TagDumpReport(file_path=str(input_path), tags=records)


def set_tag_value(
    input_path: Path,
    output_path: Path,
    tag_identifier: str,
    value: str,
    vr: str | None = None,
) -> TagEditAudit:
    dataset = pydicom.dcmread(input_path)
    tag = parse_tag_identifier(tag_identifier)
    resolved_vr = _resolve_vr(dataset, tag, vr)
    before, existed_before = _current_value(dataset, tag)
    dataset.add_new(tag, resolved_vr, value)
    action = _action(dataset, tag, "set", existed_before, before)
    _save_dataset(dataset, output_path)
    return TagEditAudit(input_path=str(input_path), output_path=str(output_path), actions=[action])


def blank_tag_value(input_path: Path, output_path: Path, tag_identifier: str) -> TagEditAudit:
    dataset = pydicom.dcmread(input_path)
    tag = parse_tag_identifier(tag_identifier)
    before, existed_before = _current_value(dataset, tag)
    if tag in dataset:
        dataset[tag].value = ""
    action = _action(dataset, tag, "blank", existed_before, before)
    _save_dataset(dataset, output_path)
    return TagEditAudit(input_path=str(input_path), output_path=str(output_path), actions=[action])


def delete_tag(input_path: Path, output_path: Path, tag_identifier: str) -> TagEditAudit:
    dataset = pydicom.dcmread(input_path)
    tag = parse_tag_identifier(tag_identifier)
    before, existed_before = _current_value(dataset, tag)
    if tag in dataset:
        del dataset[tag]
    action = _action(dataset, tag, "delete", existed_before, before, after="")
    _save_dataset(dataset, output_path)
    return TagEditAudit(input_path=str(input_path), output_path=str(output_path), actions=[action])


def parse_tag_identifier(identifier: str) -> BaseTag:
    tag = tag_for_keyword(identifier)
    if tag is not None:
        return Tag(tag)

    normalized = (
        identifier.strip()
        .removeprefix("(")
        .removesuffix(")")
        .replace(",", "")
        .replace(" ", "")
    )
    if normalized.lower().startswith("0x"):
        normalized = normalized[2:]
    if len(normalized) != 8:
        raise ValueError(f"Unsupported DICOM tag identifier: {identifier}")
    try:
        return Tag(int(normalized, 16))
    except ValueError as exc:
        raise ValueError(f"Unsupported DICOM tag identifier: {identifier}") from exc


def _resolve_vr(dataset, tag: BaseTag, vr: str | None) -> str:
    if vr:
        return vr.upper()
    if tag in dataset:
        return dataset[tag].VR
    dictionary_vr = dictionary_VR(tag)
    if dictionary_vr:
        return dictionary_vr
    raise ValueError("VR is required when adding an unknown DICOM tag")


def _current_value(dataset, tag: BaseTag) -> tuple[str, bool]:
    if tag not in dataset:
        return "", False
    return value_to_text(dataset[tag].value), True


def _action(
    dataset,
    tag: BaseTag,
    action: str,
    existed_before: bool,
    before: str,
    after: str | None = None,
) -> TagEditAction:
    element = dataset.get(tag)
    keyword = keyword_for_tag(tag) or (element.keyword if element is not None else "")
    name = _tag_name(tag, element)
    vr = element.VR if element is not None else _safe_dictionary_vr(tag)
    if after is None:
        after = value_to_text(element.value) if element is not None else ""
    return TagEditAction(
        tag=str(tag),
        keyword=keyword,
        name=name,
        vr=vr,
        action=action,
        existed_before=existed_before,
        before=before,
        after=after,
    )


def _tag_name(tag: BaseTag, element) -> str:
    if element is not None:
        return element.name
    try:
        return dictionary_description(tag)
    except KeyError:
        return "Unknown"


def _safe_dictionary_vr(tag: BaseTag) -> str:
    try:
        return dictionary_VR(tag)
    except KeyError:
        return ""


def _save_dataset(dataset, output_path: Path) -> None:
    ensure_parent(output_path)
    dataset.save_as(output_path, enforce_file_format=True)
