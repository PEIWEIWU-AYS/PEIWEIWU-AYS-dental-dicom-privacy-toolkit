from __future__ import annotations

from pydicom.dataelem import DataElement

from ddpt.models import RiskLevel
from ddpt.policy import classify_element as classify_element_with_policy
from ddpt.policy import policies_by_risk

HIGH_RISK_KEYWORDS = {policy.keyword for policy in policies_by_risk("high")}
MEDIUM_RISK_KEYWORDS = {policy.keyword for policy in policies_by_risk("medium")}
LOW_RISK_KEYWORDS = {policy.keyword for policy in policies_by_risk("low")}


def classify_element(element: DataElement) -> tuple[RiskLevel, str]:
    risk, reason, _category, _recommended_action, _dicom_action_code = (
        classify_element_with_policy(element)
    )
    return risk, reason
