# dcmodify Plan Export | dcmodify 操作计划导出

`ddpt dcmodify plan` converts a DDPT anonymization profile into a review-only
DCMTK `dcmodify`-style operation plan.

`ddpt dcmodify plan` 可以把 DDPT 的匿名化 profile 转换成仅供审阅的 DCMTK
`dcmodify` 风格操作计划。

## Command

```bash
ddpt dcmodify plan demo-run/input/sample.synthetic.dcm \
  --profile dental-basic \
  --json demo-run/reports/dcmodify-plan.json \
  --html demo-run/reports/dcmodify-plan.html \
  --script demo-run/reports/dcmodify-plan.sh
```

The built-in workflow recipe also writes:

```text
workflow-run/reports/dcmodify-plan.json
workflow-run/reports/dcmodify-plan.html
workflow-run/reports/dcmodify-plan.sh
```

## What It Shows

The plan lists:

- DICOM keyword and tag for each planned profile action
- profile action such as `replace`, `blank`, `date_shift`, or `regenerate_uid`
- matching `dcmodify` option or command style
- safe replacement value preview where applicable
- private-tag erase step when the selected profile removes private tags
- a shell script preview for expert review

## Why This Matters

DCMTK `dcmodify` is powerful because expert users can modify, insert, or delete
specific DICOM tags. This project keeps that lesson, but adds a safer layer:
profile decisions are exported into a human-readable plan before anyone changes
a file.

DCMTK `dcmodify` 的价值在于精确、底层、可复现的 tag 操作。本项目保留这个优点，
但把它放进更安全的审阅流程：先由 profile 生成计划和报告，再由专家决定是否在副本上
手动执行。

## Safety Notes

This command does not execute DCMTK and does not require DCMTK to be installed.
The generated script is for review. If a user chooses to run it manually,
they should run it only on copies of synthetic or approved test DICOM files,
because `dcmodify` edits files in place.
