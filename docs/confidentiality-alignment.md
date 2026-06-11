# DICOM Confidentiality Alignment | DICOM 保密配置对齐报告

`ddpt confidentiality alignment` creates a JSON and HTML report that maps a
DDPT anonymization profile to DICOM PS3.15-inspired Attribute Confidentiality
action codes and options.

`ddpt confidentiality alignment` 用来把本项目的脱敏 profile 映射到 DICOM
PS3.15 Attribute Confidentiality Profiles 的动作码和选项思想，生成可审计的
JSON/HTML 报告。它是标准语言对齐说明，不是官方 DICOM conformance 认证。

## Command

```bash
ddpt confidentiality alignment \
  --profile dental-basic \
  --json reports/confidentiality-alignment.json \
  --html reports/confidentiality-alignment.html
```

For research profiles:

```bash
ddpt confidentiality alignment \
  --profile dental-linkable-research \
  --json reports/linkable-confidentiality-alignment.json \
  --html reports/linkable-confidentiality-alignment.html
```

## What It Checks

The report checks whether the selected profile aligns with the toolkit's
DICOM-inspired privacy policy registry:

- `D`: replace with a dummy value, represented by `replace` or `pseudonymize`
- `Z`: zero-length value, represented by `blank`
- `X`: remove attribute, represented by blanking/removal behavior and private tag removal
- `C`: clean free-text descriptors, represented by replacing or blanking text fields
- `U`: replace UID, represented by UID regeneration
- `K`: keep low-risk technical metadata needed for readable synthetic DICOM files

The report also summarizes selected or supported options:

- Basic Application Level Confidentiality Profile baseline
- Clean Descriptors / free-text cleaning
- Clean Pixel Data evidence through pixel risk, review, and redaction reports
- Retain Longitudinal Temporal Information With Modified Dates for date-shift profiles
- UID replacement
- conservative private tag removal
- external encrypted package evidence rather than DICOM Encrypted Attributes Sequence

## Workflow Integration

The built-in workflow recipe writes:

```text
workflow-run/reports/confidentiality-alignment.json
workflow-run/reports/confidentiality-alignment.html
```

The evidence bundle also includes:

```text
evidence-run/reports/confidentiality-alignment.html
evidence-run/workflow-run/reports/confidentiality-alignment.html
```

## Why This Matters

Many DICOM tools can modify metadata. This report adds a public reviewer layer:
the profile is explained in the language of DICOM confidentiality actions, with
clear notes about which options are supported, partially supported, not selected,
or intentionally outside scope.

This helps the project stay honest. It makes the toolkit stronger than a basic
script while avoiding overclaiming regulatory or standard certification.

## Safety Notes

This report is for synthetic or explicitly approved test DICOM workflows. It
does not certify legal compliance, clinical safety, HIPAA compliance, security
compliance, or full DICOM conformance. Pixel cleaning is evidence-based and
manual/known-region oriented; it is not OCR and does not prove that all burned-in
identifiers were found.

## Reference

- DICOM PS3.15 Security and System Management Profiles, Attribute Confidentiality Profiles: https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_E.html
