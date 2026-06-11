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
