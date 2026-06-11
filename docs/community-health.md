# Community Health | 开源协作健康文件

This repository includes GitHub community health files so collaborators can
contribute without weakening the synthetic-data safety boundary.

本仓库包含开源协作健康文件，用来规范贡献、问题反馈、安全报告和 PR 审查，同时
防止真实患者资料进入公开仓库。

## Included Files

- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/privacy_safety.yml`
- `.github/ISSUE_TEMPLATE/config.yml`

## Why This Matters

Dental imaging privacy projects need stronger contribution boundaries than a
typical demo repository. Contributors may accidentally share real DICOM,
radiographs, screenshots, spreadsheets, consent forms, or clinic exports while
trying to explain a bug.

The templates ask contributors to:

- use synthetic reproduction steps
- avoid attaching clinical material
- confirm that no PHI or credentials are included
- run local quality checks before pull requests
- route privacy and safety concerns through a focused template

## Recommended Maintainer Flow

1. Confirm the report uses synthetic data only.
2. Reproduce locally with `ddpt doctor` and the reported command.
3. Run `ruff check .` and `pytest` before merging code.
4. Run `ddpt release audit .` before public publishing.
5. Keep generated evidence folders out of Git unless intentionally curated.

## Safety Boundary

These files improve open-source workflow quality. They do not provide medical,
legal, regulatory, security, or privacy certification.
