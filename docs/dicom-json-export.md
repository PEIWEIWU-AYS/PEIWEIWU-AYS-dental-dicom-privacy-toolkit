# DICOM JSON Export | DICOM JSON 安全导出

`ddpt dicom-json export` creates an Orthanc-inspired local metadata JSON export
for integration demos.

`ddpt dicom-json export` 用于生成受 Orthanc 启发的本地 metadata JSON 导出，
方便接口集成演示和 MacBook 验收。

## Command

```bash
ddpt dicom-json export demo-run/input/sample.synthetic.dcm \
  --json demo-run/reports/dicom-json.json \
  --html demo-run/reports/dicom-json.html
```

The built-in workflow recipe also writes:

```text
workflow-run/reports/dicom-json.json
workflow-run/reports/dicom-json.html
```

## Safe Mode

Safe mode is the default. It keeps useful integration fields such as tag, VR,
keyword, risk, category, and recommended action, but redacts high-risk,
medium-risk, and unknown-risk values.

默认是 safe mode。报告保留 tag、VR、keyword、风险等级、类别和建议动作，但会隐藏
高风险、中风险和未知风险字段的原始值。

Use `--include-values` only for synthetic or explicitly approved test DICOM
files:

```bash
ddpt dicom-json export demo-run/input/sample.synthetic.dcm --include-values
```

## Local API

The local API exposes the same safe export:

```bash
curl -X POST http://127.0.0.1:8765/dicom-json \
  -H "Content-Type: application/json" \
  -d '{"path":"input/sample.synthetic.dcm"}'
```

## Why This Matters

Orthanc shows why REST APIs and metadata JSON are useful for imaging workflows.
This project keeps that integration lesson while staying local-first and
privacy-first. It does not try to become a PACS or production DICOMweb server.

Orthanc 的优势是接口化、Web UI 和影像工作流集成。本项目吸收这个思路，但保持轻量、
本地优先、隐私优先：导出适合系统集成的 metadata JSON，同时默认不暴露敏感值。

## Safety Notes

This command does not export pixel data. It is not clinical software, not a
diagnostic viewer, and not legal or regulatory certification. Keep real patient
DICOM outside the public repository and outside demo folders.
