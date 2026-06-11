# Residual Privacy Risk Score | 残余隐私风险评分

`ddpt risk score` aggregates generated workflow evidence into a 100-point
residual privacy risk report.

`ddpt risk score` 会把已生成的工作流证据汇总为 100 分制的残余隐私风险报告，方便
MacBook 本地验收、GitHub 展示和协作者快速理解当前输出是否适合继续分享。

## Command

```bash
ddpt risk score workflow-run \
  --json workflow-run/reports/residual-risk.json \
  --html workflow-run/reports/residual-risk.html
```

The built-in workflow recipe also runs a final `risk-score` stage and writes:

```text
workflow-run/reports/residual-risk.json
workflow-run/reports/residual-risk.html
```

## What It Scores

The score is based on evidence already produced by the toolkit:

- before/after de-identification comparison
- profile conformance verification
- DICOM PS3.15-inspired confidentiality alignment
- pixel risk and pixel review evidence
- filename and path privacy scan
- encrypted package, share-readiness, audit-chain, and certificate evidence
- workflow quality gate result

## Output Meaning

The report includes:

- total score out of 100
- residual risk level: `low`, `medium`, or `high`
- blocking findings count
- warning findings count
- per-component score, status, evidence paths, and recommended actions

The public synthetic workflow is expected to pass with low residual risk when all
required reports are present and successful.

## Why This Matters

Many DICOM tools can anonymize metadata, clean pixels, modify tags, or run
pipelines. This project adds a reviewer-friendly aggregation layer: instead of
asking a visitor to inspect many JSON files one by one, the residual risk report
summarizes the evidence chain into one human-readable HTML page.

This is useful for:

- MacBook validation
- GitHub README screenshots and demos
- collaborator handoff review
- CI evidence checks
- explaining the toolkit's privacy workflow in papers or project notes

## Safety Notes

The score is a project evidence summary. It is not clinical, legal, regulatory,
security, HIPAA, GDPR, or DICOM conformance certification. Use synthetic or
explicitly approved test DICOM files only.
