# Pixel Risk Scan | 像素风险扫描

`ddpt pixel-risk scan` runs a conservative pixel-layer privacy screen for a
DICOM image. It checks whether pixel data is readable, whether
`BurnedInAnnotation` is reassuring, and whether simple edge-band heuristics
suggest that manual pixel review may be needed.

`ddpt pixel-risk scan` 用于对 DICOM 图像做保守的像素层隐私风险扫描。它会检查
像素数据是否可读、`BurnedInAnnotation` 是否可靠，以及边缘高亮/边缘对比等简单
启发式信号是否提示需要人工像素审查。

## Command

```bash
ddpt pixel-risk scan demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/pixel-risk.json \
  --html demo-run/reports/pixel-risk.html
```

The built-in workflow recipe also writes:

```text
workflow-run/reports/pixel-risk.json
workflow-run/reports/pixel-risk.html
```

## What It Checks

The scan checks:

- DICOM PixelData presence
- pixel data readability
- rows and columns
- `BurnedInAnnotation`
- min/max pixel values
- edge high-intensity fraction
- edge contrast ratio
- recommended actions for manual pixel review or redaction planning

## Why This Matters

DicomCleaner reminds us that metadata de-identification is not enough when
patient labels can be burned into pixel data. This project keeps the first
version safe and honest: it does not claim automatic OCR, but it creates an
auditable signal that tells reviewers when to run `ddpt pixel-review` and
`ddpt redact-pixels`.

DicomCleaner 提醒我们：只清理 DICOM header 不够，患者标识可能被烧录进像素数据。
本项目保持保守和透明：不声称自动 OCR，但会生成可审计的风险信号，提醒审阅者何时
需要运行 `ddpt pixel-review` 和 `ddpt redact-pixels`。

## Safety Notes

This is not OCR, clinical interpretation, legal certification, or proof that all
burned-in identifiers were detected. Use it as a triage step before manual
visual review and redaction planning.
