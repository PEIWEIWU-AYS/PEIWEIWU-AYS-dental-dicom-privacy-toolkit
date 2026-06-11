# Reference Tool Export Pack

`ddpt reference export` turns one DDPT dental anonymization profile into a
review-only package for common DICOM privacy tools:

- DCMTK `dcmodify` command plans
- Orthanc REST anonymization payloads and curl examples
- RSNA CTP-style pipeline and anonymizer migration notes
- A small pydicom script derived from the same profile actions

This is meant for learning, migration planning, peer review, and GitHub
evidence. It does not execute external tools, contact Orthanc, install CTP, or
upload DICOM files.

## Example

```sh
ddpt synthetic demo/input/sample.synthetic.dcm
ddpt reference export demo/input/sample.synthetic.dcm \
  --profile dental-basic \
  --resource-id sample-synthetic-instance \
  --out demo/reference-tool-pack \
  --json demo/reports/reference-tool-export.json \
  --html demo/reports/reference-tool-export.html
```

## Outputs

The generated pack contains:

- `dcmtk/dcmodify-plan.json`
- `dcmtk/dcmodify-plan.html`
- `dcmtk/dcmodify-plan.sh`
- `orthanc/orthanc-plan.json`
- `orthanc/orthanc-plan.html`
- `orthanc/orthanc-payload.json`
- `orthanc/orthanc-anonymize.sh`
- `rsna-ctp/ctp-anonymizer.script`
- `rsna-ctp/ctp-style-pipeline.xml`
- `pydicom/pydicom-profile-anonymizer.py`
- `README.md`

The JSON/HTML index includes a cross-tool mapping table for each profile
operation, showing the corresponding dcmodify command, Orthanc mapping,
CTP-style line, and pydicom statement.

## Safety Boundary

All generated external-tool artifacts are review-only. `dcmodify` can edit files
in place if a user runs the generated shell script manually. Orthanc curl
commands can send requests to a configured server if manually executed. The CTP
files are migration notes and are not guaranteed to be drop-in production CTP
configuration. The generated pydicom script is small and inspectable, but it
must still be followed by DDPT validation, de-identification comparison, profile
conformance, and pixel review before any sharing decision.

Use synthetic or explicitly approved test DICOM files only.
