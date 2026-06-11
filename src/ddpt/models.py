from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["high", "medium", "low", "unknown"]


class TagFinding(BaseModel):
    tag: str
    keyword: str
    name: str
    vr: str
    value: str
    risk: RiskLevel
    category: str = "unknown"
    recommended_action: str = "review"
    dicom_action_code: str = "?"
    reason: str


class InspectionReport(BaseModel):
    file_path: str
    sop_class_uid: str | None = None
    modality: str | None = None
    patient_id_present: bool = False
    patient_name_present: bool = False
    findings: list[TagFinding] = Field(default_factory=list)
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def high_risk_count(self) -> int:
        return sum(1 for item in self.findings if item.risk == "high")

    @property
    def medium_risk_count(self) -> int:
        return sum(1 for item in self.findings if item.risk == "medium")


class AnonymizationAction(BaseModel):
    tag: str
    keyword: str
    action: str
    before: str
    after: str


class AnonymizationAudit(BaseModel):
    input_path: str
    output_path: str
    profile: str
    actions: list[AnonymizationAction] = Field(default_factory=list)
    private_tags_removed: bool = True
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ManifestEntry(BaseModel):
    path: str
    sha256: str
    size_bytes: int


class PackageManifest(BaseModel):
    package_name: str
    encrypted: bool
    entries: list[ManifestEntry]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ValidationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class ValidationReport(BaseModel):
    file_path: str
    passed: bool
    checks: list[ValidationCheck]
    warnings: list[str] = Field(default_factory=list)
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class PixelRectangle(BaseModel):
    x: int
    y: int
    width: int
    height: int


class PixelRedactionAudit(BaseModel):
    input_path: str
    output_path: str
    rectangles: list[PixelRectangle]
    fill_value: int
    note: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DemoPipelineResult(BaseModel):
    output_dir: str
    input_dicom: str
    anonymized_dicom: str
    redacted_dicom: str
    inspection_json: str
    inspection_html: str
    audit_json: str
    audit_html: str
    validation_json: str
    redaction_json: str
    manifest_json: str
    package_path: str
    key_path: str
    summary_html: str
    validation_passed: bool
    package_entries: int
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class BatchFileResult(BaseModel):
    input_path: str
    output_path: str | None = None
    inspection_json: str | None = None
    audit_json: str | None = None
    validation_json: str | None = None
    validation_passed: bool = False
    error: str | None = None


class BatchSummary(BaseModel):
    input_dir: str
    output_dir: str
    profile: str
    total_files: int
    processed_files: int
    failed_files: int
    validation_failures: int
    files: list[BatchFileResult]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class TagPolicy(BaseModel):
    keyword: str
    risk: RiskLevel
    category: str
    recommended_action: str
    dicom_action_code: str
    reason: str
    source: str


class ProfileCoverageItem(BaseModel):
    keyword: str
    risk: RiskLevel
    category: str
    recommended_action: str
    profile_action: str
    covered: bool
    reason: str


class ProfileCoverageReport(BaseModel):
    profile: str
    total_items: int
    covered_items: int
    high_risk_uncovered: list[str]
    medium_risk_uncovered: list[str]
    items: list[ProfileCoverageItem]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
