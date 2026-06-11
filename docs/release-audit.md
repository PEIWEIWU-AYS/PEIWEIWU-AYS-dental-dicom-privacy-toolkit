# Release Audit | 发布就绪审计

`ddpt release audit` checks whether the local repository is ready to present as a
public GitHub project.

`ddpt release audit` 用来检查本地仓库是否已经具备公开发布到 GitHub 的基本证据链。

It is not clinical, legal, regulatory, or security certification. It is a local
quality gate for open-source hygiene, discoverability, reproducible demos, and
synthetic-data safety.

它不是临床、法律、监管或安全认证，而是一个本地质量门槛：检查开源项目结构、搜索曝光、
可复现实验演示和 synthetic-only 安全边界。

## Command

```bash
ddpt release audit . --json release-audit.json --html release-audit.html
```

The command exits with status `0` when all checks pass and non-zero when any
release-readiness check fails.

## What It Checks

- required public repository files such as `README.md`, `LICENSE`,
  `CITATION.cff`, `ROADMAP.md`, CI config, docs, profiles, recipes, tests, and
  scripts
- bilingual README naming and keyword-rich discoverability signals
- documented core CLI commands
- competitor-learning notes covering RSNA DICOM Anonymizer, DicomCleaner,
  Orthanc, RSNA CTP, DCMTK, and pydicom
- core implementation modules
- Python package metadata and dependencies
- GitHub Actions gates for doctor, release audit, capability matrix, evidence
  bundle, dashboard build, safety scan, lint, and tests
- YAML workflow recipe coverage for the complete synthetic privacy pipeline
- `dental-basic` profile coverage for high-risk and medium-risk policy items
- public repository safety scan results

## Outputs

JSON output is designed for CI and reproducible evidence:

```bash
ddpt release audit . --json reports/release-audit.json
```

HTML output is designed for collaborators, screenshots, GitHub discussions, and
project demonstrations:

```bash
ddpt release audit . --html reports/release-audit.html
```

Each check includes:

- check ID
- category
- pass/fail status
- short message
- evidence or missing items

## Recommended Use

Run this before pushing a major milestone:

```bash
ddpt doctor
ddpt safety scan .
ddpt release audit . --json release-audit.json --html release-audit.html
ddpt capability matrix --root . --json capability-matrix.json --html capability-matrix.html
ddpt compare deid demo-run/input/sample.synthetic.dcm demo-run/outputs/sample.anonymized.dcm --json demo-run/reports/deid-comparison.json --html demo-run/reports/deid-comparison.html
ddpt share readiness demo-run --json demo-run/reports/share-readiness.json --html demo-run/reports/share-readiness.html
ddpt evidence bundle . --out evidence-run
ddpt dashboard build evidence-run --out evidence-run/reports/review-dashboard.html
ruff check .
pytest -q
```

For this public repository, keep generated reports out of commits unless they are
intentional examples. Real DICOM, clinical photos, private spreadsheets, consent
forms, clinic exports, and manuscript drafts should stay outside the repository.
