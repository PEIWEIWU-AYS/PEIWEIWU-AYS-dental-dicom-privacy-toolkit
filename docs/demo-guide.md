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
  reports/pixel-review.json
  reports/pixel-review.html
  reports/pixel-review/pixel-review-overlay.png
  outputs/sample.anonymized.dcm
  outputs/sample.redacted.dcm
  reports/inspect.json
  reports/inspect.html
  reports/audit.json
  reports/audit.html
  reports/profile-conformance.json
  reports/profile-conformance.html
  reports/validation.json
  reports/redaction.json
  reports/audit-chain.json
  reports/audit-chain-verify.json
  reports/package-receipt.json
  reports/package-receipt.html
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
- dry-run anonymization preview
- dental-basic anonymization
- direct identifier replacement or blanking
- UID regeneration
- profile conformance verification against the selected profile
- validation pass result
- pixel review overlay for known burned-in annotation regions
- manual pixel redaction audit
- reusable percent-based pixel redaction plans
- tamper-evident audit chain
- encrypted package with manifest and checksums
- package verification receipt for receiver-side evidence
- de-identification certificate for synthetic sharing handoff evidence

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
ddpt anonymize demo-run/sample.dcm --dry-run --audit demo-run/reports/dry-run-audit.json --html demo-run/reports/dry-run-audit.html
ddpt anonymize demo-run/sample.dcm --out demo-run/outputs/sample.anonymized.dcm --audit demo-run/reports/audit.json --html demo-run/reports/audit.html
ddpt profile verify demo-run/sample.dcm demo-run/outputs/sample.anonymized.dcm --profile dental-basic --json demo-run/reports/profile-conformance.json --html demo-run/reports/profile-conformance.html
ddpt compare deid demo-run/sample.dcm demo-run/outputs/sample.anonymized.dcm --json demo-run/reports/deid-comparison.json --html demo-run/reports/deid-comparison.html
ddpt validate demo-run/outputs/sample.anonymized.dcm --json demo-run/reports/validation.json
ddpt pixel-review demo-run/outputs/sample.anonymized.dcm --out-dir demo-run/reports/pixel-review --rect 1,0,1,1 --json demo-run/reports/pixel-review.json --html demo-run/reports/pixel-review.html
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm --rect 1,0,1,1 --out demo-run/outputs/sample.redacted.dcm --audit demo-run/reports/redaction.json
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm --plan profiles/dental-pixel-redaction.yml --out demo-run/outputs/sample.plan-redacted.dcm --audit demo-run/reports/plan-redaction.json
ddpt package demo-run/outputs --encrypt --key-out demo-run/share/package.key --manifest demo-run/share/manifest.json --out demo-run/share/package.ddpt
ddpt verify demo-run/share/package.ddpt --key demo-run/share/package.key --receipt demo-run/reports/package-receipt.json --html demo-run/reports/package-receipt.html
ddpt share readiness demo-run --json demo-run/reports/share-readiness.json --html demo-run/reports/share-readiness.html
ddpt certificate create demo-run --json demo-run/reports/deid-certificate.json --html demo-run/reports/deid-certificate.html
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

For research-sharing date shifting:

```bash
ddpt policy export \
  --json demo-run/reports/policy-registry.json \
  --csv demo-run/reports/policy-registry.csv \
  --html demo-run/reports/policy-registry.html
ddpt profile lint dental-research-sharing \
  --json demo-run/reports/research-profile-lint.json \
  --html demo-run/reports/research-profile-lint.html
ddpt profile show dental-research-sharing
ddpt profile compare dental-basic dental-research-sharing \
  --json demo-run/reports/profile-comparison.json \
  --html demo-run/reports/profile-comparison.html
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --profile dental-research-sharing \
  --dry-run \
  --audit demo-run/reports/research-dry-run.json \
  --html demo-run/reports/research-dry-run.html
```

For a complete local evidence bundle:

```bash
ddpt capability matrix --root . --json capability-matrix.json --html capability-matrix.html
ddpt evidence bundle . --out evidence-run
ddpt dashboard build evidence-run --out evidence-run/reports/review-dashboard.html
open evidence-run/reports/review-dashboard.html
open evidence-run/reports/evidence-bundle.html
open evidence-run/demo-run/reports/deid-certificate.html
```

## Safety

The demo uses synthetic DICOM data only. Do not copy real patient DICOM files, clinical photos, PDFs, spreadsheets, or clinic exports into the repository.
