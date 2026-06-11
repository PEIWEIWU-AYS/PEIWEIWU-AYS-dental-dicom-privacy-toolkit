# Capability Matrix | 竞品能力矩阵

`ddpt capability matrix` creates a competitor-informed audit report that maps
well-known DICOM privacy tool capabilities to this repository's local evidence.

`ddpt capability matrix` 会把 RSNA DICOM Anonymizer、DicomCleaner、Orthanc、
RSNA CTP、DCMTK `dcmodify` 和 pydicom 示例中的关键能力，映射到本项目已经
实现的文件、命令和报告证据。

## Command

```bash
ddpt capability matrix \
  --root . \
  --json capability-matrix.json \
  --html capability-matrix.html
```

Expected result:

- terminal summary shows every capability as `implemented`
- JSON output is written for CI and machine review
- HTML output is written for GitHub demos, paper supplements, and collaborator review

## What It Checks

The matrix reviews whether the repository has evidence for:

- metadata inspection and risk classification
- filename and path privacy scan before sharing
- privacy remediation plans before anonymization
- multi-file synthetic dental study generation
- configurable anonymization profiles
- profile coverage, comparison, and lint checks
- deterministic linkable pseudonymization for synthetic longitudinal research demos
- conservative pixel risk scan for burned-in identifier triage
- burned-in pixel review and redaction evidence
- exact DICOM tag operations
- DCMTK dcmodify-style profile operation plan export
- multi-stage YAML workflow recipes
- batch de-identification evidence for directory workflows
- workflow-level de-identification certificate generation
- workflow quality gate for reproducible public review evidence
- local Orthanc-inspired REST API
- local browser workbench for GUI-style synthetic workflow review
- original objective completion audit with requirement-level evidence
- encrypted sharing packages
- package verification receipts
- de-identification certificate for synthetic sharing handoff evidence
- audit chains, safety scan, release audit, and evidence bundles
- bilingual GitHub discoverability and synthetic-data safety positioning

## Why This Matters

The goal is not to claim that this small toolkit replaces mature projects like
Orthanc, RSNA CTP, or DicomCleaner. The goal is to show, with repository evidence,
which proven ideas were inherited and where this project adds a dental-focused,
MacBook-verifiable, bilingual, report-first workflow.

## Evidence Bundle Integration

`ddpt evidence bundle` automatically includes:

```text
reports/capability-matrix.json
reports/capability-matrix.html
```

The evidence bundle only passes when the capability matrix passes.

## Safety Notes

The capability matrix is a public project audit. It does not certify legal
compliance, clinical safety, regulatory approval, or complete DICOM
de-identification. Use synthetic data for public demos and keep real patient
materials outside the repository.
