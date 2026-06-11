# Demo Guide | 演示指南

This guide shows how to validate Dental DICOM Privacy Toolkit locally on a MacBook using synthetic data only.

## Quick Demo

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/generate_demo_assets.py --out demo-run
```

The generated `demo-run/` directory contains:

```text
demo-run/
  input/sample.synthetic.dcm
  reports/inventory.json
  reports/inventory.csv
  reports/inventory.html
  reports/input-preview.png
  reports/anonymized-preview.png
  reports/redacted-preview.png
  outputs/sample.anonymized.dcm
  outputs/sample.redacted.dcm
  reports/inspect.json
  reports/inspect.html
  reports/audit.json
  reports/audit.html
  reports/validation.json
  reports/redaction.json
  reports/audit-chain.json
  reports/audit-chain-verify.json
  reports/demo-summary.json
  reports/demo-summary.html
  share/manifest.json
  share/package.ddpt
  share/package.key
```

## What to Check

Open:

```text
demo-run/reports/demo-summary.html
demo-run/reports/inspect.html
demo-run/reports/audit.html
```

The demo should show:

- synthetic DICOM input creation
- read-only directory inventory before anonymization
- PNG previews for visual workflow review
- high-risk metadata detection
- dental-basic anonymization
- direct identifier replacement or blanking
- UID regeneration
- validation pass result
- manual pixel redaction audit
- reusable percent-based pixel redaction plans
- tamper-evident audit chain
- encrypted package with manifest and checksums

## CLI Equivalent

The script is equivalent to:

```bash
ddpt demo demo-run
```

For step-by-step inspection:

```bash
ddpt synthetic demo-run/sample.dcm
ddpt inventory demo-run --json demo-run/reports/inventory.json --csv demo-run/reports/inventory.csv --html demo-run/reports/inventory.html
ddpt preview demo-run/sample.dcm --out demo-run/reports/sample-preview.png --json demo-run/reports/sample-preview.json
ddpt inspect demo-run/sample.dcm --json demo-run/reports/inspect.json --html demo-run/reports/inspect.html
ddpt anonymize demo-run/sample.dcm --out demo-run/outputs/sample.anonymized.dcm --audit demo-run/reports/audit.json --html demo-run/reports/audit.html
ddpt validate demo-run/outputs/sample.anonymized.dcm --json demo-run/reports/validation.json
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm --rect 1,0,1,1 --out demo-run/outputs/sample.redacted.dcm --audit demo-run/reports/redaction.json
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm --plan profiles/dental-pixel-redaction.yml --out demo-run/outputs/sample.plan-redacted.dcm --audit demo-run/reports/plan-redaction.json
ddpt package demo-run/outputs --encrypt --key-out demo-run/share/package.key --manifest demo-run/share/manifest.json --out demo-run/share/package.ddpt
ddpt verify demo-run/share/package.ddpt --key demo-run/share/package.key
```

For a directory-level preflight before batch anonymization:

```bash
ddpt inventory demo-run/input \
  --json demo-run/reports/inventory.json \
  --csv demo-run/reports/inventory.csv \
  --html demo-run/reports/inventory.html
```

Open `demo-run/reports/demo-summary.html` to see embedded input, anonymized, and pixel-redacted PNG previews.

For reusable burned-in label removal, inspect the sample percent-based plan:

```bash
ddpt redaction-plan show profiles/dental-pixel-redaction.yml
```

## Safety

The demo uses synthetic DICOM data only. Do not copy real patient DICOM files, clinical photos, PDFs, spreadsheets, or clinic exports into the repository.
