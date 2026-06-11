# Showcase Gallery | 公开示例画廊

`ddpt showcase build` creates a static HTML gallery from an existing evidence
bundle. It is designed for GitHub visitors, collaborators, profile pages, and
screenshots.

`ddpt showcase build` 会从本地 evidence bundle 生成一个静态 HTML 展示页，用来给
GitHub 访客、协作者和评审快速理解项目效果。

## Command

```bash
ddpt evidence bundle . --out evidence-run
ddpt showcase build evidence-run \
  --out showcase-run/showcase.html \
  --json showcase-run/showcase.json
open showcase-run/showcase.html
```

## What It Shows

- synthetic input, anonymized output, pixel-review overlay, and redacted preview
- demo summary
- de-identification certificate
- before/after de-identification comparison
- profile conformance report
- DICOM confidentiality alignment report
- clinic export intake triage report
- reference-tool export report
- competitor coverage report
- capability matrix
- privacy regression suite
- GitHub publish preflight

## Why This Matters

The review dashboard is useful for technical auditing. The showcase gallery is
more public-facing: it presents the project story, strongest synthetic visuals,
and key reports in one page that can be opened locally or used for screenshots.

It helps explain how this project combines ideas from RSNA DICOM Anonymizer,
DicomCleaner, Orthanc, RSNA CTP, DCMTK `dcmodify`, and pydicom examples while
adding a dental-focused, local-first evidence workflow.

## Safety Notes

The gallery is generated from synthetic evidence only. Generated output is
ignored by Git by default. Do not publish real patient DICOM, CBCT files, dental
photos, screenshots, clinic exports, PDFs, spreadsheets, or consent forms.
