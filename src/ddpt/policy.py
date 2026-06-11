from __future__ import annotations

from pydicom.dataelem import DataElement

from ddpt.models import ProfileCoverageItem, ProfileCoverageReport, RiskLevel, TagPolicy
from ddpt.profiles import describe_profile

POLICY_SOURCE = "DICOM PS3.15-inspired dental privacy baseline"

_POLICIES = [
    ("PatientName", "high", "direct-identifier", "replace", "D", "direct patient name"),
    ("PatientID", "high", "direct-identifier", "replace", "D", "direct patient identifier"),
    ("PatientBirthDate", "high", "date", "blank", "Z", "direct patient birth date"),
    ("PatientAddress", "high", "direct-identifier", "blank", "X/Z", "direct contact detail"),
    ("PatientTelephoneNumbers", "high", "direct-identifier", "blank", "X", "direct contact detail"),
    ("OtherPatientIDs", "high", "direct-identifier", "blank", "X", "alternate patient ID"),
    ("OtherPatientNames", "high", "direct-identifier", "blank", "X", "alternate patient name"),
    ("PatientMotherBirthName", "high", "direct-identifier", "blank", "X", "family identifier"),
    ("AccessionNumber", "medium", "workflow-identifier", "replace", "Z/D", "workflow identifier"),
    ("InstitutionName", "medium", "organization", "replace", "D", "institution detail"),
    ("InstitutionAddress", "medium", "organization", "blank", "X", "institution location"),
    ("ReferringPhysicianName", "medium", "person", "blank", "X", "clinician name"),
    ("RequestingPhysician", "medium", "person", "blank", "X", "clinician name"),
    ("OperatorsName", "medium", "person", "blank", "X", "operator name"),
    ("PhysiciansOfRecord", "medium", "person", "blank", "X", "clinician name"),
    ("PerformingPhysicianName", "medium", "person", "blank", "X", "clinician name"),
    ("StudyDescription", "medium", "free-text", "replace", "C", "may contain identifying text"),
    ("SeriesDescription", "medium", "free-text", "replace", "C", "may contain identifying text"),
    ("ProtocolName", "medium", "free-text", "blank", "C", "may contain identifying text"),
    ("DeviceSerialNumber", "medium", "device", "blank", "X", "device identifier"),
    ("StationName", "medium", "device", "blank", "X", "workstation identifier"),
    ("StudyDate", "medium", "date", "blank", "Z", "study date can aid re-identification"),
    ("SeriesDate", "medium", "date", "blank", "Z", "series date can aid re-identification"),
    (
        "AcquisitionDate",
        "medium",
        "date",
        "blank",
        "Z",
        "acquisition date can aid re-identification",
    ),
    ("ContentDate", "medium", "date", "blank", "Z", "content date can aid re-identification"),
    ("StudyTime", "medium", "time", "blank", "Z", "study time can aid re-identification"),
    ("SeriesTime", "medium", "time", "blank", "Z", "series time can aid re-identification"),
    (
        "AcquisitionTime",
        "medium",
        "time",
        "blank",
        "Z",
        "acquisition time can aid re-identification",
    ),
    ("ContentTime", "medium", "time", "blank", "Z", "content time can aid re-identification"),
    ("FrameOfReferenceUID", "medium", "uid", "regenerate_uid", "U", "UID can link datasets"),
    ("SOPInstanceUID", "medium", "uid", "regenerate_uid", "U", "UID can link datasets"),
    ("SeriesInstanceUID", "medium", "uid", "regenerate_uid", "U", "UID can link datasets"),
    ("StudyInstanceUID", "medium", "uid", "regenerate_uid", "U", "UID can link datasets"),
    ("Modality", "low", "technical", "retain", "K", "technical metadata"),
    ("Rows", "low", "technical", "retain", "K", "technical metadata"),
    ("Columns", "low", "technical", "retain", "K", "technical metadata"),
    ("BitsAllocated", "low", "technical", "retain", "K", "technical metadata"),
    ("BitsStored", "low", "technical", "retain", "K", "technical metadata"),
    ("HighBit", "low", "technical", "retain", "K", "technical metadata"),
    ("PixelRepresentation", "low", "technical", "retain", "K", "technical metadata"),
    ("SamplesPerPixel", "low", "technical", "retain", "K", "technical metadata"),
    ("PhotometricInterpretation", "low", "technical", "retain", "K", "technical metadata"),
    ("SOPClassUID", "low", "technical", "retain", "K", "technical metadata"),
    ("TransferSyntaxUID", "low", "technical", "retain", "K", "technical metadata"),
]

TAG_POLICIES = {
    keyword: TagPolicy(
        keyword=keyword,
        risk=risk,
        category=category,
        recommended_action=action,
        dicom_action_code=dicom_action,
        reason=reason,
        source=POLICY_SOURCE,
    )
    for keyword, risk, category, action, dicom_action, reason in _POLICIES
}


def policy_for_keyword(keyword: str) -> TagPolicy | None:
    return TAG_POLICIES.get(keyword)


def policies_by_risk(*risks: RiskLevel) -> list[TagPolicy]:
    risk_set = set(risks)
    return [policy for policy in TAG_POLICIES.values() if policy.risk in risk_set]


def classify_element(element: DataElement) -> tuple[RiskLevel, str, str, str, str]:
    keyword = element.keyword or ""
    policy = policy_for_keyword(keyword)
    if policy:
        return (
            policy.risk,
            policy.reason,
            policy.category,
            policy.recommended_action,
            policy.dicom_action_code,
        )
    if element.tag.is_private:
        return (
            "medium",
            "private tag may contain vendor-specific identifying information",
            "private-tag",
            "remove_private_tag",
            "X",
        )
    return (
        "unknown",
        "not classified by the initial dental privacy profile",
        "unknown",
        "review",
        "?",
    )


def profile_action_for_keyword(profile_summary: dict, keyword: str) -> str:
    if keyword in profile_summary["replace_keywords"]:
        return "replace"
    if keyword in profile_summary["blank_keywords"]:
        return "blank"
    if keyword in profile_summary["date_shift_keywords"]:
        return "date_shift"
    if keyword in profile_summary["regenerate_uid_keywords"]:
        return "regenerate_uid"
    return "unhandled"


def profile_coverage(profile_name_or_path: str) -> ProfileCoverageReport:
    summary = describe_profile(profile_name_or_path)
    items: list[ProfileCoverageItem] = []
    for policy in policies_by_risk("high", "medium"):
        profile_action = profile_action_for_keyword(summary, policy.keyword)
        covered = profile_action == policy.recommended_action or (
            policy.category == "date"
            and policy.recommended_action == "blank"
            and profile_action == "date_shift"
        )
        items.append(
            ProfileCoverageItem(
                keyword=policy.keyword,
                risk=policy.risk,
                category=policy.category,
                recommended_action=policy.recommended_action,
                profile_action=profile_action,
                covered=covered,
                reason=policy.reason,
            )
        )

    high_risk_uncovered = [
        item.keyword for item in items if item.risk == "high" and not item.covered
    ]
    medium_risk_uncovered = [
        item.keyword for item in items if item.risk == "medium" and not item.covered
    ]
    covered_count = sum(1 for item in items if item.covered)
    return ProfileCoverageReport(
        profile=str(summary["name"]),
        total_items=len(items),
        covered_items=covered_count,
        high_risk_uncovered=high_risk_uncovered,
        medium_risk_uncovered=medium_risk_uncovered,
        items=items,
    )
