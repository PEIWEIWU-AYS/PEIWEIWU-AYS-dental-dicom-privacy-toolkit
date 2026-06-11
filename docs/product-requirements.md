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
12. Apply the `dental-research-sharing` profile with deterministic date shifting.
13. Lint anonymization profiles before running workflows.
14. Compare anonymization profiles with JSON and HTML reports.
15. Export the DICOM privacy policy registry as JSON, CSV, and HTML.
16. Generate before/after de-identification comparison reports.
17. Confirm direct identifiers were replaced or removed.
18. Generate an audit event JSON file.
19. Validate anonymized output with a pass/fail report.
20. Generate pixel review reports for known burned-in annotation regions.
21. Apply manual or plan-based pixel redaction for known burned-in annotation regions.
22. Package anonymized files with checksums.
23. Encrypt the package.
24. Verify or decrypt the package.
25. Generate package verification receipts for receiver-side sharing evidence.
26. Run a share-readiness gate before synthetic package handoff.
27. Run local REST API workflow demos for integration testing.
28. Run a release-readiness audit before public GitHub publishing.
29. Run a competitor-informed capability matrix that maps features to repository evidence.
30. Generate a static local review dashboard for non-programmer walkthroughs.
31. Generate a local evidence bundle for MacBook validation and public demonstrations.
32. Run automated tests locally and in GitHub Actions.

### `ddpt demo`

Run the complete synthetic privacy workflow in one command.

Required:

- synthetic DICOM generation
- read-only directory inventory
- PNG previews
- metadata inspection
- anonymization
- before/after de-identification comparison
- validation
- pixel review report
- manual pixel redaction
- encrypted package creation
- package verification
- package verification receipt JSON and HTML
- share-readiness JSON and HTML
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
- links to package verification receipts
- static review dashboard JSON and HTML output
- non-zero exit status when any major evidence gate fails
- documentation that generated evidence output must not be committed by default

### `ddpt capability matrix`

Generate a competitor-informed capability matrix for public project review.

Required:

- cover RSNA DICOM Anonymizer, DicomCleaner, Orthanc, RSNA CTP, DCMTK `dcmodify`, and pydicom anonymization examples
- map inherited capability areas to local repository evidence
- show the project's dental-specific differentiators
- report implemented, partial, and missing capability counts
- JSON output
- optional HTML report
- non-zero exit status when capability evidence is missing

### `ddpt compare deid`

Compare a source DICOM file with an anonymized DICOM file.

Required:

- source DICOM path
- anonymized DICOM path
- terminal pass/fail table
- JSON report
- optional HTML report
- compare high-risk and medium-risk policy items
- show changed, removed, unchanged, added, and absent statuses
- report private tag counts before and after
- report PixelData SHA-256 before and after when present
- non-zero exit status when tracked high-risk or medium-risk policy items remain unsafe

### `ddpt dashboard build`

Build a static local review dashboard from an evidence bundle.

Required:

- evidence bundle directory input
- HTML output
- optional JSON dashboard report
- quick links to core reports
- embedded synthetic PNG previews when available
- artifact availability counts
- non-zero exit status when the evidence bundle index is missing or artifacts are missing
- documentation that this is a static local review aid, not a production PACS or clinical viewer

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
- support synthetic, inventory, inspect, anonymize, validate, preview, pixel redaction, package, package verification, audit chain, audit chain verification, and share-readiness stages
- support before/after de-identification comparison stages

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
- include `dental-basic` and `dental-research-sharing`
- show replacement keywords
- show blanking keywords
- show date-shift keywords and offset days
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

### `ddpt profile lint`

Check anonymization profile configuration quality before running workflows.

Required:

- validate YAML/profile shape
- validate known DICOM keywords
- detect conflicting actions for the same keyword
- validate `date_shift` shape and offset
- warn when private tags are retained
- report high-risk and medium-risk policy coverage
- JSON output
- optional HTML report
- non-zero exit status when errors exist

### `ddpt profile compare`

Compare two anonymization profiles against the high-risk and medium-risk policy registry.

Required:

- baseline and candidate profile arguments
- changed item count
- coverage count for each profile
- per-keyword baseline action
- per-keyword candidate action
- notes for important differences such as deterministic date shifting
- JSON output
- optional HTML report

### `ddpt policy export`

Export the DICOM privacy policy registry for review and documentation.

Required:

- list registry items with keyword, risk, category, recommended action, DICOM code, reason, and source
- count high-risk, medium-risk, and low-risk items
- optional risk filters
- JSON output
- CSV output
- optional HTML report

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

### `ddpt pixel-review`

Generate a visual review report for known pixel redaction regions.

Required outputs:

- original PNG preview
- redaction overlay PNG preview
- redacted PNG preview
- JSON report
- optional HTML report
- support manual rectangles
- support reusable YAML redaction plans
- warnings that pixel review does not automatically detect every burned-in identifier

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

### `ddpt verify`

Verify a package manifest and checksums.

Required:

- support encrypted package when key is provided
- report pass/fail clearly
- optional verification receipt JSON
- optional verification receipt HTML
- non-zero exit status when decryption, manifest, path safety, missing file, or checksum checks fail

### `ddpt share readiness`

Check whether a synthetic demo folder is ready for package handoff.

Required:

- demo or workflow output directory input
- check anonymized DICOM exists
- check validation report passed
- check before/after de-identification comparison passed
- check pixel review report and previews exist
- check encrypted package verification receipt passed
- check audit chain verification passed
- JSON report
- optional HTML report
- non-zero exit status when any readiness check fails
- documentation that this is a local synthetic-data gate, not legal, clinical, or regulatory certification

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

The `dental-research-sharing` profile should:

- keep the direct identifier replacement/blanking baseline
- shift study-level dates deterministically rather than exposing original dates
- preserve relative date intervals for synthetic research demonstrations
- show date-shift actions in dry-run and audit reports
- avoid claiming that date shifting alone guarantees de-identification

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
- No production web dashboard until CLI workflow is stable.
- Static local review dashboards are allowed for synthetic evidence review.

## Completion Evidence

To call Version 0.1 complete, we need:

- all required commands implemented
- tests covering synthetic, inspect, anonymize, package, verify, decrypt
- a generated HTML report from synthetic data
- a one-command demo pipeline that generates all core artifacts
- a release-readiness audit command with JSON and HTML outputs
- a capability matrix command with JSON and HTML outputs
- a before/after de-identification comparison command with JSON and HTML outputs
- a share-readiness command with JSON and HTML outputs
- a static review dashboard command with JSON and HTML outputs
- a local evidence bundle command with JSON and HTML index outputs
- README demo commands updated
- CI passing locally or documented if remote CI is not available
