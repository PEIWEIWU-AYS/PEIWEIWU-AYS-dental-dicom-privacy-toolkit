from __future__ import annotations

import json
import shlex
from pathlib import Path
from urllib.parse import quote, urljoin

from ddpt.anonymize import plan_anonymization_actions
from ddpt.models import OrthancAnonymizePlanReport, OrthancPlanItem
from ddpt.profiles import load_profile

BOUNDARY_NOTES = [
    "Review-only Orthanc REST anonymization plan; the toolkit does not contact Orthanc.",
    (
        "Payload shape follows Orthanc's documented anonymization controls: "
        "Replace, Remove, KeepPrivateTags, DicomVersion, and Force."
    ),
    (
        "UID regeneration is represented as StandardAnonymizer evidence because "
        "Orthanc controls server-side UID handling."
    ),
    (
        "Verify payload behavior against the target Orthanc server version before "
        "using it with non-synthetic data."
    ),
]


def build_orthanc_anonymize_plan(
    input_path: Path,
    profile: str = "dental-basic",
    resource_id: str = "<orthanc-resource-id>",
    orthanc_base_url: str = "http://localhost:8042",
    dicom_version: str = "2023b",
    force: bool = True,
) -> OrthancAnonymizePlanReport:
    audit = plan_anonymization_actions(input_path, profile)
    profile_data = load_profile(profile)
    keep_private_tags = not bool(profile_data.get("remove_private_tags", True))
    replace: dict[str, str] = {}
    remove: list[str] = []
    items: list[OrthancPlanItem] = []

    for order, action in enumerate(audit.actions, start=1):
        item = _item_from_action(order, action)
        items.append(item)
        if item.orthanc_section == "Replace":
            replace[item.orthanc_key] = item.orthanc_value
        elif item.orthanc_section == "Remove":
            remove.append(item.orthanc_key)

    if audit.private_tags_removed:
        items.append(
            OrthancPlanItem(
                order=len(items) + 1,
                keyword="PrivateTags",
                tag="private",
                profile_action="remove_private_tags",
                orthanc_section="KeepPrivateTags",
                orthanc_key="KeepPrivateTags",
                orthanc_value="false",
                note=(
                    "Orthanc KeepPrivateTags=false requests private-tag removal "
                    "during server-side anonymization."
                ),
            )
        )

    endpoint_path = f"/instances/{quote(resource_id, safe='')}/anonymize"
    endpoint_url = urljoin(_base_url(orthanc_base_url), endpoint_path.lstrip("/"))
    payload: dict[str, object] = {
        "DicomVersion": dicom_version,
        "Force": force,
        "KeepPrivateTags": keep_private_tags,
    }
    if replace:
        payload["Replace"] = replace
    if remove:
        payload["Remove"] = sorted(set(remove))

    curl_commands = [
        shlex.join(
            [
                "curl",
                "-sS",
                "-X",
                "POST",
                endpoint_url,
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(payload, sort_keys=True),
            ]
        )
    ]
    return OrthancAnonymizePlanReport(
        input_path=str(input_path.resolve()),
        profile=audit.profile,
        orthanc_base_url=orthanc_base_url,
        resource_id=resource_id,
        endpoint_path=endpoint_path,
        endpoint_url=endpoint_url,
        dicom_version=dicom_version,
        force=force,
        keep_private_tags=keep_private_tags,
        payload=payload,
        total_operations=len(items),
        replace_operations=sum(1 for item in items if item.orthanc_section == "Replace"),
        remove_operations=sum(1 for item in items if item.orthanc_section == "Remove"),
        standard_anonymizer_operations=sum(
            1 for item in items if item.orthanc_section == "StandardAnonymizer"
        ),
        review_only_operations=sum(
            1 for item in items if item.orthanc_section == "ReviewOnly"
        ),
        curl_commands=curl_commands,
        items=items,
        boundary_notes=BOUNDARY_NOTES,
    )


def _item_from_action(order: int, action) -> OrthancPlanItem:
    if action.action in {"replace", "blank", "pseudonymize", "date_shift"}:
        return OrthancPlanItem(
            order=order,
            keyword=action.keyword,
            tag=action.tag,
            profile_action=action.action,
            orthanc_section="Replace",
            orthanc_key=action.keyword,
            orthanc_value=action.after,
            note=(
                "Profile action is represented as an Orthanc Replace entry. "
                "Blank actions use an empty string value."
            ),
        )
    if action.action == "regenerate_uid":
        return OrthancPlanItem(
            order=order,
            keyword=action.keyword,
            tag=action.tag,
            profile_action=action.action,
            orthanc_section="StandardAnonymizer",
            orthanc_key=action.keyword,
            orthanc_value="<server-generated>",
            note=(
                "Orthanc's server-side anonymizer controls UID replacement; "
                "review the output UID policy on the target server."
            ),
        )
    return OrthancPlanItem(
        order=order,
        keyword=action.keyword,
        tag=action.tag,
        profile_action=action.action,
        orthanc_section="ReviewOnly",
        orthanc_key=action.keyword,
        orthanc_value=action.after,
        note="This profile action is included for review and is not mapped into the payload.",
    )


def _base_url(value: str) -> str:
    return value.rstrip("/") + "/"
