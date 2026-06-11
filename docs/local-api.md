# Local REST API | 本地 REST API

`ddpt api serve` exposes a local FastAPI service for synthetic-data workflow demos and integration experiments. It borrows the REST/API lesson from Orthanc while staying intentionally small and local-first.

`ddpt api serve` 提供一个本地 FastAPI 服务，用于合成数据演示和系统集成实验。它吸收 Orthanc 的 REST/API 思路，但保持轻量、本地优先。

## Start the API

```bash
ddpt api serve demo-run --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765/docs
http://127.0.0.1:8765/workbench
```

## Endpoints

- `GET /health`
- `GET /workbench`
- `GET /files/{path}`
- `POST /demo`
- `POST /inventory`
- `POST /inspect`
- `POST /dicom-json`
- `POST /filename-scan`
- `POST /remediation-plan`
- `POST /pixel-risk`
- `POST /regression-suite`
- `POST /publish-preflight`
- `GET /competitor-coverage`
- `POST /anonymize`
- `POST /validate`
- `POST /preview`

Example request:

```bash
curl -X POST http://127.0.0.1:8765/inspect \
  -H "Content-Type: application/json" \
  -d '{"path":"input/sample.synthetic.dcm"}'
```

Safe metadata JSON export:

```bash
curl -X POST http://127.0.0.1:8765/dicom-json \
  -H "Content-Type: application/json" \
  -d '{"path":"input/sample.synthetic.dcm"}'
```

Competitor coverage report, when the API root is inside this repository:

```bash
curl http://127.0.0.1:8765/competitor-coverage
```

Generate local privacy evidence reports from the API:

```bash
curl -X POST http://127.0.0.1:8765/remediation-plan \
  -H "Content-Type: application/json" \
  -d '{"path":"input","profile":"dental-basic"}'

curl -X POST http://127.0.0.1:8765/filename-scan \
  -H "Content-Type: application/json" \
  -d '{"path":"input"}'

curl -X POST http://127.0.0.1:8765/pixel-risk \
  -H "Content-Type: application/json" \
  -d '{"path":"outputs/sample.anonymized.dcm"}'

curl -X POST http://127.0.0.1:8765/regression-suite \
  -H "Content-Type: application/json" \
  -d '{"output_dir":"api-regression-run"}'
```

When the API root is inside this repository, publish readiness can also be
checked locally:

```bash
curl -X POST http://127.0.0.1:8765/publish-preflight \
  -H "Content-Type: application/json" \
  -d '{}'
```

These report endpoints return JSON and write matching JSON/HTML report files
inside the API root. The response includes `_api_artifacts` with relative paths
to the generated files.

## Path Safety

All paths are resolved inside the API root directory. Requests such as `../outside.dcm` are rejected.

## Local Workbench

The `/workbench` page provides browser controls for synthetic demo generation,
inventory, inspection, anonymization, validation, preview, privacy evidence
reports, regression suite runs, and publish preflight checks. It is a GUI-style
entrypoint for MacBook demonstrations, not a production viewer.

## Safety Boundary

This is not Orthanc, PACS, DICOMweb, or a production server. It is a local integration demo for synthetic or explicitly approved test DICOM files. Do not expose it to the public internet, and do not use it for clinical diagnosis.
