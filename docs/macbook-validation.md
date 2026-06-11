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
- `demo-run/reports/audit.html`
- `demo-run/reports/audit-chain.json`
- `demo-run/share/package.ddpt`
- `demo-run/share/package.key`

## 4. Verify Audit Chain

```bash
ddpt audit verify demo-run/reports/audit-chain.json
```

Expected:

- `Audit chain passed: True`

## 5. Open Human-Readable Outputs

Open these files locally:

```text
demo-run/reports/demo-summary.html
demo-run/reports/inventory.html
demo-run/reports/inspect.html
demo-run/reports/audit.html
```

The summary page should show embedded PNG previews for the synthetic input, anonymized DICOM, and pixel-redacted DICOM.

## 6. Optional Local API Check

Run this as a separate long-running command:

```bash
ddpt api serve demo-run --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765/docs
```

Expected:

- the API docs page loads locally
- `/health`, `/inventory`, `/inspect`, `/anonymize`, `/validate`, and `/preview` are listed

## Safety Boundary

Use synthetic data only. Do not put real patient DICOM, CBCT, X-ray images, photos, consent forms, clinic exports, or manuscript drafts inside this public repository.
