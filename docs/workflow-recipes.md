# Workflow Recipes | 工作流配方

`ddpt workflow run` executes a YAML recipe as a reproducible multi-stage DICOM privacy pipeline. It borrows the stage-by-stage lesson from RSNA CTP while staying lightweight, local-first, and synthetic-data oriented.

`ddpt workflow run` 可以按 YAML 配方执行多阶段 DICOM 隐私处理管线，吸收 RSNA CTP 的分阶段 pipeline 思路，但保持轻量、本地优先、面向合成数据。

## Run the Built-In Recipe

```bash
ddpt workflow run recipes/dental-demo-workflow.yml \
  --root workflow-run \
  --json workflow-run/reports/workflow-run.json \
  --html workflow-run/reports/workflow-run.html
```

Expected outputs:

- `workflow-run/input/sample.synthetic.dcm`
- `workflow-run/reports/inventory.json`
- `workflow-run/reports/inspect.html`
- `workflow-run/outputs/sample.anonymized.dcm`
- `workflow-run/outputs/sample.redacted.dcm`
- `workflow-run/share/package.ddpt`
- `workflow-run/reports/audit-chain.json`
- `workflow-run/reports/workflow-run.json`
- `workflow-run/reports/workflow-run.html`

## Supported Actions

- `synthetic`
- `inventory`
- `inspect`
- `anonymize`
- `validate`
- `preview`
- `redact-pixels`
- `package`
- `verify-package`
- `audit-chain`
- `audit-verify`

## Safety Boundary

Workflow recipes are automation, not privacy certification. They should be used with synthetic or explicitly approved test DICOM files. Generated `workflow-run/` and `workflow-*` folders are ignored by Git and by the public repository safety scan.
