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
