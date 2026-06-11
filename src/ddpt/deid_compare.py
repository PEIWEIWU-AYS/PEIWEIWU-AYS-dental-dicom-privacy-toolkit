from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pydicom

from ddpt.models import (
    DeidentificationComparisonItem,
    DeidentificationComparisonReport,
    TagPolicy,
)
from ddpt.policy import policies_by_risk
from ddpt.utils import value_to_text


def compare_deidentification(
    source_path: Path,
    anonymized_path: Path,
) -> DeidentificationComparisonReport:
    source = pydicom.dcmread(source_path)
    anonymized = pydicom.dcmread(anonymized_path)
    policies = policies_by_risk("high", "medium")
    items = [_compare_policy_item(source, anonymized, policy) for policy in policies]

    residual_high = [
        item.keyword for item in items if item.risk == "high" and not item.passed
    ]
    residual_medium = [
        item.keyword for item in items if item.risk == "medium" and not item.passed
    ]
    private_before = _private_tag_count(source)
    private_after = _private_tag_count(anonymized)
    before_pixel_hash = _pixel_data_hash(source)
    after_pixel_hash = _pixel_data_hash(anonymized)
    pixel_changed = None
    if before_pixel_hash and after_pixel_hash:
        pixel_changed = before_pixel_hash != after_pixel_hash
    passed = all(item.passed for item in items) and private_after == 0
    return DeidentificationComparisonReport(
        source_path=str(source_path),
        anonymized_path=str(anonymized_path),
        passed=passed,
        total_items=len(items),
        passed_items=sum(1 for item in items if item.passed),
        failed_items=sum(1 for item in items if not item.passed),
        changed_items=sum(1 for item in items if item.status == "changed"),
        removed_items=sum(1 for item in items if item.status == "removed"),
        unchanged_items=sum(1 for item in items if item.status == "unchanged"),
        residual_high_risk_keywords=residual_high,
        residual_medium_risk_keywords=residual_medium,
        private_tags_before=private_before,
        private_tags_after=private_after,
        private_tags_removed=private_after == 0,
        pixel_data_before_sha256=before_pixel_hash,
        pixel_data_after_sha256=after_pixel_hash,
        pixel_data_changed=pixel_changed,
        items=items,
    )


def _compare_policy_item(
    source: Any,
    anonymized: Any,
    policy: TagPolicy,
) -> DeidentificationComparisonItem:
    before_present = policy.keyword in source
    after_present = policy.keyword in anonymized
    before = _dataset_value(source, policy.keyword)
    after = _dataset_value(anonymized, policy.keyword)
    status = _comparison_status(before_present, after_present, before, after)
    passed, note = _policy_item_passed(policy, before_present, before, after_present, after)
    return DeidentificationComparisonItem(
        keyword=policy.keyword,
        risk=policy.risk,
        category=policy.category,
        recommended_action=policy.recommended_action,
        status=status,
        passed=passed,
        before=before,
        after=after,
        note=note,
    )


def _dataset_value(dataset: Any, keyword: str) -> str:
    if keyword in dataset:
        return value_to_text(dataset.get(keyword, ""))
    if getattr(dataset, "file_meta", None) and keyword in dataset.file_meta:
        return value_to_text(dataset.file_meta.get(keyword, ""))
    return ""


def _comparison_status(
    before_present: bool,
    after_present: bool,
    before: str,
    after: str,
) -> str:
    if not before_present and not after_present:
        return "absent"
    if before_present and not after_present:
        return "removed"
    if not before_present and after_present:
        return "added"
    if before == after:
        return "unchanged"
    if after == "":
        return "removed"
    return "changed"


def _policy_item_passed(
    policy: TagPolicy,
    before_present: bool,
    before: str,
    after_present: bool,
    after: str,
) -> tuple[bool, str]:
    if not before_present and not after_present:
        return True, "not present in either file"
    if not before_present and after_present and policy.risk in {"high", "medium"}:
        return False, "sensitive policy item was added to the anonymized file"
    if policy.recommended_action == "replace":
        if before and after and before != after:
            return True, "value was replaced"
        if not before and not after:
            return True, "empty before and after"
        return False, "value was not replaced"
    if policy.recommended_action == "blank":
        if not after_present or after == "":
            return True, "value was blanked or removed"
        if policy.category == "date" and before and after != before:
            return True, "date was shifted rather than exposed unchanged"
        return False, "value remains present"
    if policy.recommended_action == "regenerate_uid":
        if before and after and before != after:
            return True, "UID was regenerated"
        return False, "UID was not regenerated"
    if policy.recommended_action == "retain":
        return True, "technical metadata may be retained"
    if before and after != before:
        return True, "value changed"
    return False, "value remained unchanged"


def _private_tag_count(dataset: Any) -> int:
    return sum(1 for element in dataset.iterall() if element.tag.is_private)


def _pixel_data_hash(dataset: Any) -> str | None:
    if "PixelData" not in dataset:
        return None
    return hashlib.sha256(bytes(dataset.PixelData)).hexdigest()
