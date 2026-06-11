# Profile Lint | 匿名化配置体检

`ddpt profile lint` checks an anonymization profile before it is used in an
anonymization workflow.

`ddpt profile lint` 用于在运行脱敏流程之前检查匿名化 profile 配置是否合理。

## Command

```bash
ddpt profile lint dental-basic \
  --json reports/profile-lint.json \
  --html reports/profile-lint.html
```

For a custom YAML profile:

```bash
ddpt profile lint profiles/my-dental-profile.yml
```

## What It Checks

The lint report checks:

- profile YAML is a mapping
- `replace` is a keyword-to-value mapping
- `blank` and `regenerate_uids` are keyword lists
- `date_shift.offset_days` is an integer
- `date_shift.keywords` are normally date keywords
- keywords are recognized DICOM keywords
- a keyword does not appear in multiple conflicting actions
- `remove_private_tags` is boolean
- private tag retention is called out as a warning
- high-risk and medium-risk policy coverage is reported

## Outputs

JSON output is useful for CI and scripts:

```bash
ddpt profile lint dental-research-sharing --json reports/research-profile-lint.json
```

HTML output is useful for method review:

```bash
ddpt profile lint dental-research-sharing --html reports/research-profile-lint.html
```

The command exits with status `0` when no errors are found and non-zero when
errors exist. Warnings do not fail the command, but they should be reviewed.

## Safety Notes

Profile lint checks configuration quality. It does not inspect a DICOM file,
detect all burned-in identifiers, prove legal compliance, or certify that a real
dataset is safe to share.
