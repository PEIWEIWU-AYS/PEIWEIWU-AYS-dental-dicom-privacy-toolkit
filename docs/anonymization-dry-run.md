# Anonymization Dry Run | 脱敏预演

`ddpt anonymize --dry-run` previews the metadata changes that an anonymization profile would make without writing a new DICOM file.

`ddpt anonymize --dry-run` 可以在不写出新 DICOM 文件的情况下预览脱敏 profile 将会修改哪些 metadata。

## Example

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --dry-run \
  --audit demo-run/reports/dry-run-audit.json \
  --html demo-run/reports/dry-run-audit.html
```

Expected:

- no output DICOM is written
- JSON and HTML audit files list planned actions
- regenerated UID values are shown as `<generated-uid>` placeholders

## Why It Matters

Dry run mode gives reviewers a safe step before modifying files. It is useful for:

- reviewing profile behavior
- explaining planned changes to non-programmer collaborators
- comparing profiles during method development
- avoiding accidental edits during demos

## Safety Boundary

Dry run mode previews metadata actions only. It does not modify pixel data, detect all burned-in identifiers, prove legal compliance, or certify that a real dataset is safe to share.
