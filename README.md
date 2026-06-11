# Dental DICOM Privacy Toolkit | 牙科 DICOM 脱敏加密共享工具包

An open-source toolkit for dental DICOM anonymization, de-identification, encryption, audit reporting, and privacy-preserving dental imaging sharing.

一个面向牙科影像、DICOM 脱敏、医学影像隐私、加密共享、审计报告和患者隐私保护的开源工具包。

**Keywords:** dental DICOM, dental imaging, DICOM anonymization, DICOM de-identification, de-identification certificate, deterministic pseudonymization, local browser workbench, objective completion audit, medical imaging privacy, encrypted DICOM sharing, audit report, radiograph privacy, CBCT, oral radiology, open source healthcare, 牙科DICOM, 牙科影像, DICOM脱敏, DICOM去标识化, 去标识化证明书, DICOM伪名化, 本地工作台, 原始目标完成度审计, 医学影像隐私, 加密共享, 口腔影像, CBCT隐私, 患者隐私保护, 医疗数据安全

This project is designed for public code, synthetic examples, documentation, and reproducible demonstrations. Do not commit real patient data, radiographs, DICOM files, clinical photographs, consent forms, clinic exports, or private manuscript drafts.

## Purpose

The toolkit explores practical privacy controls for dental imaging workflows.

Core goals:

- DICOM metadata inspection
- Directory inventory and privacy risk preflight
- Multi-file synthetic dental study generation
- DICOM anonymization profiles for dental imaging
- Research-sharing profile with deterministic date shifting
- Linkable research profile with deterministic patient pseudonymization
- Profile comparison reports for transparent anonymization configuration review
- Profile lint checks for custom anonymization YAML safety
- DICOM privacy policy registry export in JSON, CSV, and HTML
- Competitor-informed capability matrix with repository evidence
- Objective completion audit against the original competitor-learning goal
- Before/after de-identification comparison reports
- De-identification certificate for synthetic sharing handoff evidence
- Workflow-level certificate generation as the final YAML recipe stage
- Anonymization dry-run previews before writing DICOM files
- PNG pixel previews for workflow review
- Pixel review reports with original, overlay, and redacted PNG previews
- YAML workflow recipes for reproducible staged pipelines
- Local REST API for integration demos
- Local browser workbench for synthetic workflow review
- Static local review dashboard for non-programmer walkthroughs
- Release-readiness audit for public GitHub publishing
- Local evidence bundle for MacBook validation and project demonstrations
- Encrypted sharing package prototypes
- Package verification receipts for receiver-side sharing evidence
- Share-readiness gate before synthetic package handoff
- Audit reports for de-identification and transfer events
- Synthetic examples for safe testing

## Project Blueprint

See [docs/project-blueprint.md](docs/project-blueprint.md) for the full workflow, implementation plan, languages, dependencies, tools, and presentation format.

## Quick Local Demo

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

ddpt doctor
ddpt safety scan .
ddpt release audit . --json release-audit.json --html release-audit.html
ddpt capability matrix --root . --json capability-matrix.json --html capability-matrix.html
ddpt completion audit . --json objective-audit.json --html objective-audit.html
ddpt evidence bundle . --out evidence-run
ddpt dashboard build evidence-run --out evidence-run/reports/review-dashboard.html --json evidence-run/reports/review-dashboard.json
ddpt demo demo-run
ddpt synthetic-study synthetic-study-demo --patients 2 --files-per-patient 2 --json synthetic-study-demo/manifest.json
ddpt workflow run recipes/dental-demo-workflow.yml --root workflow-run --json workflow-run/reports/workflow-run.json --html workflow-run/reports/workflow-run.html
ddpt inventory demo-run/input --json demo-run/reports/inventory.json --csv demo-run/reports/inventory.csv --html demo-run/reports/inventory.html
ddpt anonymize demo-run/input/sample.synthetic.dcm --dry-run --audit demo-run/reports/dry-run-audit.json --html demo-run/reports/dry-run-audit.html
ddpt compare deid demo-run/input/sample.synthetic.dcm demo-run/outputs/sample.anonymized.dcm --json demo-run/reports/deid-comparison.json --html demo-run/reports/deid-comparison.html
ddpt certificate create demo-run --json demo-run/reports/deid-certificate.json --html demo-run/reports/deid-certificate.html
ddpt preview demo-run/input/sample.synthetic.dcm --out demo-run/reports/input-preview.png
ddpt pixel-review demo-run/outputs/sample.anonymized.dcm --out-dir demo-run/reports/pixel-review --plan profiles/dental-pixel-redaction.yml --json demo-run/reports/pixel-review.json --html demo-run/reports/pixel-review.html
ddpt redaction-plan show profiles/dental-pixel-redaction.yml
ddpt tag dump demo-run/input/sample.synthetic.dcm --json demo-run/reports/tag-dump.json
ddpt policy export --json demo-run/reports/policy-registry.json --csv demo-run/reports/policy-registry.csv --html demo-run/reports/policy-registry.html
ddpt profile show dental-basic
ddpt profile show dental-research-sharing
ddpt profile show dental-linkable-research
ddpt profile lint dental-basic --json demo-run/reports/profile-lint.json --html demo-run/reports/profile-lint.html
ddpt profile lint dental-linkable-research --json demo-run/reports/linkable-profile-lint.json --html demo-run/reports/linkable-profile-lint.html
ddpt profile coverage dental-basic
ddpt profile coverage dental-research-sharing
ddpt profile coverage dental-linkable-research
ddpt profile compare dental-basic dental-research-sharing --json demo-run/reports/profile-comparison.json --html demo-run/reports/profile-comparison.html
ddpt profile compare dental-basic dental-linkable-research --json demo-run/reports/linkable-profile-comparison.json --html demo-run/reports/linkable-profile-comparison.html
ddpt share readiness demo-run --json demo-run/reports/share-readiness.json --html demo-run/reports/share-readiness.html
ddpt api serve demo-run --host 127.0.0.1 --port 8765
ddpt profile init profiles/my-dental-profile.yml
ddpt batch demo-run/input --out demo-run/batch-output
ddpt audit verify demo-run/reports/audit-chain.json
```

To inspect the local REST API docs, run this as a separate long-running command:

```bash
ddpt api serve demo-run
```

Then open the local browser workbench:

```text
http://127.0.0.1:8765/workbench
```

The one-command demo writes a synthetic input file, anonymized and pixel-redacted DICOM files, PNG previews, JSON reports, HTML reports, an encrypted package, a verification receipt, and a summary page to `demo-run/`.

`ddpt inventory` is a read-only directory preflight. It counts files, modalities, high-risk tags, medium-risk tags, readable/unreadable DICOMs, patient field presence, and UID hashes without exporting raw patient names or IDs.

See [docs/inventory.md](docs/inventory.md) for the inventory safety boundary and output formats.
See [docs/synthetic-study.md](docs/synthetic-study.md) for multi-file synthetic dental study generation.
See [docs/preview.md](docs/preview.md) for PNG preview behavior and safety limits.
See [docs/pixel-review.md](docs/pixel-review.md) for burned-in annotation region review reports.

See [docs/demo-guide.md](docs/demo-guide.md) for MacBook validation steps and expected outputs.
See [docs/workflow-recipes.md](docs/workflow-recipes.md) for recipe-driven staged pipelines.
See [docs/anonymization-dry-run.md](docs/anonymization-dry-run.md) for pre-write anonymization previews.
See [docs/research-sharing-profile.md](docs/research-sharing-profile.md) for deterministic date-shift research sharing.
See [docs/linkable-research-profile.md](docs/linkable-research-profile.md) for deterministic patient pseudonymization in longitudinal research demos.
See [docs/profile-lint.md](docs/profile-lint.md) for anonymization profile configuration checks.
See [docs/profile-comparison.md](docs/profile-comparison.md) for anonymization profile comparison reports.
See [docs/policy-registry.md](docs/policy-registry.md) for the DICOM privacy policy registry export.
See [docs/deid-comparison.md](docs/deid-comparison.md) for before/after de-identification comparison reports.
See [docs/deid-certificate.md](docs/deid-certificate.md) for the synthetic de-identification certificate.
See [docs/capability-matrix.md](docs/capability-matrix.md) for competitor-informed capability evidence.
See [docs/objective-completion-audit.md](docs/objective-completion-audit.md) for requirement-level evidence against the original goal.
See [docs/macbook-validation.md](docs/macbook-validation.md) for a local acceptance checklist.
See [docs/safety-scan.md](docs/safety-scan.md) for public repository safety checks.
See [docs/release-audit.md](docs/release-audit.md) for public release readiness checks.
See [docs/evidence-bundle.md](docs/evidence-bundle.md) for one-command local evidence generation.
See [docs/review-dashboard.md](docs/review-dashboard.md) for the static local review dashboard.
See [docs/package-verification-receipts.md](docs/package-verification-receipts.md) for receiver-side sharing receipts.
See [docs/share-readiness.md](docs/share-readiness.md) for the final synthetic sharing gate.
See [docs/local-api.md](docs/local-api.md) for the local REST API demo.
See [docs/local-workbench.md](docs/local-workbench.md) for the local browser workbench.

## Manual Step-by-Step Demo

```bash
ddpt synthetic demo-run/sample.dcm
ddpt inventory demo-run --json demo-run/reports/inventory.json --csv demo-run/reports/inventory.csv --html demo-run/reports/inventory.html
ddpt preview demo-run/sample.dcm --out demo-run/reports/sample-preview.png --json demo-run/reports/sample-preview.json
ddpt tag set demo-run/sample.dcm PatientName ANON^TEST --out demo-run/outputs/sample.tag-set.dcm --audit demo-run/reports/tag-set-audit.json
ddpt inspect demo-run/sample.dcm --json demo-run/reports/inspect.json --html demo-run/reports/inspect.html
ddpt anonymize demo-run/sample.dcm --dry-run --audit demo-run/reports/dry-run-audit.json --html demo-run/reports/dry-run-audit.html
ddpt anonymize demo-run/sample.dcm --out demo-run/outputs/sample.anonymized.dcm --audit demo-run/reports/audit.json --html demo-run/reports/audit.html
ddpt validate demo-run/outputs/sample.anonymized.dcm --json demo-run/reports/validation.json
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm --rect 1,0,1,1 --out demo-run/outputs/sample.redacted.dcm --audit demo-run/reports/redaction.json
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm --plan profiles/dental-pixel-redaction.yml --out demo-run/outputs/sample.plan-redacted.dcm --audit demo-run/reports/plan-redaction.json
ddpt package demo-run/outputs --encrypt --key-out demo-run/share/package.key --manifest demo-run/share/manifest.json --out demo-run/share/package.ddpt
ddpt verify demo-run/share/package.ddpt --key demo-run/share/package.key --receipt demo-run/reports/package-receipt.json --html demo-run/reports/package-receipt.html
ddpt certificate create demo-run --json demo-run/reports/deid-certificate.json --html demo-run/reports/deid-certificate.html
ddpt share readiness demo-run --json demo-run/reports/share-readiness.json --html demo-run/reports/share-readiness.html
ddpt decrypt demo-run/share/package.ddpt --key demo-run/share/package.key --out demo-run/restored
```

## Suggested GitHub Topics

`dicom` `dental-imaging` `medical-imaging` `dicom-anonymization` `de-identification` `pseudonymization` `local-first` `web-ui` `privacy` `encryption` `audit-report` `cbct` `oral-radiology` `dentistry` `open-source-healthcare`

## Repository Structure

```text
src/                    Shared source code
dicom-anonymizer/       De-identification logic and profiles
dicom-encryption/       Encryption and packaging prototypes
dicom-sharing/          Sharing workflow and access-control prototypes
docs/                   Public project documentation
examples/synthetic-dicom/ Synthetic DICOM examples only
synthetic-data/         Synthetic demo metadata only
scripts/                Development and validation scripts
tests/                  Automated tests
```

## Safety Boundary

This is a public repository. Use synthetic files only.

Sensitive local materials should stay outside the repository, for example:

```text
/Users/pengqian/Desktop/GitHub-PEIWEIWU-AYS/teledentistry-private-data_DO_NOT_UPLOAD
```

## Status

Version 0.1 local prototype in active development. The current workflow supports
synthetic-data DICOM inspection, anonymization, validation, pixel redaction,
encrypted packaging, audit chains, YAML workflow recipes, local REST API demos,
local browser workbench, research-sharing date shifting, linkable research pseudonymization,
objective completion audit, release-readiness checks, and local evidence bundle generation,
package verification receipts, profile comparison reports,
profile lint checks, policy registry exports, capability matrix reports, static
review dashboards, de-identification comparison reports, de-identification
certificates, and pixel review reports, plus share-readiness gates.

## License

MIT License.
