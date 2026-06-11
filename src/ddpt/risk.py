from __future__ import annotations

from pydicom.dataelem import DataElement

from ddpt.models import RiskLevel

HIGH_RISK_KEYWORDS = {
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "PatientMotherBirthName",
}

MEDIUM_RISK_KEYWORDS = {
    "AccessionNumber",
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "RequestingPhysician",
    "OperatorsName",
    "PhysiciansOfRecord",
    "PerformingPhysicianName",
    "StudyDescription",
    "SeriesDescription",
    "ProtocolName",
    "DeviceSerialNumber",
    "StationName",
    "StudyDate",
    "SeriesDate",
    "AcquisitionDate",
    "ContentDate",
    "StudyTime",
    "SeriesTime",
    "AcquisitionTime",
    "ContentTime",
    "FrameOfReferenceUID",
    "SOPInstanceUID",
    "SeriesInstanceUID",
    "StudyInstanceUID",
}

LOW_RISK_KEYWORDS = {
    "Modality",
    "Rows",
    "Columns",
    "BitsAllocated",
    "BitsStored",
    "HighBit",
    "PixelRepresentation",
    "SamplesPerPixel",
    "PhotometricInterpretation",
    "SOPClassUID",
    "TransferSyntaxUID",
}


def classify_element(element: DataElement) -> tuple[RiskLevel, str]:
    keyword = element.keyword or ""
    if keyword in HIGH_RISK_KEYWORDS:
        return "high", "direct patient identifier or direct contact detail"
    if keyword in MEDIUM_RISK_KEYWORDS:
        return "medium", "contextual identifier, institution detail, device detail, or date/time"
    if keyword in LOW_RISK_KEYWORDS:
        return "low", "technical metadata usually needed for file interpretation"
    if element.tag.is_private:
        return "medium", "private tag may contain vendor-specific identifying information"
    return "unknown", "not classified by the initial dental privacy profile"
