# Dental DICOM Privacy Toolkit | 牙科 DICOM 脱敏加密共享工具包

Dental DICOM Privacy Toolkit is a local-first open-source toolkit for dental
DICOM anonymization, DICOM de-identification, pixel privacy review, audit
evidence, and encrypted DICOM sharing.

牙科 DICOM 脱敏加密共享工具包是一个本地优先的开源项目，用于牙科 DICOM 脱敏、DICOM 去标识化、像素隐私复核、审计证据和加密共享流程。

**Keywords:** dental DICOM, dental imaging, DICOM anonymization, DICOM de-identification, DICOM confidentiality, DICOM JSON export, filename privacy scan, privacy remediation plan, profile conformance, pixel risk scan, Orthanc anonymization plan, dcmodify plan, encrypted DICOM sharing, de-identification certificate, deterministic pseudonymization, local browser workbench, workflow quality gate, residual privacy risk score, privacy regression suite, MacBook validation report, GitHub publish preflight, public showcase gallery, community health, security policy, CBCT, oral radiology, synthetic DICOM, 牙科DICOM, 牙科影像, DICOM脱敏, DICOM去标识化, 医学影像隐私, 文件名隐私扫描, 隐私整改计划, 脱敏配置符合性验证, 像素风险扫描, 去标识化证明书, DICOM伪名化, 本地工作台, 工作流质量门禁, 残余隐私风险评分, 隐私回归测试, MacBook验收报告, GitHub发布预检, 公开示例画廊, 开源协作健康, 安全政策, Orthanc匿名化计划, 加密共享, 患者隐私保护

> Safety boundary: this public repository is for source code, documentation,
> tests, synthetic examples, and reproducible demonstrations only. Do not commit
> real patient DICOM files, CBCT scans, radiographs, intraoral photos, clinic
> exports, consent forms, credentials, private notes, or manuscript drafts.

## English

### What You Can Do

Use this project when you need a reproducible local workflow for dental imaging
privacy review before research sharing, teaching, product demos, or technical
collaboration.

- Generate synthetic dental DICOM files for safe testing.
- Inspect DICOM metadata and flag privacy-sensitive tags.
- Scan file and folder names for patient identifiers.
- Build a privacy remediation plan before anonymization.
- Anonymize DICOM files with readable YAML profiles.
- Verify anonymized files against the selected profile.
- Render PNG previews for human review.
- Run conservative pixel risk scans for burned-in identifiers.
- Apply planned rectangular pixel redaction when a region is known.
- Create JSON and HTML reports for audit evidence.
- Package de-identified files with checksums and optional encryption.
- Run local quality gates, MacBook validation, and publish preflight checks.

This is not a diagnostic viewer, clinical decision tool, legal compliance
certificate, PACS replacement, or guarantee that every identifier has been
removed. Pixel-level burned-in identifiers still require human review.

### Requirements

- Python 3.11+
- Git
- macOS, Linux, or Windows
- Synthetic or explicitly approved test files only

### Install

```bash
git clone git@github.com:PEIWEIWU-AYS/PEIWEIWU-AYS-dental-dicom-privacy-toolkit.git
cd PEIWEIWU-AYS-dental-dicom-privacy-toolkit

python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Check the installation:

```bash
ddpt doctor
ddpt safety scan .
```

### Fastest Demo

Run the complete synthetic demo:

```bash
ddpt demo demo-run
```

Open the generated report:

```text
demo-run/reports/demo-summary.html
```

The demo creates synthetic input, anonymized output, preview images, pixel review
artifacts, an encrypted sharing package, verification receipts, and HTML reports.

### Step-by-Step Workflow

Create a synthetic DICOM file:

```bash
ddpt synthetic demo-run/input/sample.synthetic.dcm
```

Inspect metadata:

```bash
ddpt inspect demo-run/input/sample.synthetic.dcm \
  --json demo-run/reports/inspect.json \
  --html demo-run/reports/inspect.html
```

Review the folder before sharing:

```bash
ddpt inventory demo-run/input \
  --json demo-run/reports/inventory.json \
  --csv demo-run/reports/inventory.csv \
  --html demo-run/reports/inventory.html

ddpt filename scan demo-run/input \
  --json demo-run/reports/filename-privacy.json \
  --html demo-run/reports/filename-privacy.html
```

Create a remediation plan:

```bash
ddpt remediation plan demo-run/input \
  --profile dental-basic \
  --json demo-run/reports/remediation-plan.json \
  --html demo-run/reports/remediation-plan.html
```

Preview anonymization without writing a new DICOM file:

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --dry-run \
  --audit demo-run/reports/dry-run-audit.json \
  --html demo-run/reports/dry-run-audit.html
```

Write the anonymized DICOM file:

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --out demo-run/outputs/sample.anonymized.dcm \
  --audit demo-run/reports/anonymization-audit.json \
  --html demo-run/reports/anonymization-audit.html
```

Validate the output:

```bash
ddpt validate demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/validation.json

ddpt profile verify demo-run/input/sample.synthetic.dcm \
  demo-run/outputs/sample.anonymized.dcm \
  --profile dental-basic \
  --json demo-run/reports/profile-conformance.json \
  --html demo-run/reports/profile-conformance.html
```

Create visual review artifacts:

```bash
ddpt preview demo-run/input/sample.synthetic.dcm \
  --out demo-run/reports/input-preview.png

ddpt pixel-risk scan demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/pixel-risk.json \
  --html demo-run/reports/pixel-risk.html

ddpt pixel-review demo-run/outputs/sample.anonymized.dcm \
  --out-dir demo-run/reports/pixel-review \
  --plan profiles/dental-pixel-redaction.yml \
  --json demo-run/reports/pixel-review.json \
  --html demo-run/reports/pixel-review.html
```

Redact a known pixel region:

```bash
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm \
  --plan profiles/dental-pixel-redaction.yml \
  --out demo-run/outputs/sample.redacted.dcm \
  --audit demo-run/reports/pixel-redaction.json
```

Package, verify, and decrypt shared output:

```bash
ddpt package demo-run/outputs \
  --encrypt \
  --key-out demo-run/share/package.key \
  --manifest demo-run/share/manifest.json \
  --out demo-run/share/package.ddpt

ddpt verify demo-run/share/package.ddpt \
  --key demo-run/share/package.key \
  --receipt demo-run/reports/package-receipt.json \
  --html demo-run/reports/package-receipt.html

ddpt decrypt demo-run/share/package.ddpt \
  --key demo-run/share/package.key \
  --out demo-run/restored
```

Create handoff evidence:

```bash
ddpt compare deid demo-run/input/sample.synthetic.dcm \
  demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/deid-comparison.json \
  --html demo-run/reports/deid-comparison.html

ddpt certificate create demo-run \
  --json demo-run/reports/deid-certificate.json \
  --html demo-run/reports/deid-certificate.html

ddpt share readiness demo-run \
  --json demo-run/reports/share-readiness.json \
  --html demo-run/reports/share-readiness.html
```

### Repeatable Recipe Workflow

Use the included YAML recipe for a repeatable staged run:

```bash
ddpt workflow run recipes/dental-demo-workflow.yml \
  --root workflow-run \
  --json workflow-run/reports/workflow-run.json \
  --html workflow-run/reports/workflow-run.html

ddpt quality gate workflow-run \
  --workflow-report workflow-run/reports/workflow-run.json \
  --json workflow-run/reports/quality-gate.json \
  --html workflow-run/reports/quality-gate.html

ddpt risk score workflow-run \
  --json workflow-run/reports/residual-risk.json \
  --html workflow-run/reports/residual-risk.html
```

### Local Browser Workbench

Start the local API:

```bash
ddpt api serve demo-run --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765/workbench
```

The local browser workbench is for local demonstration only. It does not upload
DICOM files to a cloud service.

### Useful Checks Before Publishing

```bash
ddpt release audit .
ddpt evidence bundle . --out evidence-run
ddpt dashboard build evidence-run --out evidence-run/reports/review-dashboard.html
ddpt showcase build evidence-run --out showcase-run/showcase.html
ddpt regression suite regression-run
ddpt macbook validate . --out macbook-validation-run
ddpt publish preflight . --check-remote
```

### Other Useful Commands

```bash
ddpt profile lint dental-basic
ddpt profile coverage dental-basic
ddpt profile compare dental-basic dental-research-sharing
ddpt confidentiality alignment --profile dental-basic
ddpt policy export --json reports/policy-registry.json --csv reports/policy-registry.csv --html reports/policy-registry.html
ddpt dcmodify plan demo-run/input/sample.synthetic.dcm --profile dental-basic
ddpt dicom-json export demo-run/input/sample.synthetic.dcm --json demo-run/reports/dicom-json.json
ddpt orthanc plan demo-run/input/sample.synthetic.dcm --profile dental-basic --resource-id sample-synthetic-instance
ddpt synthetic-study synthetic-study-demo --patients 2 --files-per-patient 2 --json synthetic-study-demo/manifest.json
ddpt batch demo-run/input --out demo-run/batch-output
```

### Outputs

Most commands can write machine-readable JSON and human-readable HTML.

Typical output folders:

```text
demo-run/input/      synthetic DICOM input
demo-run/outputs/    anonymized and pixel-redacted DICOM files
demo-run/reports/    JSON reports, HTML reports, PNG previews
demo-run/share/      encrypted package, manifest, verification key
demo-run/restored/   decrypted package contents for receiver-side checks
```

Generated demo output should normally stay out of Git. Keep the repository
focused on source code, documentation, tests, synthetic examples, and community
health files.

### Documentation

- [Demo guide](docs/demo-guide.md)
- [Data safety](docs/data-safety.md)
- [Workflow recipes](docs/workflow-recipes.md)
- [Profile conformance](docs/profile-conformance.md)
- [Pixel review](docs/pixel-review.md)
- [Share readiness](docs/share-readiness.md)
- [MacBook validation](docs/macbook-validation.md)
- [Local API](docs/local-api.md)
- [Discoverability](docs/discoverability.md)

### Repository Layout

```text
src/ddpt/                 Python package and CLI implementation
profiles/                 anonymization and pixel redaction profiles
recipes/                  reproducible YAML workflows
docs/                     detailed documentation
tests/                    automated tests
examples/synthetic-dicom/ synthetic-only examples
dicom-anonymizer/         de-identification notes and profile area
dicom-encryption/         packaging and encryption notes
dicom-sharing/            sharing workflow notes
```

### Contributing and Security

Issues and pull requests are welcome with synthetic examples only. Please read:

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Support](SUPPORT.md)
- [Code of conduct](CODE_OF_CONDUCT.md)

Do not include real clinical images, real patient metadata, exported clinic
folders, credentials, private manuscripts, or other sensitive material in
issues, pull requests, examples, or tests.

### Suggested GitHub Topics

`dicom` `dental-imaging` `medical-imaging` `dicom-anonymization` `de-identification` `dicom-confidentiality` `dicom-json` `orthanc` `dcmodify` `pydicom` `pixel-risk` `privacy-regression` `pseudonymization` `local-first` `web-ui` `encryption` `audit-report` `cbct` `oral-radiology` `dentistry` `open-source-healthcare`

### License

MIT License.

## 中文

### 你可以用它做什么

当你需要在研究共享、教学演示、产品展示或技术协作前，本地复现一套牙科影像隐私处理流程时，可以使用这个项目。

- 生成安全测试用的 synthetic 合成牙科 DICOM。
- 检查 DICOM metadata，并标记隐私敏感 tag。
- 扫描文件名和文件夹路径中的患者标识风险。
- 在脱敏前生成 privacy remediation plan 隐私整改计划。
- 使用可读 YAML profile 执行 DICOM 脱敏。
- 验证脱敏文件是否符合指定 profile。
- 生成 PNG 预览图供人工复核。
- 对 burned-in identifier 像素标识风险进行保守筛查。
- 对已知区域执行矩形像素遮盖。
- 生成 JSON 和 HTML 审计报告。
- 将去标识化文件打包，并可选择加密。
- 运行本地质量门禁、MacBook 验收和 GitHub 发布预检。

它不是诊断阅片软件、临床决策工具、法律合规证书、PACS 替代品，也不能保证自动移除所有标识。像素层烧录标识仍然需要人工复核。

### 环境要求

- Python 3.11+
- Git
- macOS、Linux 或 Windows
- 只使用 synthetic 合成数据，或明确获准使用的测试文件

### 安装

```bash
git clone git@github.com:PEIWEIWU-AYS/PEIWEIWU-AYS-dental-dicom-privacy-toolkit.git
cd PEIWEIWU-AYS-dental-dicom-privacy-toolkit

python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Windows PowerShell 使用：

```powershell
.\.venv\Scripts\Activate.ps1
```

检查安装是否成功：

```bash
ddpt doctor
ddpt safety scan .
```

### 最快演示

运行完整合成演示：

```bash
ddpt demo demo-run
```

打开生成的报告：

```text
demo-run/reports/demo-summary.html
```

这个演示会生成合成输入、脱敏输出、预览图、像素复核材料、加密共享包、验证回执和 HTML 报告。

### 分步骤使用流程

生成合成 DICOM 文件：

```bash
ddpt synthetic demo-run/input/sample.synthetic.dcm
```

检查 metadata：

```bash
ddpt inspect demo-run/input/sample.synthetic.dcm \
  --json demo-run/reports/inspect.json \
  --html demo-run/reports/inspect.html
```

共享前检查文件夹：

```bash
ddpt inventory demo-run/input \
  --json demo-run/reports/inventory.json \
  --csv demo-run/reports/inventory.csv \
  --html demo-run/reports/inventory.html

ddpt filename scan demo-run/input \
  --json demo-run/reports/filename-privacy.json \
  --html demo-run/reports/filename-privacy.html
```

生成隐私整改计划：

```bash
ddpt remediation plan demo-run/input \
  --profile dental-basic \
  --json demo-run/reports/remediation-plan.json \
  --html demo-run/reports/remediation-plan.html
```

先预览脱敏动作，不写入新 DICOM：

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --dry-run \
  --audit demo-run/reports/dry-run-audit.json \
  --html demo-run/reports/dry-run-audit.html
```

写出脱敏后的 DICOM 文件：

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --out demo-run/outputs/sample.anonymized.dcm \
  --audit demo-run/reports/anonymization-audit.json \
  --html demo-run/reports/anonymization-audit.html
```

验证输出结果：

```bash
ddpt validate demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/validation.json

ddpt profile verify demo-run/input/sample.synthetic.dcm \
  demo-run/outputs/sample.anonymized.dcm \
  --profile dental-basic \
  --json demo-run/reports/profile-conformance.json \
  --html demo-run/reports/profile-conformance.html
```

生成可视化复核材料：

```bash
ddpt preview demo-run/input/sample.synthetic.dcm \
  --out demo-run/reports/input-preview.png

ddpt pixel-risk scan demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/pixel-risk.json \
  --html demo-run/reports/pixel-risk.html

ddpt pixel-review demo-run/outputs/sample.anonymized.dcm \
  --out-dir demo-run/reports/pixel-review \
  --plan profiles/dental-pixel-redaction.yml \
  --json demo-run/reports/pixel-review.json \
  --html demo-run/reports/pixel-review.html
```

遮盖已知像素区域：

```bash
ddpt redact-pixels demo-run/outputs/sample.anonymized.dcm \
  --plan profiles/dental-pixel-redaction.yml \
  --out demo-run/outputs/sample.redacted.dcm \
  --audit demo-run/reports/pixel-redaction.json
```

打包、验证、解密共享输出：

```bash
ddpt package demo-run/outputs \
  --encrypt \
  --key-out demo-run/share/package.key \
  --manifest demo-run/share/manifest.json \
  --out demo-run/share/package.ddpt

ddpt verify demo-run/share/package.ddpt \
  --key demo-run/share/package.key \
  --receipt demo-run/reports/package-receipt.json \
  --html demo-run/reports/package-receipt.html

ddpt decrypt demo-run/share/package.ddpt \
  --key demo-run/share/package.key \
  --out demo-run/restored
```

生成交接证据：

```bash
ddpt compare deid demo-run/input/sample.synthetic.dcm \
  demo-run/outputs/sample.anonymized.dcm \
  --json demo-run/reports/deid-comparison.json \
  --html demo-run/reports/deid-comparison.html

ddpt certificate create demo-run \
  --json demo-run/reports/deid-certificate.json \
  --html demo-run/reports/deid-certificate.html

ddpt share readiness demo-run \
  --json demo-run/reports/share-readiness.json \
  --html demo-run/reports/share-readiness.html
```

### 可复现配方流程

使用内置 YAML recipe 运行可复现的阶段式流程：

```bash
ddpt workflow run recipes/dental-demo-workflow.yml \
  --root workflow-run \
  --json workflow-run/reports/workflow-run.json \
  --html workflow-run/reports/workflow-run.html

ddpt quality gate workflow-run \
  --workflow-report workflow-run/reports/workflow-run.json \
  --json workflow-run/reports/quality-gate.json \
  --html workflow-run/reports/quality-gate.html

ddpt risk score workflow-run \
  --json workflow-run/reports/residual-risk.json \
  --html workflow-run/reports/residual-risk.html
```

### 本地浏览器工作台

启动本地 API：

```bash
ddpt api serve demo-run --host 127.0.0.1 --port 8765
```

浏览器打开：

```text
http://127.0.0.1:8765/workbench
```

本地工作台只用于本机演示，不会把 DICOM 文件上传到云端服务。

### 发布前常用检查

```bash
ddpt release audit .
ddpt evidence bundle . --out evidence-run
ddpt dashboard build evidence-run --out evidence-run/reports/review-dashboard.html
ddpt showcase build evidence-run --out showcase-run/showcase.html
ddpt regression suite regression-run
ddpt macbook validate . --out macbook-validation-run
ddpt publish preflight . --check-remote
```

### 其他常用命令

```bash
ddpt profile lint dental-basic
ddpt profile coverage dental-basic
ddpt profile compare dental-basic dental-research-sharing
ddpt confidentiality alignment --profile dental-basic
ddpt policy export --json reports/policy-registry.json --csv reports/policy-registry.csv --html reports/policy-registry.html
ddpt dcmodify plan demo-run/input/sample.synthetic.dcm --profile dental-basic
ddpt dicom-json export demo-run/input/sample.synthetic.dcm --json demo-run/reports/dicom-json.json
ddpt orthanc plan demo-run/input/sample.synthetic.dcm --profile dental-basic --resource-id sample-synthetic-instance
ddpt synthetic-study synthetic-study-demo --patients 2 --files-per-patient 2 --json synthetic-study-demo/manifest.json
ddpt batch demo-run/input --out demo-run/batch-output
```

### 输出内容

多数命令可以同时写出机器可读的 JSON 和适合人工查看的 HTML。

常见输出文件夹：

```text
demo-run/input/      合成 DICOM 输入
demo-run/outputs/    脱敏和像素遮盖后的 DICOM 文件
demo-run/reports/    JSON 报告、HTML 报告、PNG 预览
demo-run/share/      加密包、manifest、验证 key
demo-run/restored/   解密后的接收方检查内容
```

生成的演示输出通常不要提交到 Git。仓库应主要保留源码、文档、测试、合成示例和 community health 文件。

### 文档入口

- [演示指南](docs/demo-guide.md)
- [数据安全](docs/data-safety.md)
- [工作流配方](docs/workflow-recipes.md)
- [Profile 符合性验证](docs/profile-conformance.md)
- [像素复核](docs/pixel-review.md)
- [共享就绪检查](docs/share-readiness.md)
- [MacBook 验收](docs/macbook-validation.md)
- [本地 API](docs/local-api.md)
- [可搜索性配置](docs/discoverability.md)

### 仓库结构

```text
src/ddpt/                 Python 包和 CLI 实现
profiles/                 脱敏和像素遮盖 profile
recipes/                  可复现 YAML 工作流
docs/                     详细文档
tests/                    自动化测试
examples/synthetic-dicom/ 仅合成数据示例
dicom-anonymizer/         去标识化说明和 profile 区域
dicom-encryption/         打包和加密说明
dicom-sharing/            共享流程说明
```

### 贡献和安全

欢迎提交 issue 和 pull request，但请只使用 synthetic 合成示例。贡献前请阅读：

- [贡献指南](CONTRIBUTING.md)
- [安全政策](SECURITY.md)
- [支持说明](SUPPORT.md)
- [行为准则](CODE_OF_CONDUCT.md)

不要在 issue、pull request、示例或测试中包含真实临床影像、真实患者 metadata、诊所导出文件夹、账号密钥、私人论文草稿或其他敏感材料。

### GitHub 推荐 Topics

`dicom` `dental-imaging` `medical-imaging` `dicom-anonymization` `de-identification` `dicom-confidentiality` `dicom-json` `orthanc` `dcmodify` `pydicom` `pixel-risk` `privacy-regression` `pseudonymization` `local-first` `web-ui` `encryption` `audit-report` `cbct` `oral-radiology` `dentistry` `open-source-healthcare`

### 许可证

MIT License.
