# Profile Conformance | 脱敏配置符合性验证

`ddpt profile verify` checks whether an anonymized DICOM file actually conforms
to the selected anonymization profile.

`ddpt profile verify` 用来验证脱敏后的 DICOM 是否真的符合指定 profile。它不是
只检查固定字段，而是按 profile 逐项验证 replace、blank、date shift、
pseudonymize、UID regeneration 和 private tag removal。

## Command

```bash
ddpt profile verify \
  demo-run/input/sample.synthetic.dcm \
  demo-run/outputs/sample.anonymized.dcm \
  --profile dental-basic \
  --json demo-run/reports/profile-conformance.json \
  --html demo-run/reports/profile-conformance.html
```

## What It Checks

The report verifies:

- replacement values match the profile
- blanked fields are blank or absent
- deterministic pseudonyms match the configured source, prefix, namespace, and length
- shifted dates match the configured offset
- regenerated UIDs are valid and different from the source value
- private tags are removed when the profile requires removal

## Workflow Integration

The built-in workflow recipe writes:

```text
workflow-run/reports/profile-conformance.json
workflow-run/reports/profile-conformance.html
```

The workflow quality gate treats profile conformance as required evidence.

## Why This Matters

General validation answers "does this anonymized file look safe enough for the
demo?" Profile conformance answers a stricter question: "did the output follow
the selected configuration?" That is closer to a staged RSNA CTP-style evidence
pipeline and makes custom profile review safer.

## Safety Notes

This report is technical evidence for synthetic or explicitly approved test
DICOM files. It is not clinical, legal, regulatory, or security certification.
Real patient data must stay outside the public repository.
