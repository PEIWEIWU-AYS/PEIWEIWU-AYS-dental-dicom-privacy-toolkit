# Clinic Export Intake Triage | 诊所导出包接收预检

`ddpt intake triage` performs a read-only preflight on a dental clinic export
folder, single file, or ZIP archive before the export enters anonymization.

Many real dental imaging exports are not just `.dcm` files. They may include
`DICOMDIR`, PDFs, spreadsheets, JPEG/PNG screenshots, nested ZIP files, patient
names in folder paths, phone numbers, dates, and other sidecar material. This
command catches those risks before a user accidentally pushes or shares the raw
export.

## Command

```sh
ddpt intake triage clinic-export \
  --json reports/intake-triage.json \
  --html reports/intake-triage.html
```

ZIP archives can be scanned without extraction:

```sh
ddpt intake triage clinic-export.zip \
  --json reports/zip-intake-triage.json \
  --html reports/zip-intake-triage.html
```

## What It Detects

- DICOM files with direct or linkage identifiers
- `DICOMDIR` files, which can contain patient/study directory records
- Sidecar files such as PDF, CSV, Excel, Word, JPEG, PNG, TIFF, and HEIC
- Patient names, phone-like numbers, dates, MRN/case IDs, and Chinese patient markers in paths
- Unsafe ZIP member paths such as `../escape.dcm`
- Nested archives that need separate review
- Unknown file types that do not belong clearly in the DICOM privacy workflow

## Outputs

The JSON/HTML report includes:

- file counts by kind
- readable DICOM flags
- patient field presence flags
- high/medium metadata risk counts
- file-level findings
- recommended next steps
- explicit safety boundaries

## Safety Boundary

This command does not anonymize, extract, modify, upload, or contact servers. It
is an intake gate. A report with `ACTION REQUIRED` means the export should not
be published, pushed to GitHub, or shared until sidecar/path/archive risks are
resolved and DICOM files have gone through DDPT de-identification, validation,
profile conformance, de-identification comparison, and pixel review as needed.
