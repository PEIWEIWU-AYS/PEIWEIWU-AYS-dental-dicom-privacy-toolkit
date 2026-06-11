# Share Readiness | 分享前就绪检查

`ddpt share readiness` checks whether a synthetic demo output folder has the key
artifacts needed before sharing an anonymized dental DICOM package with a
collaborator.

`ddpt share readiness` 用来检查合成数据演示目录是否已经具备分享前所需的关键证据：
脱敏验证、脱敏前后对比、像素审查、加密包回执和审计链。

## Command

```bash
ddpt share readiness demo-run \
  --json demo-run/reports/share-readiness.json \
  --html demo-run/reports/share-readiness.html
```

## What It Checks

The readiness gate checks:

- anonymized DICOM output exists
- validation report passed
- before/after de-identification comparison passed
- no residual high-risk or medium-risk policy items remain in the comparison report
- private tags after anonymization are zero
- pixel review report and preview images exist
- encrypted package verification receipt passed
- audit chain verification passed

## Output

The command writes:

- terminal pass/fail table
- JSON readiness report
- HTML readiness report

The one-command demo automatically writes:

```text
demo-run/reports/share-readiness.json
demo-run/reports/share-readiness.html
```

The evidence bundle includes the HTML readiness report as a sharing artifact.

## Safety Notes

This is a local project gate, not a clinical, legal, regulatory, or security
certification. It helps reviewers see whether the synthetic demo package has the
expected evidence before sharing. Real patient DICOM files require a separate
approved clinical, legal, and institutional workflow.
