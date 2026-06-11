# Dental DICOM Privacy Toolkit | 牙科 DICOM 脱敏加密共享工具包

An open-source toolkit for dental DICOM anonymization, de-identification, encryption, audit reporting, and privacy-preserving dental imaging sharing.

一个面向牙科影像、DICOM 脱敏、医学影像隐私、加密共享、审计报告和患者隐私保护的开源工具包。

**Keywords:** dental DICOM, dental imaging, DICOM anonymization, DICOM de-identification, medical imaging privacy, encrypted DICOM sharing, audit report, radiograph privacy, CBCT, oral radiology, open source healthcare, 牙科DICOM, 牙科影像, DICOM脱敏, 医学影像隐私, 加密共享, 口腔影像, CBCT隐私, 患者隐私保护, 医疗数据安全

This project is designed for public code, synthetic examples, documentation, and reproducible demonstrations. Do not commit real patient data, radiographs, DICOM files, clinical photographs, consent forms, clinic exports, or private manuscript drafts.

## Purpose

The toolkit explores practical privacy controls for dental imaging workflows.

Core goals:

- DICOM metadata inspection
- DICOM anonymization profiles for dental imaging
- Encrypted sharing package prototypes
- Audit reports for de-identification and transfer events
- Synthetic examples for safe testing

## Project Blueprint

See [docs/project-blueprint.md](docs/project-blueprint.md) for the full workflow, implementation plan, languages, dependencies, tools, and presentation format.

## Quick Local Demo

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

ddpt demo demo-run
ddpt profile show dental-basic
ddpt profile coverage dental-basic
ddpt profile init profiles/my-dental-profile.yml
```

The one-command demo writes a synthetic input file, anonymized and pixel-redacted DICOM files, JSON reports, HTML reports, an encrypted package, and a summary page to `demo-run/`.

## Manual Step-by-Step Demo

```bash
ddpt synthetic demo-run/sample.dcm
ddpt inspect demo-run/sample.dcm --json demo-run/reports/inspect.json --html demo-run/reports/inspect.html
ddpt anonymize demo-run/sample.dcm --out demo-run/outputs/sample.anonymized.dcm --audit demo-run/reports/audit.json --html demo-run/reports/audit.html
ddpt validate demo-run/outputs/sample.anonymized.dcm --json demo-run/reports/validation.json
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm --rect 1,0,1,1 --out demo-run/outputs/sample.redacted.dcm --audit demo-run/reports/redaction.json
ddpt package demo-run/outputs --encrypt --key-out demo-run/share/package.key --manifest demo-run/share/manifest.json --out demo-run/share/package.ddpt
ddpt verify demo-run/share/package.ddpt --key demo-run/share/package.key
```

## Suggested GitHub Topics

`dicom` `dental-imaging` `medical-imaging` `dicom-anonymization` `de-identification` `privacy` `encryption` `audit-report` `cbct` `oral-radiology` `dentistry` `open-source-healthcare`

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

Initial project skeleton.

## License

MIT License.
