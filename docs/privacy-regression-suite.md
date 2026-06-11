# Privacy Regression Suite | 隐私回归测试套件

`ddpt regression suite` generates adversarial synthetic DICOM cases and verifies
that key privacy guardrails fire as expected.

`ddpt regression suite` 会生成对抗性合成 DICOM 场景，并验证本项目的隐私防线是否按
预期工作。它不是 happy-path demo，而是用已知泄漏场景测试工具链。

## Command

```bash
ddpt regression suite regression-run \
  --json regression-run/reports/privacy-regression-suite.json \
  --html regression-run/reports/privacy-regression-suite.html
```

## Cases

The suite currently checks:

- direct metadata identifiers are covered and removed by the profile
- risky filenames and private tags are detected or removed
- `BurnedInAnnotation=YES` triggers pixel review risk
- linkable research pseudonymization is stable for repeated synthetic PatientID values

## Outputs

The command writes a suite-level JSON/HTML report and per-case evidence under
the output directory. The evidence bundle also includes:

```text
evidence-run/reports/privacy-regression-suite.json
evidence-run/reports/privacy-regression-suite.html
evidence-run/regression-run/
```

## Why This Matters

Many DICOM privacy demos only prove the normal path. This suite adds regression
pressure: if metadata comparison, filename scanning, private tag removal, pixel
risk triage, or linkable pseudonymization breaks later, tests and CI can catch it.

## Safety Notes

All fixtures are synthetic and generated locally. A passing regression suite is
project evidence, not legal, clinical, regulatory, security, or complete
de-identification certification.
