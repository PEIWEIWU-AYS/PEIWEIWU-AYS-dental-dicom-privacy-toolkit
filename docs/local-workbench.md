# Local Browser Workbench | 本地浏览器工作台

`ddpt api serve` includes a lightweight local browser workbench at
`/workbench`. It provides GUI-style controls for the synthetic DICOM privacy
workflow while keeping all files inside the local API root.

`ddpt api serve` 会在 `/workbench` 提供一个轻量本地浏览器工作台。它让用户可以
用按钮触发合成 DICOM 演示、目录 inventory、metadata inspect、匿名化、验证和 PNG
preview，也可以生成隐私整改、文件名隐私、像素风险、隐私回归和 GitHub 发布预检
报告，同时所有路径都被限制在本地 API root 内。

## Start

```bash
ddpt api serve demo-run --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765/workbench
```

The same server also exposes:

- API docs: `http://127.0.0.1:8765/docs`
- JSON API root: `http://127.0.0.1:8765/`

## What It Does

The workbench can call local API endpoints for:

- environment health check
- one-click synthetic demo generation
- DICOM directory inventory
- metadata inspection
- profile-based anonymization
- anonymized DICOM validation
- PNG preview generation
- filename privacy reports
- privacy remediation reports
- pixel risk reports
- privacy regression suite reports
- GitHub publish preflight reports
- safe links to generated files inside the API root

The profile selector includes:

- `dental-basic`
- `dental-research-sharing`
- `dental-linkable-research`

## Why This Matters

RSNA DICOM Anonymizer and DicomCleaner show that GUI workflows help
non-programmers inspect privacy tooling. Orthanc shows the value of a browser UI
and REST API. This project inherits that usability lesson without adding a
production PACS, public upload service, or heavy deployment requirement.

The newer evidence buttons expose report-first workflow checks through the same
local browser entrypoint. This makes MacBook validation easier for
non-programmer reviewers: they can trigger the privacy reports from the browser
and then open the generated HTML artifacts from the API root.

## Safety Boundary

The workbench is local-only and synthetic-data-first. It is not a clinical
viewer, PACS, DICOMweb server, regulatory compliance system, or diagnostic tool.
Do not expose it to the public internet. Keep real patient DICOM, CBCT, X-ray
images, photos, clinic exports, linkage tables, and consent forms outside the
API root and outside this public repository.
