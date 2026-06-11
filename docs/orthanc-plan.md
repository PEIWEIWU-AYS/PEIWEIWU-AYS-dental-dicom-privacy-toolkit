# Orthanc Anonymization Plan | Orthanc 匿名化计划

`ddpt orthanc plan` exports a review-only Orthanc REST anonymization payload
from a DDPT dental anonymization profile.

`ddpt orthanc plan` 会把本项目的牙科脱敏 profile 转换成可审阅的 Orthanc REST
匿名化 payload 和 curl 命令。该命令只生成计划，不连接 Orthanc，也不上传 DICOM。

## Command

```bash
ddpt orthanc plan workflow-run/input/sample.synthetic.dcm \
  --profile dental-basic \
  --resource-id sample-synthetic-instance \
  --json workflow-run/reports/orthanc-plan.json \
  --html workflow-run/reports/orthanc-plan.html
```

The built-in workflow recipe writes:

```text
workflow-run/reports/orthanc-plan.json
workflow-run/reports/orthanc-plan.html
```

## What It Exports

The report includes:

- Orthanc endpoint preview, such as `/instances/{id}/anonymize`
- JSON payload with `Replace`, `KeepPrivateTags`, `DicomVersion`, and `Force`
- curl command preview for expert review
- per-keyword mapping from DDPT profile action to Orthanc payload section
- notes for UID handling and private-tag behavior

## Why This Matters

Orthanc is strong because it exposes DICOM workflows through a REST API. This
project keeps the first public release local and synthetic-data-first, but it
still provides an integration bridge: dental YAML profile decisions can be
reviewed as Orthanc-style REST payloads before any server is contacted.

## Safety Notes

This command is review-only. It does not contact Orthanc, does not upload DICOM,
and does not prove that a target Orthanc server will behave identically across
versions or configuration. Verify payload behavior on synthetic data before any
approved non-synthetic workflow.
