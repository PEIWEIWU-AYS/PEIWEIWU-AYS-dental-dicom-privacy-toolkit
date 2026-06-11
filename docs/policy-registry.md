# Policy Registry | 风险策略库

The toolkit uses a DICOM PS3.15-inspired dental privacy baseline to classify DICOM metadata and explain recommended actions.

This is not a claim of regulatory certification or complete DICOM conformance. It is a transparent, testable baseline for dental imaging privacy workflows.

## Fields

Each policy item includes:

- `keyword`: DICOM keyword, such as `PatientName`.
- `risk`: `high`, `medium`, `low`, or `unknown`.
- `category`: why the element matters, such as `direct-identifier`, `date`, `uid`, `free-text`, `device`, or `technical`.
- `recommended_action`: toolkit-level action, such as `replace`, `blank`, `regenerate_uid`, `retain`, or `review`.
- `dicom_action_code`: DICOM confidentiality-profile-inspired action code.
- `reason`: human-readable explanation.

## DICOM Action Code Notes

The policy registry uses short DICOM-inspired action codes for explainability:

- `D`: replace with a non-identifying dummy value.
- `Z`: zero-length or blank value.
- `X`: remove.
- `U`: replace UID.
- `K`: keep.
- `C`: clean or sanitize when free text may contain identifiers.

## Coverage

Use:

```bash
ddpt profile coverage dental-basic
```

This compares the `dental-basic` profile against high-risk and medium-risk registry items. A strong profile should cover all high-risk items and clearly explain any uncovered medium-risk items.

## Safety

Metadata policy coverage does not prove that a DICOM file is fully de-identified. Pixel data, burned-in annotations, rare private tags, external filenames, clinical context, and longitudinal uniqueness can still create re-identification risk.

## Reference

- DICOM Attribute Confidentiality Profiles: https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_e.html
