from __future__ import annotations

from ddpt.models import (
    ConfidentialityActionCode,
    ConfidentialityAlignmentItem,
    ConfidentialityAlignmentReport,
    ConfidentialityOptionItem,
    TagPolicy,
)
from ddpt.policy import TAG_POLICIES, profile_action_for_keyword
from ddpt.profiles import describe_profile

CONFIDENTIALITY_SOURCE = (
    "DICOM PS3.15 Attribute Confidentiality Profiles-inspired dental alignment"
)

ACTION_CODES = [
    ConfidentialityActionCode(
        code="D",
        meaning="replace with a non-zero length dummy value",
        toolkit_interpretation="replace or deterministic pseudonymize",
    ),
    ConfidentialityActionCode(
        code="Z",
        meaning="replace with a zero-length value, or a dummy value where required",
        toolkit_interpretation=(
            "blank, or date_shift when a research profile intentionally retains intervals"
        ),
    ),
    ConfidentialityActionCode(
        code="X",
        meaning="remove the attribute",
        toolkit_interpretation=(
            "blank/remove value in toolkit reports; remove private tags for private elements"
        ),
    ),
    ConfidentialityActionCode(
        code="K",
        meaning="keep the attribute",
        toolkit_interpretation=(
            "retain low-risk technical metadata needed for readable synthetic DICOM"
        ),
    ),
    ConfidentialityActionCode(
        code="C",
        meaning="clean descriptors or free text",
        toolkit_interpretation="replace or blank text fields that may contain identifiers",
    ),
    ConfidentialityActionCode(
        code="U",
        meaning="replace UID with a new UID",
        toolkit_interpretation="regenerate UID fields listed by the selected profile",
    ),
]

BOUNDARY_NOTES = [
    "This is a standards-alignment report, not DICOM conformance certification.",
    "The toolkit uses synthetic or explicitly approved test DICOM files for public evidence.",
    (
        "Pixel cleaning evidence is manual/known-region based; it is not OCR "
        "and not full burned-in PHI detection."
    ),
    (
        "Encrypted sharing packages are project artifacts and do not implement "
        "DICOM Encrypted Attributes Sequence."
    ),
]


def build_confidentiality_alignment(
    profile_name_or_path: str = "dental-basic",
) -> ConfidentialityAlignmentReport:
    summary = describe_profile(profile_name_or_path)
    items = [_item_for_policy(policy, summary) for policy in TAG_POLICIES.values()]
    high_medium_unaligned = sum(
        1 for item in items if item.risk in {"high", "medium"} and not item.aligned
    )
    aligned = sum(1 for item in items if item.aligned)
    return ConfidentialityAlignmentReport(
        profile=str(summary["name"]),
        source=CONFIDENTIALITY_SOURCE,
        passed=high_medium_unaligned == 0,
        total_policy_items=len(items),
        aligned_items=aligned,
        unaligned_items=len(items) - aligned,
        high_medium_unaligned=high_medium_unaligned,
        remove_private_tags=bool(summary["remove_private_tags"]),
        date_shift_offset_days=int(summary["date_shift_offset_days"]),
        action_codes=ACTION_CODES,
        options=_options(summary, items),
        items=items,
        boundary_notes=BOUNDARY_NOTES,
    )


def _item_for_policy(
    policy: TagPolicy,
    profile_summary: dict,
) -> ConfidentialityAlignmentItem:
    profile_action = _effective_profile_action(policy, profile_summary)
    aligned = _aligned(policy, profile_action)
    return ConfidentialityAlignmentItem(
        keyword=policy.keyword,
        risk=policy.risk,
        category=policy.category,
        dicom_action_code=policy.dicom_action_code,
        recommended_action=policy.recommended_action,
        profile_action=profile_action,
        aligned=aligned,
        note=_note(policy, profile_action, aligned),
    )


def _effective_profile_action(policy: TagPolicy, profile_summary: dict) -> str:
    action = profile_action_for_keyword(profile_summary, policy.keyword)
    if action == "unhandled" and policy.recommended_action == "retain":
        return "retain"
    return action


def _aligned(policy: TagPolicy, profile_action: str) -> bool:
    if profile_action == policy.recommended_action:
        return True
    if policy.recommended_action == "replace" and profile_action == "pseudonymize":
        return True
    if policy.category == "date" and policy.recommended_action == "blank":
        return profile_action in {"blank", "date_shift"}
    if policy.recommended_action == "retain" and profile_action == "retain":
        return True
    return False


def _note(policy: TagPolicy, profile_action: str, aligned: bool) -> str:
    if aligned and profile_action == "date_shift":
        return "Aligned through modified-date research option; review re-identification risk."
    if aligned and profile_action == "pseudonymize":
        return "Aligned through deterministic pseudonymization instead of a fixed dummy value."
    if aligned:
        return "Profile action matches the recommended DICOM-inspired action."
    return (
        f"Recommended {policy.recommended_action} for {policy.reason}; "
        f"profile action is {profile_action}."
    )


def _options(
    profile_summary: dict,
    items: list[ConfidentialityAlignmentItem],
) -> list[ConfidentialityOptionItem]:
    high_medium_unaligned = [
        item for item in items if item.risk in {"high", "medium"} and not item.aligned
    ]
    date_shift_keywords = list(profile_summary["date_shift_keywords"])
    free_text_items = [
        item for item in items if item.category == "free-text" and item.aligned
    ]
    uid_items = [
        item for item in items if item.category == "uid" and item.profile_action == "regenerate_uid"
    ]
    return [
        ConfidentialityOptionItem(
            id="basic-application-level-confidentiality",
            name="Basic Application Level Confidentiality Profile baseline",
            status="supported" if not high_medium_unaligned else "partially-supported",
            evidence=[
                f"high_medium_unaligned={len(high_medium_unaligned)}",
                f"aligned={sum(1 for item in items if item.aligned)}/{len(items)}",
            ],
            note=(
                "High and medium risk registry items are covered by the selected profile."
                if not high_medium_unaligned
                else "Some high or medium risk registry items are not covered."
            ),
        ),
        ConfidentialityOptionItem(
            id="clean-descriptors",
            name="Clean Descriptors / free-text cleaning",
            status="supported" if len(free_text_items) >= 3 else "partially-supported",
            evidence=[item.keyword for item in free_text_items],
            note="Free-text dental descriptors are replaced or blanked by profile rules.",
        ),
        ConfidentialityOptionItem(
            id="clean-pixel-data",
            name="Clean Pixel Data option evidence",
            status="partially-supported",
            evidence=[
                "src/ddpt/pixel_risk.py",
                "src/ddpt/pixel_review.py",
                "src/ddpt/pixels.py",
                "docs/pixel-review.md",
            ],
            note=(
                "The toolkit supports pixel risk triage, known-region review, and "
                "manual redaction evidence, but not automatic OCR-based detection."
            ),
        ),
        ConfidentialityOptionItem(
            id="modified-dates",
            name="Retain Longitudinal Temporal Information With Modified Dates",
            status="supported" if date_shift_keywords else "not-selected",
            evidence=date_shift_keywords,
            note=(
                f"Date fields are shifted by {profile_summary['date_shift_offset_days']} days."
                if date_shift_keywords
                else "The selected profile blanks date fields instead of retaining modified dates."
            ),
        ),
        ConfidentialityOptionItem(
            id="regenerate-uids",
            name="UID replacement",
            status="supported" if uid_items else "not-selected",
            evidence=[item.keyword for item in uid_items],
            note="UID fields are regenerated rather than retained.",
        ),
        ConfidentialityOptionItem(
            id="retain-safe-private",
            name="Retain Safe Private Option",
            status=(
                "not-selected"
                if profile_summary["remove_private_tags"]
                else "partially-supported"
            ),
            evidence=[f"remove_private_tags={profile_summary['remove_private_tags']}"],
            note=(
                "Private tags are removed by default for a conservative public demo boundary."
                if profile_summary["remove_private_tags"]
                else "Profile retains private tags; review vendor-specific risk carefully."
            ),
        ),
        ConfidentialityOptionItem(
            id="encrypted-attributes-sequence",
            name="DICOM Encrypted Attributes Sequence",
            status="not-supported",
            evidence=["docs/package-verification-receipts.md", "src/ddpt/sharing.py"],
            note=(
                "The project demonstrates external encrypted packages with receipts, "
                "not in-DICOM Encrypted Attributes Sequence handling."
            ),
        ),
    ]
