# Pixel Redaction Plans | 像素遮挡计划

`ddpt redact-pixels --plan` applies reusable YAML redaction regions to DICOM pixel data. This is useful when a clinic, device, or export workflow consistently places burned-in acquisition labels in the same image area.

`ddpt redact-pixels --plan` 可以用 YAML 文件复用像素遮挡区域，适合处理设备或导出流程中固定位置的 burned-in 标识。

## Built-In Example

```bash
ddpt redaction-plan show profiles/dental-pixel-redaction.yml
```

The built-in example uses a percent-based top banner region:

```yaml
name: dental-burned-in-banner
description: Demo dental pixel redaction plan for known burned-in acquisition labels near the top image banner.
regions:
  - label: top-acquisition-banner
    unit: percent
    x: 0
    y: 0
    width: 100
    height: 12
```

## Create a Template

```bash
ddpt redaction-plan init profiles/my-pixel-redaction.yml
```

## Apply a Plan

```bash
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm \
  --plan profiles/dental-pixel-redaction.yml \
  --out demo-run/outputs/sample.plan-redacted.dcm \
  --audit demo-run/reports/plan-redaction.json
```

## Coordinate Units

- `pixels`: absolute `x,y,width,height` values
- `percent`: relative values from `0` to `100`, resolved against the DICOM image rows and columns

Percent-based plans are easier to reuse across different image sizes.

## Safety Boundary

Pixel redaction plans only cover known regions. They do not automatically discover all burned-in identifiers. Always review the rendered PNG previews and keep real patient DICOM files outside the public repository.
