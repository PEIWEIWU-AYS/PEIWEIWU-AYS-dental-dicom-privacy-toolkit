# Contributing | 贡献指南

Thank you for helping improve Dental DICOM Privacy Toolkit. This project is a
synthetic-data-only open-source toolkit for dental DICOM privacy workflows.

感谢你帮助改进本项目。本仓库只接受合成数据、文档、测试和工具代码，不接受真实
患者资料。

## Safety First

- Do not upload real DICOM, CBCT files, radiographs, intraoral photos, PDFs,
  spreadsheets, clinic exports, consent forms, or screenshots with patient data.
- Use synthetic DICOM created by `ddpt synthetic`, `ddpt synthetic-study`, or the
  demo/evidence commands.
- If a bug requires an example file, create a synthetic reproduction.
- Remove local generated folders such as `demo-run/`, `evidence-run/`,
  `showcase-run/`, and `macbook-validation-run/` before committing.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Quality Checks

Run these before opening a pull request:

```bash
ruff check .
pytest
ddpt release audit .
ddpt capability matrix --root .
ddpt competitor coverage --root .
ddpt completion audit .
ddpt evidence bundle . --out evidence-run
```

For a local acceptance report:

```bash
ddpt macbook validate . --out macbook-validation-run --no-check-remote
```

## Pull Request Scope

Good pull requests usually include:

- a focused code or documentation change
- tests for new CLI/API/report behavior
- updated docs when commands or outputs change
- safety wording for clinical, privacy, or sharing features
- no generated evidence folders unless intentionally curated as safe examples

## Clinical Boundary

This project does not provide clinical diagnosis, legal advice, regulatory
approval, security certification, or a guarantee that re-identification is
impossible. All public examples must remain synthetic.
