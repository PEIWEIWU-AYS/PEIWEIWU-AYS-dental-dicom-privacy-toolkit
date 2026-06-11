# Review Dashboard | 本地审阅仪表盘

`ddpt dashboard build` creates a static HTML dashboard from an evidence bundle.
It is a lightweight visual entrypoint for non-programmer review, inspired by the
accessibility of GUI tools such as RSNA DICOM Anonymizer, DicomCleaner, and
Orthanc's Web UI, while staying local-first and synthetic-data-only.

`ddpt dashboard build` 会从 evidence bundle 生成一个静态 HTML 仪表盘，把关键
报告、预览图和证据链接集中到一个页面，适合在 MacBook 上演示。

## Commands

Generate a complete evidence bundle:

```bash
ddpt evidence bundle . --out evidence-run
```

The evidence bundle automatically writes:

```text
evidence-run/reports/review-dashboard.html
evidence-run/reports/review-dashboard.json
```

You can also rebuild the dashboard manually:

```bash
ddpt dashboard build evidence-run \
  --out evidence-run/reports/review-dashboard.html \
  --json evidence-run/reports/review-dashboard.json
```

Open it locally:

```bash
open evidence-run/reports/review-dashboard.html
```

## What It Shows

The dashboard includes:

- overall evidence bundle status
- artifact availability counts
- quick links to the strongest reports
- de-identification certificate link when present
- synthetic input, anonymized, redacted, and pixel-review PNG previews
- all evidence artifacts with status, category, path, and description

## Why This Matters

CLI commands are strong for reproducibility, but dental collaborators, clinic
owners, and reviewers often need a single visual entrypoint. The dashboard makes
the project easier to inspect without adding a production PACS, cloud upload,
or browser-based real-patient workflow.

## Safety Notes

The dashboard is a local static report. It does not upload files, certify
de-identification, provide clinical diagnosis, or prove legal compliance. Use it
with synthetic evidence bundles and keep real patient DICOM outside the public
repository.
