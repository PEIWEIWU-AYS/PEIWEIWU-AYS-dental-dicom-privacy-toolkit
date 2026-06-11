# Evidence Bundle | 本地证据包

`ddpt evidence bundle` creates a local demonstration bundle that gathers the
project's strongest proof artifacts into one folder.

`ddpt evidence bundle` 会把项目最重要的本地验证证据集中生成到一个目录里，方便
MacBook 验收、GitHub 展示、论文方法学说明和协作者沟通。

## Command

```bash
ddpt evidence bundle . --out evidence-run
```

The command uses synthetic DICOM data only. It does not require real patient
DICOM, radiographs, photos, consent forms, spreadsheets, or clinic exports.

## Included Evidence

The bundle includes:

- environment doctor JSON
- public repository safety scan JSON
- release-readiness audit JSON and HTML
- competitor-informed capability matrix JSON and HTML
- competitor coverage JSON and HTML
- policy registry JSON, CSV, and HTML
- DICOM confidentiality alignment JSON and HTML
- built-in profile lint JSON and HTML
- safe DICOM JSON export JSON and HTML from the workflow recipe
- filename privacy scan JSON and HTML from the workflow recipe
- privacy remediation plan JSON and HTML from the workflow recipe
- dcmodify plan JSON, HTML, and review script from the workflow recipe
- Orthanc REST anonymization plan JSON and HTML from the workflow recipe
- DICOM confidentiality alignment JSON and HTML from the workflow recipe
- profile conformance JSON and HTML from the workflow recipe and demo
- pixel risk scan JSON and HTML from the workflow recipe
- one-command synthetic demo output
- demo summary HTML with synthetic PNG previews
- before/after de-identification comparison JSON and HTML
- pixel review HTML with original, overlay, and redacted previews
- encrypted sharing package from anonymized synthetic DICOM files
- package verification receipt HTML
- share-readiness JSON and HTML gate
- de-identification certificate JSON and HTML
- workflow quality gate JSON and HTML
- residual privacy risk score JSON and HTML from the workflow recipe
- tamper-evident demo audit chain
- YAML workflow JSON and HTML report
- static review dashboard JSON and HTML
- evidence bundle JSON and HTML index

## Output Structure

```text
evidence-run/
  reports/
    doctor.json
    safety-scan.json
    release-audit.json
    release-audit.html
    capability-matrix.json
    capability-matrix.html
    competitor-coverage.json
    competitor-coverage.html
    policy-registry.json
    policy-registry.csv
    policy-registry.html
    confidentiality-alignment.json
    confidentiality-alignment.html
    profile-lint-dental-basic.html
    profile-lint-dental-research-sharing.html
    workflow-run.json
    workflow-run.html
    review-dashboard.json
    review-dashboard.html
    evidence-bundle.json
    evidence-bundle.html
  demo-run/
    reports/demo-summary.html
    reports/deid-comparison.html
    reports/confidentiality-alignment.html
    reports/profile-conformance.html
    reports/deid-certificate.html
    reports/share-readiness.html
    reports/quality-gate.html
    reports/pixel-review.html
    reports/pixel-review/pixel-review-overlay.png
    reports/audit-chain.json
    reports/package-receipt.html
    share/package.ddpt
    share/package.key
  workflow-run/
    input/sample.synthetic.dcm
    outputs/sample.anonymized.dcm
    outputs/sample.redacted.dcm
    reports/
      filename-privacy.html
      dicom-json.html
      remediation-plan.html
      confidentiality-alignment.html
      dcmodify-plan.html
      dcmodify-plan.sh
      orthanc-plan.html
      profile-conformance.html
      pixel-risk.html
      residual-risk.html
    share/
```

Open the index:

```bash
open evidence-run/reports/evidence-bundle.html
open evidence-run/reports/review-dashboard.html
```

## Why This Matters

Many DICOM tools can anonymize files, modify tags, or run server-side workflows.
This evidence bundle focuses on public demonstration value:

- a new user can validate the project locally
- reviewers can inspect human-readable reports
- non-programmer collaborators can start from one dashboard page
- CI can exercise the same proof path
- GitHub visitors can understand the workflow without real patient data
- collaborators can see environment, safety, release, workflow, audit, and package
  evidence together

## Safety Notes

`evidence-run/` and `evidence-*/` are ignored by Git. They may contain generated
DICOM, encryption keys, and package files from synthetic examples. Do not commit
evidence bundle output unless you intentionally curate a safe public sample.
