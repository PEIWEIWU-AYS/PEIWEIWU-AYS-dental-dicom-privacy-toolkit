# Profile Comparison | 匿名化配置对比

`ddpt profile compare` compares two anonymization profiles against the toolkit's
high-risk and medium-risk dental privacy policy registry.

`ddpt profile compare` 可以基于项目内置的高风险和中风险牙科隐私策略表，对比两个匿名化
profile 的处理差异。

## Command

```bash
ddpt profile compare dental-basic dental-research-sharing \
  --json reports/profile-comparison.json \
  --html reports/profile-comparison.html
```

## What It Shows

The comparison report includes:

- baseline profile name
- candidate profile name
- total policy items compared
- changed item count
- coverage count for each profile
- high-risk and medium-risk uncovered keywords for each profile
- per-keyword baseline action
- per-keyword candidate action
- notes explaining important differences such as date shifting

## Why This Matters

Configurable anonymization is only useful when reviewers can understand what a
configuration changes. A profile comparison report helps:

- explain why `dental-research-sharing` shifts dates while `dental-basic` blanks them
- review custom YAML profiles before using them in a workflow
- show collaborators a transparent profile diff
- turn configuration decisions into JSON and HTML evidence

## Safety Notes

Profile comparison explains metadata handling plans. It does not inspect pixel
data, prove legal compliance, or certify that a real dataset is safe to share.
Use it with dry-run reports, validation, inventory, safety scan, and package
verification receipts.
