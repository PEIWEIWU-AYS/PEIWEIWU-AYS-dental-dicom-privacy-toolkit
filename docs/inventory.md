# DICOM Inventory Preflight | DICOM 目录预检

`ddpt inventory` is a read-only preflight command for DICOM directories. It helps a user understand what is inside a folder before anonymization, batch processing, or encrypted sharing.

`ddpt inventory` 是一个只读的 DICOM 目录预检命令，用于在脱敏、批处理或加密共享之前先了解文件夹里的影像类型和隐私风险。

## Why It Exists

General DICOM anonymizers often start at the point of modifying files. Dental clinics and research users usually need an earlier step:

- How many DICOM files are in this folder?
- Which files are readable?
- What modalities are present?
- Do patient name, patient ID, or birth date fields exist?
- How many high-risk and medium-risk tags are present?
- Can we export a safe CSV/HTML summary without exposing raw patient names?

## Example

```bash
ddpt inventory demo-run/input \
  --json demo-run/reports/inventory.json \
  --csv demo-run/reports/inventory.csv \
  --html demo-run/reports/inventory.html
```

## Outputs

- `inventory.json`: reproducible structured report
- `inventory.csv`: spreadsheet-friendly file list
- `inventory.html`: human-readable review page

The report records patient-field presence flags and short UID hashes. It does not export raw patient names, patient IDs, or raw UID values.

## Safety Boundary

Inventory is not anonymization. It does not modify DICOM files, remove identifiers, detect all burned-in pixel annotations, or prove legal compliance. Use it as a first step before `ddpt inspect`, `ddpt anonymize`, `ddpt validate`, and `ddpt package`.
