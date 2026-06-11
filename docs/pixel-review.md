# Pixel Review | 像素遮挡审核报告

`ddpt pixel-review` creates a visual review report for known burned-in
annotation regions.

`ddpt pixel-review` 用来针对已知 burned-in 标识区域生成视觉审核报告。

It creates:

- original PNG preview
- redaction overlay PNG preview
- redacted PNG preview
- JSON report
- HTML review page

## Command

```bash
ddpt pixel-review demo-run/outputs/sample.anonymized.dcm \
  --out-dir demo-run/reports/pixel-review \
  --plan profiles/dental-pixel-redaction.yml \
  --json demo-run/reports/pixel-review.json \
  --html demo-run/reports/pixel-review.html
```

Manual rectangles are also supported:

```bash
ddpt pixel-review demo-run/outputs/sample.anonymized.dcm \
  --out-dir demo-run/reports/pixel-review \
  --rect 1,0,1,1 \
  --json demo-run/reports/pixel-review.json \
  --html demo-run/reports/pixel-review.html
```

## Why This Matters

DicomCleaner highlights an important lesson: DICOM privacy is not only metadata.
Pixel data may contain burned-in patient names, IDs, dates, scanner labels, or
clinic annotations. This project does not attempt full OCR detection in version
0.1, but it does make known-region review reproducible and auditable.

## Safety Notes

Pixel review is not diagnostic interpretation. It does not automatically detect
every burned-in identifier, prove legal compliance, or certify that a real image
is safe to share. Use synthetic data for public demos, and combine pixel review
with inventory, metadata inspection, anonymization, validation, audit chains, and
package verification receipts.
