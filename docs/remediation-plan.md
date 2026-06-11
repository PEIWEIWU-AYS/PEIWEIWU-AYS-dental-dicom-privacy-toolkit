# Privacy Remediation Plan | 隐私整改计划

`ddpt remediation plan` creates a pre-anonymization action plan for a DICOM file
or directory. It turns metadata risk findings into reviewer-friendly next steps.

`ddpt remediation plan` 用于在脱敏前为单个 DICOM 文件或目录生成隐私整改计划，
把 metadata 风险项转成可审阅、可执行的处理建议。

## Command

```bash
ddpt remediation plan demo-run/input \
  --profile dental-basic \
  --json demo-run/reports/remediation-plan.json \
  --html demo-run/reports/remediation-plan.html
```

The built-in workflow recipe also writes:

```text
workflow-run/reports/remediation-plan.json
workflow-run/reports/remediation-plan.html
```

## What It Checks

The remediation plan checks:

- high-risk and medium-risk DICOM metadata items
- recommended action from the toolkit privacy policy registry
- current profile action for each risky keyword
- whether the selected profile covers the recommended action
- private tag presence and whether private-tag removal is enabled
- `BurnedInAnnotation` and whether pixel review should be considered
- unreadable files before batch anonymization

## Why This Matters

DicomCleaner and RSNA DICOM Anonymizer make cleaning workflows accessible.
DCMTK gives precise tag-level control. This project adds a planning layer:
before writing anonymized output, a reviewer can see what needs to happen, what
the selected profile already covers, and where a stronger profile or manual
review may be needed.

DicomCleaner 和 RSNA DICOM Anonymizer 的优势是让清理流程更容易理解；DCMTK
的优势是精确 tag 操作。本项目增加了一个脱敏前计划层：在写出新 DICOM 之前，
先让审阅者看到哪些标签需要处理、当前 profile 是否覆盖，以及是否需要像素审查。

## Safety Notes

The report is a planning aid, not proof of de-identification. After running a
plan, still run anonymization, validation, before/after de-identification
comparison, pixel review when needed, and the workflow quality gate.
