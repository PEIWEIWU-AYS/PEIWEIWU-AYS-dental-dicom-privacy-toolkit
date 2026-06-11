# Filename Privacy Scan | 文件名隐私扫描

`ddpt filename scan` checks DICOM file names and directory names before sharing.
It catches path-level privacy risks that metadata anonymizers may miss.

`ddpt filename scan` 用于在分享前检查 DICOM 文件名和目录名，发现 metadata
脱敏工具可能忽略的路径层隐私风险。

## Command

```bash
ddpt filename scan demo-run/input \
  --json demo-run/reports/filename-privacy.json \
  --html demo-run/reports/filename-privacy.html
```

The built-in workflow recipe also writes:

```text
workflow-run/reports/filename-privacy.json
workflow-run/reports/filename-privacy.html
```

## What It Checks

The scan checks DICOM file and directory names for:

- email-like tokens
- phone-like numbers
- date-like tokens
- patient, case, MRN, or ID-like markers
- Chinese patient/case markers such as `患者`, `病例`, `姓名`, `身份证`, and `手机号`
- private-data folder markers

## Why This Matters

DICOM privacy is not only inside the DICOM object. A file named
`Patient_123456_20240101.dcm` can leak context even after metadata is cleaned.
This module adds a share-before-publishing guardrail that complements metadata
inspection, anonymization, pixel review, and repository safety scan.

DICOM 隐私不只存在于 DICOM header 或 pixel data 里。即使 metadata 已经脱敏，
类似 `Patient_123456_20240101.dcm` 的文件名仍可能泄露上下文。这个模块补上了
分享和发布前的文件名/路径层检查。

## Safety Notes

This is a path-name guardrail, not de-identification proof. Use it together with
inventory, remediation planning, anonymization, validation, pixel risk scan,
pixel review, and workflow quality gate.
