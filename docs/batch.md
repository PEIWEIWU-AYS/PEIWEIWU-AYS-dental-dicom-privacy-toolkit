# Batch De-identification Evidence | 批量脱敏证据

`ddpt batch` processes a directory of synthetic or approved test DICOM files and
writes per-file evidence for inspection, anonymization, validation, and
before/after de-identification comparison.

`ddpt batch` 用于批量处理合成或已明确批准的测试 DICOM 文件，并为每个文件生成
检查、脱敏、验证和脱敏前后对比证据。

## Command

```bash
ddpt batch synthetic-study-demo \
  --out synthetic-study-demo-batch \
  --profile dental-linkable-research
```

## Outputs

The command writes:

- anonymized DICOM files under `dicom/`
- per-file inspection JSON under `reports/`
- per-file anonymization audit JSON under `reports/`
- per-file validation JSON under `reports/`
- per-file de-identification comparison JSON under `reports/`
- `batch-summary.json`
- `batch-summary.html`

## Why This Matters

Single-file demos are useful, but research and clinic workflows often involve
folders, repeated studies, and repeated patients. Batch de-identification
evidence makes directory-level processing auditable:

- every output has a validation result
- every output has a before/after privacy comparison
- failures are counted in the batch summary
- non-zero exit status protects CI and scripted workflows

## Safety Notes

Use synthetic or explicitly approved test DICOM files only. Batch processing is
not legal, clinical, regulatory, or security certification. Review outputs
before sharing, especially pixel data and burned-in annotations.
