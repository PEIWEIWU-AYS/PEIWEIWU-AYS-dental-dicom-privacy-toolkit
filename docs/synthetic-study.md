# Synthetic Dental Study Generator | 合成牙科研究数据集生成器

`ddpt synthetic-study` creates a small multi-file synthetic DICOM dataset for
local workflow validation. It is useful for testing inventory, batch
anonymization, linkable pseudonymization, evidence bundles, and MacBook demos
without real patient data.

`ddpt synthetic-study` 可以生成一个多文件合成 DICOM 数据集，用于本地验证
inventory、批量脱敏、可链接伪名化、证据包和 MacBook 演示。它只生成合成数据，
不要把真实患者数据放进公开仓库。

## Command

```bash
ddpt synthetic-study synthetic-study-demo \
  --patients 2 \
  --files-per-patient 2 \
  --json synthetic-study-demo/manifest.json
```

Expected output:

```text
synthetic-study-demo/
  patient-001/study-001/dx-001.dcm
  patient-001/study-001/px-002.dcm
  patient-002/study-001/px-001.dcm
  patient-002/study-001/ct-002.dcm
```

The generated manifest includes patient IDs, patient names, modality counts,
study UIDs, series UIDs, SOP Instance UIDs, and relative file paths.

## Example Workflow

```bash
ddpt inventory synthetic-study-demo \
  --json synthetic-study-demo/reports/inventory.json \
  --html synthetic-study-demo/reports/inventory.html

ddpt batch synthetic-study-demo \
  --out synthetic-study-demo-batch \
  --profile dental-linkable-research
```

With `dental-linkable-research`, files from the same synthetic patient keep the
same research pseudonym while different synthetic patients get different
pseudonyms. The batch summary also reports validation failures and
de-identification comparison failures across the folder.

## Why This Matters

A single DICOM file is enough for unit tests, but real dental imaging privacy
workflows usually involve folders, repeated subjects, multiple modalities, and
batch processing. This command creates a safe local dataset for demonstrating
those workflows.

## Safety Notes

The command creates synthetic DICOM only. It is not a clinical data generator,
diagnostic simulator, or realistic CBCT reconstruction engine. Do not mix real
patient files into the generated folder before committing or sharing anything.
