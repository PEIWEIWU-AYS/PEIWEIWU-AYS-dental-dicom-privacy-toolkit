# De-identification Comparison | 脱敏前后对比报告

`ddpt compare deid` compares an original DICOM file with an anonymized DICOM
file and produces a side-by-side privacy policy report.

`ddpt compare deid` 用来比较原始 DICOM 和脱敏后的 DICOM，生成“哪些字段已替换、
哪些字段已清空、哪些 UID 已重建、是否仍有残留风险”的前后对比报告。

## Command

```bash
ddpt compare deid \
  demo-run/input/sample.synthetic.dcm \
  demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/deid-comparison.json \
  --html demo-run/reports/deid-comparison.html
```

## What It Checks

The comparison report focuses on high-risk and medium-risk policy items from the
project's DICOM privacy policy registry:

- direct identifiers such as `PatientName`, `PatientID`, and birth date
- contact details and alternate patient identifiers
- clinician, institution, device, workflow, and free-text metadata
- study, series, acquisition, and content dates/times
- UID values that should be regenerated
- private tag count before and after
- PixelData SHA-256 before and after

## Output

The command can write:

- terminal table
- JSON report
- HTML report

The HTML report is intended for non-programmer review and paper/project
evidence. It explains whether each policy item passed, changed, was removed, or
remained unchanged.

## Workflow Integration

The one-command demo and YAML workflow both generate:

```text
reports/deid-comparison.json
reports/deid-comparison.html
```

The evidence bundle includes the HTML comparison report as a core artifact.

## Safety Notes

Passing this comparison means the configured synthetic workflow changed or
removed the tracked policy items. It does not prove complete de-identification,
legal compliance, regulatory approval, or pixel-level safety. Burned-in pixel
identifiers still require pixel review and redaction workflows.
