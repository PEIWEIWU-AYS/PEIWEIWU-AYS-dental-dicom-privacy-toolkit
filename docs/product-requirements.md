# Product Requirements | 产品需求

## Product Goal

Build a local-first, synthetic-data-only toolkit for dental DICOM privacy workflows. The first complete version should let a user run a reproducible demo on a MacBook and produce machine-readable and human-readable evidence that the workflow worked.

## Success Criteria for Version 0.1

Version 0.1 is successful when a new user can:

1. Install the Python package in a virtual environment.
2. Run `ddpt doctor` to confirm the local environment is ready.
3. Run `ddpt safety scan` to confirm the public repository has no obvious private clinical material.
4. Generate a synthetic DICOM file.
5. Run a YAML recipe as a reproducible multi-stage workflow.
6. Run a read-only directory inventory and receive JSON, CSV, and HTML reports.
7. Generate PNG previews for visual workflow review.
8. Run exact tag dump/set/blank/delete operations for expert workflows.
9. Inspect metadata and receive JSON plus HTML reports.
10. Preview anonymization actions with dry-run mode.
11. Apply the `dental-basic` anonymization profile.
12. Confirm direct identifiers were replaced or removed.
13. Generate an audit event JSON file.
14. Validate anonymized output with a pass/fail report.
15. Apply manual or plan-based pixel redaction for known burned-in annotation regions.
16. Package anonymized files with checksums.
17. Encrypt the package.
18. Verify or decrypt the package.
19. Run local REST API workflow demos for integration testing.
20. Run a release-readiness audit before public GitHub publishing.
21. Generate a local evidence bundle for MacBook validation and public demonstrations.
22. Run automated tests locally and in GitHub Actions.

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

### `ddpt doctor`

Check whether the local environment can run the toolkit.

Required:

- Python version check
- runtime dependency import checks
- package version
- platform summary
- terminal pass/fail output
- optional JSON export

### `ddpt safety scan`

Scan the public repository for common accidental private-data leaks before pushing.

Required:

- block real DICOM extensions outside clearly synthetic examples
- block clinical image/document/spreadsheet/archive extensions
- block `.env`, private key, and certificate files
- flag dangerous directory names such as `private`, `patient-data`, `real-data`, `clinic-exports`, and `raw-dicom`
- ignore generated local demo directories and Python/Node caches
- optional JSON export
- non-zero exit status when findings are present

### `ddpt release audit`

Audit whether the local repository is ready for a public GitHub milestone.

Required:

- required repository files check
- bilingual README and keyword discoverability check
- core CLI command documentation check
- competitor-learning documentation check
- source module presence check
- Python package metadata and dependency check
- GitHub Actions gate check
- YAML workflow recipe coverage check
- `dental-basic` privacy profile coverage check
- public repository safety scan check
- JSON output
- optional HTML report
- non-zero exit status when any release-readiness check fails

### `ddpt evidence bundle`

Generate a local evidence bundle for reviewers and collaborators.

Required:

- environment doctor JSON
- public repository safety scan JSON
- release-readiness audit JSON and HTML
- one-command synthetic demo artifacts
- YAML workflow JSON and HTML reports
- evidence index JSON and HTML
- links to demo summary, audit chain, encrypted package, and workflow report
- non-zero exit status when any major evidence gate fails
- documentation that generated evidence output must not be committed by default

### `ddpt workflow run`

Run a YAML recipe as a reproducible multi-stage privacy workflow.

Required:

- workflow recipe YAML
- root output directory
- structured JSON workflow report
- human-readable HTML workflow report
- step-level pass/fail status
- artifacts list per step
- non-zero exit status when any step fails
- support synthetic, inventory, inspect, anonymize, validate, preview, pixel redaction, package, package verification, audit chain, and audit chain verification stages

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

### `ddpt tag dump/set/blank/delete`

Perform exact low-level DICOM metadata operations for expert workflows.

Required:

- dump metadata tags with optional JSON output
- exclude PixelData from dump by default
- set existing tags
- insert missing dictionary tags
- support explicit VR for unknown or private tags
- blank existing tags
- delete tags
- accept both DICOM keywords and hex tags such as `0010,0010`
- audit JSON output for write operations

### `ddpt api serve`

Run a local REST API demo for synthetic-data workflows.

Required:

- local-only FastAPI app
- `/health` endpoint
- inventory endpoint
- inspect endpoint
- anonymize endpoint
- validate endpoint
- preview endpoint
- path traversal protection
- documentation that this is not a production PACS, DICOMweb server, or clinical viewer

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
- output DICOM unless dry-run mode is used
- profile name
- audit JSON output
- optional HTML report
- dry-run mode that writes no DICOM file
- dry-run planned UID changes represented as placeholders

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
- optional YAML redaction plan
- percent-based reusable regions
- output DICOM
- audit JSON output
- bounds checking
- documentation that this does not automatically find all burned-in identifiers

### `ddpt redaction-plan init/show`

Create and inspect reusable pixel redaction plans.

Required:

- YAML template generation
- refuse to overwrite by default
- show plan regions in terminal
- optional JSON export
- support `pixels` and `percent` coordinate units

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
- FastAPI and Uvicorn for the local API demo.
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
- a release-readiness audit command with JSON and HTML outputs
- a local evidence bundle command with JSON and HTML index outputs
- README demo commands updated
- CI passing locally or documented if remote CI is not available
