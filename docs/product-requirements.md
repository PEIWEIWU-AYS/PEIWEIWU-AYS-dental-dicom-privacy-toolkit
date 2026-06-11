# Product Requirements | 产品需求

## Product Goal

Build a local-first, synthetic-data-only toolkit for dental DICOM privacy workflows. The first complete version should let a user run a reproducible demo on a MacBook and produce machine-readable and human-readable evidence that the workflow worked.

## Success Criteria for Version 0.1

Version 0.1 is successful when a new user can:

1. Install the Python package in a virtual environment.
2. Generate a synthetic DICOM file.
3. Inspect metadata and receive JSON plus HTML reports.
4. Apply the `dental-basic` anonymization profile.
5. Confirm direct identifiers were replaced or removed.
6. Generate an audit event JSON file.
7. Validate anonymized output with a pass/fail report.
8. Apply manual pixel redaction for known burned-in annotation regions.
9. Package anonymized files with checksums.
10. Encrypt the package.
11. Verify or decrypt the package.
12. Run automated tests locally and in GitHub Actions.

### `ddpt demo`

Run the complete synthetic privacy workflow in one command.

Required:

- synthetic DICOM generation
- metadata inspection
- anonymization
- validation
- manual pixel redaction
- encrypted package creation
- package verification
- JSON reports
- HTML reports
- summary HTML page

### `ddpt profile list/show`

Expose anonymization profile behavior so users can see what the toolkit will change.

Required:

- list built-in profiles
- show replacement keywords
- show blanking keywords
- show UID regeneration keywords
- show private tag policy
- optional JSON export

## Command Requirements

The CLI command is `ddpt`.

### `ddpt synthetic`

Generate a synthetic DICOM fixture.

Required:

- output path
- synthetic patient name
- synthetic patient ID
- modality
- study description

### `ddpt inspect`

Inspect a DICOM file and classify metadata privacy risk.

Required outputs:

- terminal summary
- JSON report
- optional HTML report

### `ddpt anonymize`

Apply a named anonymization profile.

Required:

- input DICOM
- output DICOM
- profile name
- audit JSON output
- optional HTML report

### `ddpt package`

Create a sharing package from anonymized files.

Required:

- manifest JSON
- SHA-256 checksums
- ZIP package
- optional Fernet encryption
- optional key output

### `ddpt redact-pixels`

Apply manual rectangular pixel redaction for known burned-in annotation regions.

Required:

- one or more `x,y,width,height` rectangles
- output DICOM
- audit JSON output
- bounds checking
- documentation that this does not automatically find all burned-in identifiers

### `ddpt verify`

Verify a package manifest and checksums.

Required:

- support encrypted package when key is provided
- report pass/fail clearly

### `ddpt validate`

Validate an anonymized DICOM file against the initial dental privacy profile.

Required:

- direct identifier replacement checks
- direct identifier blanking checks
- private tag removal check
- burned-in annotation warning
- JSON report output
- non-zero exit status on failed validation

### `ddpt decrypt`

Decrypt an encrypted package into a local output folder.

Required:

- key input
- safe output directory behavior

## Anonymization Requirements

The initial `dental-basic` profile should:

- replace `PatientName`
- replace `PatientID`
- remove or blank `PatientBirthDate`
- remove or blank `PatientAddress`
- replace accession and study identifiers where appropriate
- remove private tags by default
- preserve enough technical metadata for the synthetic file to remain readable

## Risk Classification Requirements

Risk levels:

- high: direct identifiers and dates
- medium: institution, device, accession, study descriptions, operators
- low: mostly technical fields needed for interpretation
- unknown: unclassified fields

The initial classifier should be transparent and easy to extend.

## Report Requirements

Reports should be useful for both developers and dental/research collaborators.

Required report formats:

- JSON for reproducibility
- HTML for presentation

HTML report sections:

- file summary
- high-risk tags
- medium-risk tags
- anonymization actions
- validation result
- synthetic-only warning

## Safety Requirements

- The project must not require real patient data.
- Tests must use synthetic DICOM files.
- Documentation must warn that de-identification reduces risk but is not a guarantee.
- Burned-in pixel annotations must be called out as a separate risk.
- The repository should continue ignoring real clinical file formats by default.

## Technical Requirements

- Python package under `src/ddpt`.
- `pyproject.toml` with runtime and development dependencies.
- Typer CLI.
- pydicom for DICOM handling.
- cryptography for encryption.
- pytest tests.
- GitHub Actions must run tests.

## Non-Goals for Version 0.1

- No clinical diagnosis.
- No legal compliance guarantee.
- No real patient data processing in examples.
- No production PACS integration.
- No cloud upload.
- No web dashboard until CLI workflow is stable.

## Completion Evidence

To call Version 0.1 complete, we need:

- all required commands implemented
- tests covering synthetic, inspect, anonymize, package, verify, decrypt
- a generated HTML report from synthetic data
- a one-command demo pipeline that generates all core artifacts
- README demo commands updated
- CI passing locally or documented if remote CI is not available
