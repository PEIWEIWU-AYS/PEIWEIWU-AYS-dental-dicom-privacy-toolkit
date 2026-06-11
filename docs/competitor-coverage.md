# Competitor Coverage | 精品项目能力覆盖报告

`ddpt competitor coverage` creates a JSON and HTML report that maps this
toolkit against the reference tools named in the project objective:

- RSNA DICOM Anonymizer
- PixelMed DicomCleaner
- Orthanc
- RSNA CTP
- DCMTK `dcmodify`
- pydicom anonymization examples

`ddpt competitor coverage` 用来生成“竞品能力覆盖报告”，把本项目从这些精品
DICOM 工具中学习到的能力、已经实现的证据、差异化价值和安全边界列出来。

## Command

```bash
ddpt competitor coverage \
  --root . \
  --json competitor-coverage.json \
  --html competitor-coverage.html
```

## What It Proves

The report groups implemented capabilities by reference tool. For each tool, it
shows:

- strengths learned from that tool
- project responses and differentiators
- implemented capabilities
- repository evidence files
- runnable commands
- explicit boundaries and non-claims

This is useful for GitHub visitors, collaborators, reviewers, and MacBook demos
because it turns "we learned from the best tools" into a reproducible artifact.

## Local API

When the API root is inside this repository, the same report is available from:

```bash
curl http://127.0.0.1:8765/competitor-coverage
```

## Safety Boundary

This is a positioning and evidence report, not clinical, legal, regulatory, or
security certification. Public demos must use synthetic data only.
