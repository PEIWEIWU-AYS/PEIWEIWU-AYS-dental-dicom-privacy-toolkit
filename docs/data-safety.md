# Data Safety

This repository is public. Treat anything committed here as visible to the internet.

## Never Commit

- Real DICOM files
- Real radiographs or clinical photographs
- Names, phone numbers, addresses, ID numbers, dates of birth, or medical record numbers
- Signed consent forms
- Clinic management system exports
- Private manuscript drafts

## Allowed

- Synthetic DICOM examples
- Generated demo metadata
- Public documentation
- Code
- Tests
- Schemas

## Pre-Push Guardrail

Run this before publishing or pushing:

```bash
ddpt safety scan .
```

The scan blocks common accidental leaks such as real DICOM files, clinical images, PDFs, spreadsheets, `.env` files, private keys, and suspicious private-data folder names. It is a guardrail, not a legal privacy guarantee.
