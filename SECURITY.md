# Security Policy | 安全政策

Dental DICOM Privacy Toolkit is a local-first, synthetic-data-only project. It
handles privacy workflow evidence for demonstrations, but it is not a certified
security product.

## Supported Versions

The public repository currently supports the `main` branch before the first
stable release.

## Reporting a Vulnerability

Please do not open a public issue with exploitable details or real patient data.

If you find a vulnerability:

1. Create a minimal synthetic reproduction when possible.
2. Describe the affected command, module, or report.
3. Include the local environment and version.
4. Avoid real DICOM, screenshots, clinic exports, tokens, passwords, private
   URLs, or patient identifiers.

If private reporting is not yet available on GitHub, open a public issue with a
high-level description only, then coordinate details after a maintainer responds.

## Scope

In scope:

- unsafe file handling in local CLI/API workflows
- path traversal or archive extraction risks
- accidental inclusion of generated private material in public outputs
- incorrect public repository safety checks
- privacy evidence reports that expose values intended to be redacted

Out of scope:

- clinical diagnosis or treatment guidance
- compliance certification
- vulnerabilities requiring real patient data to demonstrate
- attacks against third-party systems not controlled by this project

## Safety Boundary

Never attach real patient DICOM, CBCT, radiographs, photos, consent forms,
spreadsheets, PDFs, or clinic exports to a report.
