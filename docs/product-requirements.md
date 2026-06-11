# Product Requirements | 产品需求

## Product Goal

Build a local-first, synthetic-data-only toolkit for dental DICOM privacy workflows. The first complete version should let a user run a reproducible demo on a MacBook and produce machine-readable and human-readable evidence that the workflow worked.

## Success Criteria for Version 0.1

Version 0.1 is successful when a new user can:

1. Install the Python package in a virtual environment.
2. Generate a synthetic DICOM file.
3. Run a read-only directory inventory and receive JSON, CSV, and HTML reports.
4. Generate PNG previews for visual workflow review.
5. Inspect metadata and receive JSON plus HTML reports.
6. Apply the `dental-basic` anonymization profile.
7. Confirm direct identifiers were replaced or removed.
8. Generate an audit event JSON file.
9. Validate anonymized output with a pass/fail report.
10. Apply manual pixel redaction for known burned-in annotation regions.
11. Package anonymized files with checksums.
12. Encrypt the package.
13. Verify or decrypt the package.
14. Run automated tests locally and in GitHub Actions.

### `ddpt demo`

Run the complete synthetic privacy workflow in one command.

Required:

- synthetic DICOM generation
- read-only directory inventory
- PNG previews
- metadata inspection
- anonymization
- validation
- manual pixel redaction
- encrypted package creation
- package verification
- JSON reports
- HTML reports
- summary HTML page

### `ddpt inventory`

Run a read-only preflight scan before anonymization or batch processing.

Required:

- recursive DICOM discovery
- readable and unreadable file counts
- modality counts
- high-risk and medium-risk tag counts
- patient field presence flags without exporting raw patient names or IDs
- UID hashes rather than raw UID values
- JSON output
- CSV output
- optional HTML report

### `ddpt batch`

Run directory-level inspection, anonymization, validation, and summary reporting.

Required:

- recursive DICOM discovery
- per-file inspection JSON
- per-file anonymization audit JSON
- per-file validation JSON
- anonymized DICOM output directory
- batch summary JSON
- batch summary HTML
- non-zero exit status when failures occur

### `ddpt audit chain/verify`

Create and verify a tamper-evident hash chain for generated artifacts.

Required:

- deterministic file ordering
- SHA-256 for each file
- previous hash and chain hash per entry
- root hash
- default exclusion for key files
- verification command with non-zero exit status on mismatch

### `ddpt profile list/show`

Expose anonymization profile behavior so users can see what the toolkit will change.

Required:

- list built-in profiles
- show replacement keywords
- show blanking keywords
- show UID regeneration keywords
- show private tag policy
- optional JSON export

### `ddpt profile init`

Create a user-editable YAML profile from the built-in dental baseline.

Required:

- write profile YAML
- refuse to overwrite by default
- support explicit overwrite
- generated profile must be usable with `ddpt anonymize --profile`

### `ddpt profile coverage`

Compare an anonymization profile against the toolkit's high-risk and medium-risk policy registry.

Required:

- structured policy registry
- high-risk coverage count
- medium-risk coverage count
- uncovered high-risk keyword list
- uncovered medium-risk keyword list
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

### `ddpt preview`

Render DICOM pixel data to a PNG preview for workflow review.

Required outputs:

- PNG preview image
- optional JSON metadata report
- image dimensions
- rendered preview dimensions
- pixel value range
- warning that previews are not diagnostic images

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
