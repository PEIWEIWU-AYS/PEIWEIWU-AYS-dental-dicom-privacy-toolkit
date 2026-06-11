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


class PackageVerificationReceipt(BaseModel):
    package_path: str
    key_provided: bool
    passed: bool
    package_sha256: str
    package_name: str | None = None
    encrypted: bool | None = None
    entries: list[ManifestEntry] = Field(default_factory=list)
    total_size_bytes: int = 0
    errors: list[str] = Field(default_factory=list)
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


class PixelRedactionPlanRegion(BaseModel):
    label: str
    unit: Literal["pixels", "percent"] = "percent"
    x: float
    y: float
    width: float
    height: float


class PixelRedactionPlan(BaseModel):
    name: str
    description: str
    regions: list[PixelRedactionPlanRegion]


class PixelRedactionAudit(BaseModel):
    input_path: str
    output_path: str
    rectangles: list[PixelRectangle]
    fill_value: int
    note: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class PreviewReport(BaseModel):
    input_path: str
    output_path: str
    rows: int
    columns: int
    rendered_width: int
    rendered_height: int
    min_pixel_value: float
    max_pixel_value: float
    photometric_interpretation: str | None = None
    note: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DoctorCheck(BaseModel):
    name: str
    passed: bool
    message: str


class DoctorReport(BaseModel):
    passed: bool
    python_version: str
    platform: str
    package_version: str
    checks: list[DoctorCheck]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SafetyFinding(BaseModel):
    path: str
    severity: Literal["high", "medium", "low"]
    rule_id: str
    message: str


class SafetyScanReport(BaseModel):
    root_dir: str
    passed: bool
    scanned_files: int
    findings: list[SafetyFinding]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ReleaseAuditCheck(BaseModel):
    id: str
    category: str
    passed: bool
    message: str
    evidence: list[str] = Field(default_factory=list)


class ReleaseAuditReport(BaseModel):
    root_dir: str
    passed: bool
    checks: list[ReleaseAuditCheck]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def passed_checks(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_checks(self) -> int:
        return sum(1 for check in self.checks if not check.passed)


class EvidenceArtifact(BaseModel):
    label: str
    category: str
    path: str
    description: str


class EvidenceBundleResult(BaseModel):
    repository_root: str
    output_dir: str
    passed: bool
    doctor_passed: bool
    safety_passed: bool
    release_audit_passed: bool
    demo_passed: bool
    workflow_passed: bool
    artifacts: list[EvidenceArtifact]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DicomTagRecord(BaseModel):
    tag: str
    keyword: str
    name: str
    vr: str
    value: str


class TagDumpReport(BaseModel):
    file_path: str
    tags: list[DicomTagRecord]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class TagEditAction(BaseModel):
    tag: str
    keyword: str
    name: str
    vr: str
    action: Literal["set", "blank", "delete"]
    existed_before: bool
    before: str
    after: str


class TagEditAudit(BaseModel):
    input_path: str
    output_path: str
    actions: list[TagEditAction]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class WorkflowStepResult(BaseModel):
    id: str
    action: str
    passed: bool
    message: str
    artifacts: list[str] = Field(default_factory=list)


class WorkflowRunReport(BaseModel):
    recipe_path: str
    root_dir: str
    name: str
    passed: bool
    steps: list[WorkflowStepResult]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DemoPipelineResult(BaseModel):
    output_dir: str
    input_dicom: str
    inventory_json: str
    inventory_csv: str
    inventory_html: str
    input_preview_png: str
    anonymized_preview_png: str
    redacted_preview_png: str
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
    package_receipt_json: str
    package_receipt_html: str
    audit_chain_json: str
    audit_chain_verify_json: str
    summary_html: str
    validation_passed: bool
    audit_chain_passed: bool
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


class InventoryFileRecord(BaseModel):
    path: str
    readable: bool
    error: str | None = None
    file_sha256: str | None = None
    modality: str | None = None
    sop_class_uid: str | None = None
    study_instance_uid_hash: str | None = None
    series_instance_uid_hash: str | None = None
    sop_instance_uid_hash: str | None = None
    patient_name_present: bool = False
    patient_id_present: bool = False
    patient_birth_date_present: bool = False
    burned_in_annotation: str | None = None
    rows: int | None = None
    columns: int | None = None
    transfer_syntax_uid: str | None = None
    high_risk_tags: int = 0
    medium_risk_tags: int = 0
    low_risk_tags: int = 0
    unknown_risk_tags: int = 0
    recommended_actions: list[str] = Field(default_factory=list)
    high_risk_keywords: list[str] = Field(default_factory=list)


class InventoryReport(BaseModel):
    root_dir: str
    recursive: bool
    total_files: int
    readable_files: int
    unreadable_files: int
    high_risk_tags: int
    medium_risk_tags: int
    modalities: dict[str, int]
    files: list[InventoryFileRecord]
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


class ProfileComparisonItem(BaseModel):
    keyword: str
    risk: RiskLevel
    category: str
    recommended_action: str
    baseline_action: str
    candidate_action: str
    changed: bool
    note: str


class ProfileComparisonReport(BaseModel):
    baseline_profile: str
    candidate_profile: str
    total_items: int
    changed_items: int
    baseline_covered_items: int
    candidate_covered_items: int
    baseline_high_risk_uncovered: list[str]
    baseline_medium_risk_uncovered: list[str]
    candidate_high_risk_uncovered: list[str]
    candidate_medium_risk_uncovered: list[str]
    items: list[ProfileComparisonItem]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class AuditChainEntry(BaseModel):
    path: str
    sha256: str
    size_bytes: int
    previous_chain_hash: str
    chain_hash: str


class AuditChainManifest(BaseModel):
    root_dir: str
    root_hash: str
    entries: list[AuditChainEntry]
    excluded_patterns: list[str]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class AuditChainVerification(BaseModel):
    manifest_path: str
    passed: bool
    checked_files: int
    errors: list[str]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
