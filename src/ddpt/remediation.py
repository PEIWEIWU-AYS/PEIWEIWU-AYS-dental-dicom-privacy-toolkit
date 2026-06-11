from __future__ import annotations

from pathlib import Path

import pydicom
from pydicom.dataelem import DataElement
from pydicom.dataset import FileDataset

from ddpt.batch import find_dicom_files
from ddpt.models import (
    PrivacyRemediationFilePlan,
    PrivacyRemediationItem,
    PrivacyRemediationPlanReport,
)
from ddpt.policy import classify_element, profile_action_for_keyword
from ddpt.profiles import describe_profile
from ddpt.utils import value_to_text


def build_privacy_remediation_plan(
    input_path: Path,
    profile: str = "dental-basic",
    recursive: bool = True,
) -> PrivacyRemediationPlanReport:
    input_path = input_path.resolve()
    profile_summary = describe_profile(profile)
    file_paths = _input_files(input_path, recursive=recursive)
    file_plans = [
        _file_plan(path, input_path, profile_summary) for path in file_paths
    ]
    readable = [plan for plan in file_plans if plan.readable]
    total_items = sum(len(plan.items) for plan in readable)
    covered_items = sum(
        1 for plan in readable for item in plan.items if item.covered_by_profile
    )
    uncovered_high = sum(plan.uncovered_high_risk_items for plan in readable)
    uncovered_medium = sum(plan.uncovered_medium_risk_items for plan in readable)
    private_tags = sum(plan.private_tags_present for plan in readable)
    pixel_review_files = sum(1 for plan in readable if plan.pixel_review_recommended)
    unreadable = len(file_plans) - len(readable)
    passed = unreadable == 0 and uncovered_high == 0 and uncovered_medium == 0
    return PrivacyRemediationPlanReport(
        input_path=str(input_path),
        profile=str(profile_summary.get("name", profile)),
        recursive=recursive,
        passed=passed,
        total_files=len(file_plans),
        readable_files=len(readable),
        unreadable_files=unreadable,
        total_items=total_items,
        covered_items=covered_items,
        uncovered_items=total_items - covered_items,
        uncovered_high_risk_items=uncovered_high,
        uncovered_medium_risk_items=uncovered_medium,
        private_tags_present=private_tags,
        pixel_review_recommended_files=pixel_review_files,
        files=file_plans,
        next_steps=_next_steps(
            unreadable,
            uncovered_high,
            uncovered_medium,
            private_tags,
            pixel_review_files,
        ),
    )


def _input_files(input_path: Path, recursive: bool) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return find_dicom_files(input_path, recursive=recursive)
    return [input_path]


def _file_plan(
    path: Path,
    input_root: Path,
    profile_summary: dict,
) -> PrivacyRemediationFilePlan:
    try:
        dataset = pydicom.dcmread(path, stop_before_pixels=True)
    except Exception as exc:
        return PrivacyRemediationFilePlan(
            path=_relative_text(path, input_root),
            readable=False,
            error=str(exc),
        )

    items = [_item_for_element(element, profile_summary) for element in dataset.iterall()]
    tracked_items = [item for item in items if item is not None]
    high_items = [item for item in tracked_items if item.risk == "high"]
    medium_items = [item for item in tracked_items if item.risk == "medium"]
    uncovered_high = [item for item in high_items if not item.covered_by_profile]
    uncovered_medium = [item for item in medium_items if not item.covered_by_profile]
    burned_in = value_to_text(dataset.get("BurnedInAnnotation", "")) or None
    pixel_review = _pixel_review_recommended(dataset, burned_in)
    return PrivacyRemediationFilePlan(
        path=_relative_text(path, input_root),
        readable=True,
        modality=value_to_text(dataset.get("Modality", "")) or None,
        high_risk_items=len(high_items),
        medium_risk_items=len(medium_items),
        uncovered_high_risk_items=len(uncovered_high),
        uncovered_medium_risk_items=len(uncovered_medium),
        private_tags_present=sum(1 for item in tracked_items if item.category == "private-tag"),
        burned_in_annotation=burned_in,
        pixel_review_recommended=pixel_review,
        items=tracked_items,
    )


def _item_for_element(
    element: DataElement,
    profile_summary: dict,
) -> PrivacyRemediationItem | None:
    if element.keyword == "PixelData":
        return None
    risk, reason, category, recommended_action, dicom_action_code = classify_element(element)
    if risk not in {"high", "medium"}:
        return None
    keyword = element.keyword or str(element.tag)
    profile_action = _profile_action(element, profile_summary)
    covered = _action_covers(
        category=category,
        recommended_action=recommended_action,
        profile_action=profile_action,
    )
    return PrivacyRemediationItem(
        tag=str(element.tag),
        keyword=keyword,
        risk=risk,
        category=category,
        current_value=value_to_text(element.value),
        recommended_action=recommended_action,
        profile_action=profile_action,
        covered_by_profile=covered,
        dicom_action_code=dicom_action_code,
        note=reason if covered else f"{reason}; profile action is {profile_action}.",
    )


def _profile_action(element: DataElement, profile_summary: dict) -> str:
    if element.tag.is_private:
        return "remove_private_tag" if profile_summary["remove_private_tags"] else "unhandled"
    return profile_action_for_keyword(profile_summary, element.keyword or "")


def _action_covers(category: str, recommended_action: str, profile_action: str) -> bool:
    if profile_action == recommended_action:
        return True
    if recommended_action == "replace" and profile_action == "pseudonymize":
        return True
    if category == "date" and recommended_action == "blank" and profile_action == "date_shift":
        return True
    return recommended_action == "remove_private_tag" and profile_action == "remove_private_tag"


def _pixel_review_recommended(dataset: FileDataset, burned_in: str | None) -> bool:
    has_pixels = dataset.get("Rows") is not None and dataset.get("Columns") is not None
    if not has_pixels:
        return False
    if burned_in is None:
        return True
    return burned_in.upper() != "NO"


def _next_steps(
    unreadable: int,
    uncovered_high: int,
    uncovered_medium: int,
    private_tags: int,
    pixel_review_files: int,
) -> list[str]:
    steps = []
    if unreadable:
        steps.append("Review unreadable files before batch anonymization.")
    if uncovered_high or uncovered_medium:
        steps.append("Adjust the anonymization profile or choose a stronger built-in profile.")
    if private_tags:
        steps.append("Keep remove_private_tags enabled before sharing.")
    if pixel_review_files:
        steps.append("Run pixel review for files with possible burned-in identifiers.")
    if not steps:
        steps.append(
            "Run anonymization, validation, de-identification comparison, and quality gate."
        )
    return steps


def _relative_text(path: Path, input_root: Path) -> str:
    root = input_root if input_root.is_dir() else input_root.parent
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
