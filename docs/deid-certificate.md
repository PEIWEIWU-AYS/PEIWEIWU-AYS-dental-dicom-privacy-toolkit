# De-identification Certificate | 去标识化证明书

`ddpt certificate create` builds a portable JSON and HTML certificate from a
synthetic demo or workflow output folder.

`ddpt certificate create` 会把合成数据演示目录中的脱敏证据汇总成一份 JSON 和
HTML 去标识化证明书，方便 MacBook 验收、协作者沟通和 GitHub 项目展示。

## Command

```bash
ddpt certificate create demo-run \
  --json demo-run/reports/deid-certificate.json \
  --html demo-run/reports/deid-certificate.html
```

The one-command demo automatically writes:

```text
demo-run/reports/deid-certificate.json
demo-run/reports/deid-certificate.html
```

## What It Summarizes

The certificate checks existing evidence from the demo folder:

- anonymization audit exists and records metadata actions
- validation report passed
- before/after de-identification comparison passed
- residual high-risk and medium-risk keywords are empty
- private tags after anonymization are zero
- pixel review report and preview PNG files exist
- encrypted package verification receipt passed
- audit chain verification passed
- share-readiness gate passed

## Output

The JSON certificate is machine-readable. The HTML certificate is designed for
local review and screenshots. It includes:

- overall pass/fail status
- profile name
- input and anonymized DICOM paths
- passed checks and total checks
- residual policy findings
- pixel review region count
- encrypted package entry count
- package SHA-256
- evidence links and summary messages

## When To Use It

Use the certificate after running:

```bash
ddpt demo demo-run
```

or after generating a complete evidence bundle:

```bash
ddpt evidence bundle . --out evidence-run
open evidence-run/demo-run/reports/deid-certificate.html
```

It can also run as the final stage in a YAML workflow recipe:

```yaml
- id: deid-certificate
  action: certificate
  root: .
  json: reports/deid-certificate.json
  html: reports/deid-certificate.html
```

## Safety Notes

This is a project evidence certificate for synthetic demonstrations. It is not
legal certification, HIPAA compliance proof, regulatory approval, clinical
validation, or a guarantee that re-identification is impossible.

Real patient DICOM files require an approved clinical, legal, institutional, and
security workflow outside this public repository.
