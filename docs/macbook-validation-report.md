# MacBook Validation Report | MacBook 本地验收报告

`ddpt macbook validate` creates a one-command local acceptance report for a
MacBook. It runs the project's existing quality evidence path and summarizes the
result into JSON and HTML.

`ddpt macbook validate` 会在 MacBook 本地生成一份总体验收报告，把环境检查、
发布审计、竞品能力矩阵、目标完成度审计、证据包和 GitHub 发布预检集中到一个
JSON/HTML 结果里。

## Command

```bash
ddpt macbook validate . --out macbook-validation-run
open macbook-validation-run/reports/macbook-validation.html
open macbook-validation-run/evidence-run/reports/review-dashboard.html
```

By default, the command checks whether the GitHub remote exists, but a missing
remote is reported as `action-required` instead of failing local validation.
This lets a user validate the software before creating the public repository.

If publishing to GitHub must be part of the acceptance gate:

```bash
ddpt macbook validate . --out macbook-validation-run --require-remote
```

## What It Checks

- local Python runtime and required dependencies
- public release audit
- competitor-informed capability matrix
- reference-tool coverage report
- original objective completion audit
- local evidence bundle generation
- static review dashboard generation
- GitHub publish preflight and remote reachability

## Outputs

```text
macbook-validation-run/
  reports/
    macbook-validation.json
    macbook-validation.html
  evidence-run/
    reports/
      evidence-bundle.html
      review-dashboard.html
      publish-preflight.html
      capability-matrix.html
      competitor-coverage.html
      objective-audit.html
```

## Expected Result

For local validation, expected status is:

- `local_passed: true`
- `passed: true`
- `github_ready: false` until the GitHub repository exists
- `github-publish-preflight: action-required` until the empty GitHub repository
  is created under `PEIWEIWU-AYS`

After the GitHub repository exists and is reachable, rerun:

```bash
ddpt macbook validate . --out macbook-validation-run --require-remote
```

Expected final publishing-ready status is:

- `local_passed: true`
- `github_ready: true`
- `passed: true`

## Safety Notes

The command uses synthetic generated DICOM evidence. It does not require real
patients, clinic exports, consent forms, CBCT files, screenshots, PDFs, or
spreadsheets. Keep real clinical materials outside this public repository.
