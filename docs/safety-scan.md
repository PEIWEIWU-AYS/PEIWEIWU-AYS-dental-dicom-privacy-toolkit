# Public Repository Safety Scan | 公开仓库安全扫描

`ddpt safety scan` checks a repository before publishing or pushing to GitHub. It is designed to reduce the chance of accidentally committing real clinical material.

`ddpt safety scan` 用于在发布或推送 GitHub 前检查仓库，降低误传真实临床资料的风险。

## Example

```bash
ddpt safety scan . --json reports/safety-scan.json
```

Expected result for a clean public repository:

- `Overall: PASS`
- zero findings

## What It Flags

- DICOM files outside clearly named synthetic examples
- radiograph or photo-like image files
- PDFs, Word documents, spreadsheets, CSV exports, and ZIP archives
- `.env`, private keys, certificates, and package keys
- suspicious private data folder names such as `private`, `patient-data`, `real-data`, `clinical-data`, `clinic-exports`, `raw-dicom`, and `dicom-private`

## What It Ignores by Default

Generated and local-only directories are ignored:

- `.git`
- `.venv`
- `reports`
- `outputs`
- `share`
- `restored`
- `demo-run`
- `demo-*`
- `workflow-run`
- `workflow-*`
- Python and Node cache/build directories

## Safety Boundary

This scan is a repository guardrail, not a legal or clinical privacy guarantee. Use it together with `.gitignore`, careful manual review, and a strict habit of keeping real patient data outside the public project folder.
