# Workflow Quality Gate | 工作流质量门禁

`ddpt quality gate` checks whether a synthetic demo or workflow output folder
has the evidence needed for reproducible public review.

`ddpt quality gate` 用来检查合成数据 demo 或 workflow 输出目录是否具备可复现、
可审计、可公开展示的关键证据。

## Command

```bash
ddpt quality gate workflow-run \
  --workflow-report workflow-run/reports/workflow-run.json \
  --json workflow-run/reports/quality-gate.json \
  --html workflow-run/reports/quality-gate.html
```

The workflow recipe also includes a `quality-gate` stage that writes:

```text
workflow-run/reports/quality-gate.json
workflow-run/reports/quality-gate.html
```

## What It Checks

The gate checks:

- source synthetic DICOM exists
- anonymized DICOM exists
- pixel-redacted DICOM exists
- anonymized DICOM validation passed
- before/after de-identification comparison passed
- no residual high-risk or medium-risk policy items remain
- private tags after anonymization are zero
- pixel review regions and PNG previews exist
- encrypted package receipt passed and has entries
- audit chain verification passed
- share-readiness report passed
- de-identification certificate passed
- optional workflow run report passed when provided

## Why This Matters

RSNA CTP teaches the value of staged pipelines. Orthanc teaches the value of
integration surfaces and repeatable operations. This project adds a lightweight
quality gate that can be run locally on a MacBook or in CI, then shared as
JSON/HTML evidence.

RSNA CTP 的优势是多阶段 pipeline，Orthanc 的优势是接口化和可复现操作。本项目在
轻量本地工具里加入质量门禁，让整个牙科 DICOM 隐私流程可以被 MacBook、CI 和
HTML 报告共同验证。

## Safety Notes

This gate verifies project evidence produced by the toolkit. It is not clinical,
legal, regulatory, security, or HIPAA certification. Use synthetic or explicitly
approved test DICOM files only.
