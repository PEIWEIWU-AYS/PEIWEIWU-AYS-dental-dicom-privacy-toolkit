# Linkable Research Profile | 可链接研究伪名化配置

`dental-linkable-research` is a configurable anonymization profile for synthetic
dental imaging studies where the same subject should remain linkable across
multiple DICOM files without exposing the original `PatientName` or `PatientID`.

`dental-linkable-research` 是面向合成牙科影像研究演示的伪名化配置。它允许同一
患者在多次影像检查中保持同一个研究用伪名，同时不暴露原始姓名和原始患者编号。

## Why Linkable Pseudonyms

One-time anonymization is useful for public demos, but research workflows often
need longitudinal linkage. For example, a collaborator may need to know that two
synthetic CBCT or radiograph files belong to the same research subject without
seeing the clinic's original patient identifier.

This profile creates deterministic pseudonyms from a configured source keyword.
That behavior is deterministic pseudonymization: the same source identifier maps
to the same synthetic research identifier.
The built-in profile uses `PatientID` as the source and writes:

- `PatientName`: `ANONYMIZED^<HASH>`
- `PatientID`: `DDPT-LINK-<HASH>`

The same input `PatientID` gets the same pseudonym. A different input
`PatientID` gets a different pseudonym.

## Profile Behavior

The built-in profile:

- pseudonymizes `PatientName` and `PatientID` from the original `PatientID`
- replaces accession, study, series, and institution text with synthetic values
- blanks direct identifiers, clinician names, device/station fields, protocol
  text, and study/series/acquisition/content times
- shifts `StudyDate`, `SeriesDate`, `AcquisitionDate`, and `ContentDate` by
  `-3650` days
- regenerates `StudyInstanceUID`, `SeriesInstanceUID`, `SOPInstanceUID`, and
  `FrameOfReferenceUID`
- removes private tags by default

## Commands

Inspect the profile:

```bash
ddpt profile show dental-linkable-research --json reports/linkable-profile.json
```

Lint the profile before use:

```bash
ddpt profile lint dental-linkable-research \
  --json reports/linkable-profile-lint.json \
  --html reports/linkable-profile-lint.html
```

Preview changes without writing DICOM:

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --profile dental-linkable-research \
  --dry-run \
  --audit demo-run/reports/linkable-dry-run.json \
  --html demo-run/reports/linkable-dry-run.html
```

Write a linkable research copy:

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --profile dental-linkable-research \
  --out demo-run/outputs/sample.linkable-research.dcm \
  --audit demo-run/reports/linkable-audit.json \
  --html demo-run/reports/linkable-audit.html
```

Check policy coverage and compare with the default profile:

```bash
ddpt profile coverage dental-linkable-research
ddpt profile compare dental-basic dental-linkable-research \
  --json demo-run/reports/linkable-profile-comparison.json \
  --html demo-run/reports/linkable-profile-comparison.html
```

## YAML Shape

Custom profiles can use the `pseudonymize` action:

```yaml
pseudonymize:
  PatientID:
    source: PatientID
    prefix: DDPT-LINK-
    length: 12
    namespace: local-research-demo-v1
```

Supported options:

- `source`: DICOM keyword used to derive the pseudonym
- `prefix`: visible prefix written before the hash fragment
- `length`: hash fragment length from 6 to 48 characters
- `namespace`: deterministic context string for separating projects or demos

## Safety Notes

This is a research-demo privacy control, not a standalone legal or regulatory
guarantee. Public examples must use synthetic DICOM only. Do not commit real
patient identifiers, real salts or secrets, clinic exports, or private linkage
tables to GitHub.
