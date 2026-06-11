from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

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


class DicomJsonElement(BaseModel):
    tag: str
    keyword: str
    name: str
    vr: str
    risk: RiskLevel
    category: str
    recommended_action: str
    value: list[str]
    redacted: bool
    note: str


class DicomJsonExportReport(BaseModel):
    input_path: str
    safe_mode: bool
    include_values: bool
    total_elements: int
    redacted_elements: int
    high_risk_elements: int
    medium_risk_elements: int
    unknown_risk_elements: int
    dicom_json: dict[str, dict[str, Any]]
    elements: list[DicomJsonElement]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


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


class ShareReadinessCheck(BaseModel):
    id: str
    category: str
    passed: bool
    message: str
    evidence: list[str] = Field(default_factory=list)


class ShareReadinessReport(BaseModel):
    root_dir: str
    passed: bool
    checks: list[ShareReadinessCheck]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def passed_checks(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_checks(self) -> int:
        return sum(1 for check in self.checks if not check.passed)


class CertificateEvidenceItem(BaseModel):
    id: str
    category: str
    passed: bool
    summary: str
    evidence: list[str] = Field(default_factory=list)


class DeidentificationCertificate(BaseModel):
    root_dir: str
    passed: bool
    profile: str
    input_path: str
    anonymized_path: str
    package_path: str | None = None
    package_sha256: str | None = None
    passed_checks: int
    total_checks: int
    residual_high_risk_keywords: list[str] = Field(default_factory=list)
    residual_medium_risk_keywords: list[str] = Field(default_factory=list)
    private_tags_after: int | None = None
    pixel_review_regions: int = 0
    package_entries: int = 0
    share_readiness_passed: bool = False
    checks: list[CertificateEvidenceItem] = Field(default_factory=list)
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


class ProfileConformanceCheck(BaseModel):
    keyword: str
    action: str
    status: Literal["pass", "fail", "skip"]
    passed: bool
    original: str
    expected: str
    actual: str
    message: str


class ProfileConformanceReport(BaseModel):
    source_path: str
    anonymized_path: str
    profile: str
    passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    skipped_checks: int
    checks: list[ProfileConformanceCheck]
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


class SyntheticStudyFile(BaseModel):
    path: str
    patient_id: str
    patient_name: str
    modality: str
    study_description: str
    study_instance_uid: str
    series_instance_uid: str
    sop_instance_uid: str


class SyntheticStudyReport(BaseModel):
    output_dir: str
    patient_count: int
    files_per_patient: int
    total_files: int
    modalities: dict[str, int]
    files: list[SyntheticStudyFile]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class PixelReviewRegion(BaseModel):
    label: str
    x: int
    y: int
    width: int
    height: int


class PixelReviewReport(BaseModel):
    input_path: str
    plan_path: str | None = None
    original_preview_png: str
    overlay_preview_png: str
    redacted_preview_png: str
    rows: int
    columns: int
    rendered_width: int
    rendered_height: int
    burned_in_annotation: str | None = None
    regions: list[PixelReviewRegion]
    warnings: list[str] = Field(default_factory=list)
    note: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class PixelRiskSignal(BaseModel):
    id: str
    severity: Literal["high", "medium", "low"]
    passed: bool
    message: str
    evidence: list[str] = Field(default_factory=list)


class PixelRiskScanReport(BaseModel):
    input_path: str
    passed: bool
    pixel_data_present: bool
    rows: int | None = None
    columns: int | None = None
    burned_in_annotation: str | None = None
    min_pixel_value: float | None = None
    max_pixel_value: float | None = None
    edge_high_intensity_fraction: float | None = None
    edge_contrast_ratio: float | None = None
    signals: list[PixelRiskSignal]
    recommended_actions: list[str] = Field(default_factory=list)
    note: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class FilenamePrivacyFinding(BaseModel):
    path: str
    part: str
    severity: Literal["high", "medium", "low"]
    rule_id: str
    message: str
    suggested_safe_name: str


class FilenamePrivacyFileResult(BaseModel):
    path: str
    suggested_safe_name: str
    findings: list[FilenamePrivacyFinding] = Field(default_factory=list)


class FilenamePrivacyScanReport(BaseModel):
    input_path: str
    recursive: bool
    passed: bool
    scanned_files: int
    findings_count: int
    high_findings: int
    medium_findings: int
    files: list[FilenamePrivacyFileResult]
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


class DashboardArtifact(BaseModel):
    label: str
    category: str
    path: str
    description: str
    exists: bool


class DashboardPreview(BaseModel):
    label: str
    path: str
    exists: bool


class ReviewDashboardReport(BaseModel):
    evidence_dir: str
    output_path: str
    passed: bool
    evidence_bundle_passed: bool
    total_artifacts: int
    available_artifacts: int
    missing_artifacts: int
    artifacts: list[DashboardArtifact]
    previews: list[DashboardPreview]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DeidentificationComparisonItem(BaseModel):
    keyword: str
    risk: RiskLevel
    category: str
    recommended_action: str
    status: Literal["changed", "unchanged", "removed", "added", "absent"]
    passed: bool
    before: str
    after: str
    note: str


class DeidentificationComparisonReport(BaseModel):
    source_path: str
    anonymized_path: str
    passed: bool
    total_items: int
    passed_items: int
    failed_items: int
    changed_items: int
    removed_items: int
    unchanged_items: int
    residual_high_risk_keywords: list[str]
    residual_medium_risk_keywords: list[str]
    private_tags_before: int
    private_tags_after: int
    private_tags_removed: bool
    pixel_data_before_sha256: str | None = None
    pixel_data_after_sha256: str | None = None
    pixel_data_changed: bool | None = None
    items: list[DeidentificationComparisonItem]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class CompetitorReference(BaseModel):
    name: str
    category: str
    url: str
    strengths: list[str]
    gaps_for_dental_toolkit: list[str]


class CapabilityMatrixItem(BaseModel):
    id: str
    capability: str
    source_tools: list[str]
    status: Literal["implemented", "partial", "missing"]
    evidence: list[str]
    missing_evidence: list[str] = Field(default_factory=list)
    command: str | None = None
    differentiator: str
    note: str


class CapabilityMatrixReport(BaseModel):
    root_dir: str
    passed: bool
    implemented_items: int
    partial_items: int
    missing_items: int
    total_items: int
    references: list[CompetitorReference]
    items: list[CapabilityMatrixItem]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class CompetitorCoverageTool(BaseModel):
    name: str
    category: str
    url: str
    status: Literal["covered", "partial", "missing"]
    strengths_learned: list[str]
    project_responses: list[str]
    implemented_capabilities: int
    partial_capabilities: int
    missing_capabilities: int
    capabilities: list[CapabilityMatrixItem]


class CompetitorCoverageReport(BaseModel):
    root_dir: str
    passed: bool
    covered_tools: int
    partial_tools: int
    missing_tools: int
    total_tools: int
    implemented_capabilities: int
    total_capabilities: int
    boundary_notes: list[str]
    tools: list[CompetitorCoverageTool]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ObjectiveAuditItem(BaseModel):
    id: str
    category: str
    requirement: str
    passed: bool
    evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    note: str


class ObjectiveAuditReport(BaseModel):
    root_dir: str
    passed: bool
    total_items: int
    passed_items: int
    failed_items: int
    items: list[ObjectiveAuditItem]
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


class DcmodifyPlanItem(BaseModel):
    order: int
    keyword: str
    tag: str
    profile_action: str
    dcmodify_action: Literal["modify", "erase-private", "generate-uid"]
    option: str
    argument: str
    command: str
    value_preview: str
    note: str


class DcmodifyPlanReport(BaseModel):
    input_path: str
    profile: str
    total_operations: int
    modify_operations: int
    uid_operations: int
    private_tag_operations: int
    commands: list[str]
    items: list[DcmodifyPlanItem]
    note: str
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


class WorkflowQualityGateCheck(BaseModel):
    id: str
    stage: str
    required: bool
    passed: bool
    message: str
    evidence: list[str] = Field(default_factory=list)


class WorkflowQualityGateReport(BaseModel):
    root_dir: str
    passed: bool
    workflow_report_path: str | None = None
    required_checks: int
    passed_checks: int
    failed_checks: int
    checks: list[WorkflowQualityGateCheck]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class PrivacyRemediationItem(BaseModel):
    tag: str
    keyword: str
    risk: RiskLevel
    category: str
    current_value: str
    recommended_action: str
    profile_action: str
    covered_by_profile: bool
    dicom_action_code: str
    note: str


class PrivacyRemediationFilePlan(BaseModel):
    path: str
    readable: bool
    error: str | None = None
    modality: str | None = None
    high_risk_items: int = 0
    medium_risk_items: int = 0
    uncovered_high_risk_items: int = 0
    uncovered_medium_risk_items: int = 0
    private_tags_present: int = 0
    burned_in_annotation: str | None = None
    pixel_review_recommended: bool = False
    items: list[PrivacyRemediationItem] = Field(default_factory=list)


class PrivacyRemediationPlanReport(BaseModel):
    input_path: str
    profile: str
    recursive: bool
    passed: bool
    total_files: int
    readable_files: int
    unreadable_files: int
    total_items: int
    covered_items: int
    uncovered_items: int
    uncovered_high_risk_items: int
    uncovered_medium_risk_items: int
    private_tags_present: int
    pixel_review_recommended_files: int
    files: list[PrivacyRemediationFilePlan]
    next_steps: list[str] = Field(default_factory=list)
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
    deid_comparison_json: str
    deid_comparison_html: str
    profile_conformance_json: str
    profile_conformance_html: str
    validation_json: str
    share_readiness_json: str
    share_readiness_html: str
    pixel_review_json: str
    pixel_review_html: str
    redaction_json: str
    manifest_json: str
    package_path: str
    key_path: str
    package_receipt_json: str
    package_receipt_html: str
    deid_certificate_json: str
    deid_certificate_html: str
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
    deid_comparison_json: str | None = None
    validation_passed: bool = False
    deid_comparison_passed: bool = False
    error: str | None = None


class BatchSummary(BaseModel):
    input_dir: str
    output_dir: str
    profile: str
    total_files: int
    processed_files: int
    failed_files: int
    validation_failures: int
    comparison_failures: int = 0
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


class PolicyRegistryReport(BaseModel):
    source: str
    total_items: int
    high_risk_items: int
    medium_risk_items: int
    low_risk_items: int
    items: list[TagPolicy]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


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


class ProfileLintFinding(BaseModel):
    severity: Literal["error", "warning"]
    rule_id: str
    keyword: str | None = None
    message: str


class ProfileLintReport(BaseModel):
    profile: str
    passed: bool
    error_count: int
    warning_count: int
    covered_items: int
    total_policy_items: int
    high_risk_uncovered: list[str]
    medium_risk_uncovered: list[str]
    findings: list[ProfileLintFinding]
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
