# MacBook Validation | MacBook 本地验收

This checklist validates the project locally on a MacBook using synthetic DICOM data only.

这份清单用于在 MacBook 上用合成 DICOM 数据验收项目效果。

## 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 2. Check Environment

```bash
ddpt doctor --json demo-run/reports/doctor.json
```

Expected:

- overall status is `PASS`
- Python is 3.10 or newer
- `pydicom`, `numpy`, `Pillow`, `cryptography`, `fastapi`, `uvicorn`, `typer`, and `rich` are available

## 3. Run One-Command Demo

```bash
ddpt demo demo-run
```

Expected key artifacts:

- `demo-run/reports/demo-summary.html`
- `demo-run/reports/inventory.html`
- `demo-run/reports/input-preview.png`
- `demo-run/reports/anonymized-preview.png`
- `demo-run/reports/redacted-preview.png`
- `demo-run/reports/pixel-review.html`
- `demo-run/reports/deid-comparison.html`
- `demo-run/reports/pixel-review/pixel-review-overlay.png`
- `demo-run/reports/audit.html`
- `demo-run/reports/audit-chain.json`
- `demo-run/reports/package-receipt.html`
- `demo-run/reports/share-readiness.html`
- `demo-run/share/package.ddpt`
- `demo-run/share/package.key`

## 4. Verify Audit Chain

```bash
ddpt audit verify demo-run/reports/audit-chain.json
```

Expected:

- `Audit chain passed: True`

## 5. Preview Anonymization Without Writing DICOM

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --dry-run \
  --audit demo-run/reports/dry-run-audit.json \
  --html demo-run/reports/dry-run-audit.html
```

Expected:

- dry-run audit files are created
- no new DICOM output is required

## 6. Run Recipe Workflow

```bash
ddpt workflow run recipes/dental-demo-workflow.yml \
  --root workflow-run \
  --json workflow-run/reports/workflow-run.json \
  --html workflow-run/reports/workflow-run.html
```

Expected:

- `workflow-run/reports/workflow-run.json` exists
- `workflow-run/reports/workflow-run.html` exists
- overall workflow status is `PASS`

## 7. Check Research Sharing Profile

```bash
ddpt policy export \
  --json demo-run/reports/policy-registry.json \
  --csv demo-run/reports/policy-registry.csv \
  --html demo-run/reports/policy-registry.html
ddpt profile lint dental-research-sharing \
  --json demo-run/reports/research-profile-lint.json \
  --html demo-run/reports/research-profile-lint.html
ddpt profile lint dental-linkable-research \
  --json demo-run/reports/linkable-profile-lint.json \
  --html demo-run/reports/linkable-profile-lint.html
ddpt profile show dental-research-sharing
ddpt profile show dental-linkable-research
ddpt profile compare dental-basic dental-research-sharing \
  --json demo-run/reports/profile-comparison.json \
  --html demo-run/reports/profile-comparison.html
ddpt profile compare dental-basic dental-linkable-research \
  --json demo-run/reports/linkable-profile-comparison.json \
  --html demo-run/reports/linkable-profile-comparison.html
ddpt compare deid \
  demo-run/input/sample.synthetic.dcm \
  demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/deid-comparison.json \
  --html demo-run/reports/deid-comparison.html
ddpt share readiness demo-run \
  --json demo-run/reports/share-readiness.json \
  --html demo-run/reports/share-readiness.html
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --profile dental-research-sharing \
  --dry-run \
  --audit demo-run/reports/research-dry-run.json \
  --html demo-run/reports/research-dry-run.html
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --profile dental-linkable-research \
  --dry-run \
  --audit demo-run/reports/linkable-dry-run.json \
  --html demo-run/reports/linkable-dry-run.html
```

Expected:

- policy registry JSON, CSV, and HTML files are created
- profile lint reports pass without errors
- the profile output lists date-shift and pseudonymize keywords
- the profile comparison report shows date fields changed from `blank` to `date_shift`
- the linkable profile comparison report shows direct identifiers changed to `pseudonymize`
- the de-identification comparison report passes and shows direct identifiers changed
- the share-readiness report passes all sharing gates
- dry-run audit includes `date_shift` actions for study-level date fields
- linkable dry-run audit includes `pseudonymize` actions for `PatientName` and `PatientID`
- no DICOM output is written during dry run

## 8. Run Release Audit

```bash
ddpt release audit . \
  --json release-audit.json \
  --html release-audit.html
```

Expected:

- overall release audit status is `PASS`
- JSON and HTML release-readiness reports are created
- README, docs, workflow recipe, CI, safety scan, and profile coverage checks pass

## 9. Run Capability Matrix

```bash
ddpt capability matrix \
  --root . \
  --json capability-matrix.json \
  --html capability-matrix.html
```

Expected:

- overall capability matrix status is `PASS`
- every capability item is `implemented`
- `capability-matrix.html` shows reference tools, project evidence, and differentiators

## 10. Generate Evidence Bundle

```bash
ddpt evidence bundle . --out evidence-run
```

Expected:

- overall evidence bundle status is `PASS`
- `evidence-run/reports/evidence-bundle.html` exists
- `evidence-run/reports/review-dashboard.html` exists
- `evidence-run/reports/capability-matrix.html` exists
- `evidence-run/reports/release-audit.html` exists
- `evidence-run/reports/workflow-run.html` exists
- `evidence-run/demo-run/reports/demo-summary.html` exists
- `evidence-run/demo-run/reports/deid-comparison.html` exists
- `evidence-run/demo-run/reports/pixel-review.html` exists
- `evidence-run/demo-run/reports/package-receipt.html` exists
- `evidence-run/demo-run/reports/share-readiness.html` exists

## 11. Run Objective Completion Audit

```bash
ddpt completion audit . \
  --json objective-audit.json \
  --html objective-audit.html
```

Expected:

- overall objective completion audit status is `PASS`
- every named reference tool has evidence
- inherited capabilities and differentiators are mapped to repository files and commands

## 12. Open Human-Readable Outputs

Open these files locally:

```text
release-audit.html
capability-matrix.html
objective-audit.html
evidence-run/reports/evidence-bundle.html
evidence-run/reports/review-dashboard.html
demo-run/reports/demo-summary.html
demo-run/reports/inventory.html
demo-run/reports/deid-comparison.html
demo-run/reports/inspect.html
demo-run/reports/audit.html
demo-run/reports/share-readiness.html
```

The summary page should show embedded PNG previews for the synthetic input, anonymized DICOM, and pixel-redacted DICOM.
The review dashboard should show quick links, artifact status, and synthetic PNG previews.

## 13. Optional Local API Check

Run this as a separate long-running command:

```bash
ddpt api serve demo-run --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765/docs
http://127.0.0.1:8765/workbench
```

Expected:

- the API docs page loads locally
- the local browser workbench loads locally
- `/health`, `/inventory`, `/inspect`, `/anonymize`, `/validate`, and `/preview` are listed
- the workbench profile selector includes `dental-linkable-research`
- the workbench buttons can run against synthetic files inside the API root

## Safety Boundary

Use synthetic data only. Do not put real patient DICOM, CBCT, X-ray images, photos, consent forms, clinic exports, or manuscript drafts inside this public repository.
