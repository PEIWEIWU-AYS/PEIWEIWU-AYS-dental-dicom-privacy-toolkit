# Dental DICOM Privacy Toolkit

An open-source toolkit for dental DICOM anonymization, encryption, audit reporting, and privacy-preserving image sharing.

This project is designed for public code, synthetic examples, documentation, and reproducible demonstrations. Do not commit real patient data, radiographs, DICOM files, clinical photographs, consent forms, clinic exports, or private manuscript drafts.

## Purpose

The toolkit explores practical privacy controls for dental imaging workflows.

Core goals:

- DICOM metadata inspection
- DICOM anonymization profiles for dental imaging
- Encrypted sharing package prototypes
- Audit reports for de-identification and transfer events
- Synthetic examples for safe testing

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
