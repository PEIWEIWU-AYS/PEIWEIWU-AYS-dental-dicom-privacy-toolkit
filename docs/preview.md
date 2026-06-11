# DICOM PNG Preview | DICOM 像素预览

`ddpt preview` renders DICOM pixel data to a PNG image for workflow review. It is designed for demos, documentation, before/after screenshots, and quick checks on a local MacBook.

`ddpt preview` 可以把 DICOM 像素数据渲染成 PNG 图片，用于流程演示、文档截图、脱敏前后对比和本地快速检查。

## Example

```bash
ddpt preview demo-run/input/sample.synthetic.dcm \
  --out demo-run/reports/input-preview.png \
  --json demo-run/reports/input-preview.json
```

The one-command demo also creates:

- `reports/input-preview.png`
- `reports/anonymized-preview.png`
- `reports/redacted-preview.png`

These images are embedded in `reports/demo-summary.html`.

## What It Shows

- pixel dimensions
- normalized grayscale PNG preview
- visible effect of manual pixel redaction
- before/after artifacts for README screenshots or papers

## Safety Boundary

PNG previews are for workflow review only. They are not diagnostic images, not clinical-quality viewers, and not a substitute for PACS, OHIF, Orthanc, or professional dental imaging software.

Do not create previews from real patient DICOM files inside this public repository.
