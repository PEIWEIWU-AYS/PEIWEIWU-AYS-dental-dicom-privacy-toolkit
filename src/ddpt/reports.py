from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Template

from ddpt.models import (
    AnonymizationAudit,
    BatchSummary,
    DemoPipelineResult,
    EvidenceBundleResult,
    InspectionReport,
    InventoryReport,
    PackageVerificationReceipt,
    ReleaseAuditReport,
    WorkflowRunReport,
)
from ddpt.utils import ensure_parent

INSPECTION_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Privacy Report</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2 { color: #123; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .high { color: #b00020; font-weight: 700; }
    .medium { color: #8a5a00; font-weight: 700; }
    .low { color: #1f6f43; }
    .unknown { color: #4b5563; }
  </style>
</head>
<body>
  <h1>Dental DICOM Privacy Report</h1>
  <p class="warning">
    Synthetic-data workflow only. De-identification reduces privacy risk but is not a
    guarantee. Pixel-level burned-in annotations require separate review.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>File: {{ report.file_path }}</li>
    <li>Modality: {{ report.modality or "unknown" }}</li>
    <li>High-risk tags: {{ report.high_risk_count }}</li>
    <li>Medium-risk tags: {{ report.medium_risk_count }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Findings</h2>
  <table>
    <thead>
      <tr>
        <th>Risk</th>
        <th>Tag</th>
        <th>Keyword</th>
        <th>Category</th>
        <th>Recommended</th>
        <th>DICOM Code</th>
        <th>Name</th>
        <th>Value</th>
        <th>Reason</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.findings %}
      <tr>
        <td class="{{ item.risk }}">{{ item.risk }}</td>
        <td>{{ item.tag }}</td>
        <td>{{ item.keyword }}</td>
        <td>{{ item.category }}</td>
        <td>{{ item.recommended_action }}</td>
        <td>{{ item.dicom_action_code }}</td>
        <td>{{ item.name }}</td>
        <td>{{ item.value }}</td>
        <td>{{ item.reason }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

AUDIT_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Anonymization Audit</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Anonymization Audit</h1>
  <p class="warning">
    Synthetic-data workflow only. Review pixel data separately for burned-in identifiers.
  </p>
  <ul>
    <li>Input: {{ audit.input_path }}</li>
    <li>Output: {{ audit.output_path }}</li>
    <li>Profile: {{ audit.profile }}</li>
    <li>Private tags removed: {{ audit.private_tags_removed }}</li>
    <li>Generated at: {{ audit.generated_at }}</li>
  </ul>
  <table>
    <thead>
      <tr><th>Action</th><th>Tag</th><th>Keyword</th><th>Before</th><th>After</th></tr>
    </thead>
    <tbody>
      {% for item in audit.actions %}
      <tr>
        <td>{{ item.action }}</td>
        <td>{{ item.tag }}</td>
        <td>{{ item.keyword }}</td>
        <td>{{ item.before }}</td>
        <td>{{ item.after }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

DEMO_SUMMARY_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Privacy Toolkit Demo Summary</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2 { color: #123; }
    .ok { color: #1f6f43; font-weight: 700; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
    .preview-grid { display: flex; gap: 16px; flex-wrap: wrap; }
    .preview-grid figure { margin: 0; }
    .preview-grid img {
      image-rendering: pixelated;
      width: 128px;
      height: 128px;
      border: 1px solid #d9dee3;
      background: #f3f6f8;
    }
    .preview-grid figcaption { margin-top: 6px; font-size: 0.9rem; }
  </style>
</head>
<body>
  <h1>Dental DICOM Privacy Toolkit Demo Summary</h1>
  <p class="warning">
    Synthetic demo only. This workflow demonstrates privacy risk reduction, auditability,
    packaging, and verification. It is not a legal compliance guarantee.
  </p>
  <h2>Pipeline Result</h2>
  <ul>
    <li>
      Validation:
      <span class="ok">{{ "passed" if result.validation_passed else "failed" }}</span>
    </li>
    <li>
      Audit chain:
      <span class="ok">{{ "passed" if result.audit_chain_passed else "failed" }}</span>
    </li>
    <li>Package entries: {{ result.package_entries }}</li>
    <li>Generated at: {{ result.generated_at }}</li>
  </ul>
  <h2>Pixel Previews</h2>
  <div class="preview-grid">
    {% for item in preview_images %}
    <figure>
      <img src="{{ item.src }}" alt="{{ item.label }}">
      <figcaption>{{ item.label }}</figcaption>
    </figure>
    {% endfor %}
  </div>
  <h2>Artifacts</h2>
  <table>
    <thead><tr><th>Artifact</th><th>Path</th></tr></thead>
    <tbody>
      <tr><td>Input synthetic DICOM</td><td><code>{{ result.input_dicom }}</code></td></tr>
      <tr><td>Inventory JSON</td><td><code>{{ result.inventory_json }}</code></td></tr>
      <tr><td>Inventory CSV</td><td><code>{{ result.inventory_csv }}</code></td></tr>
      <tr><td>Inventory HTML</td><td><code>{{ result.inventory_html }}</code></td></tr>
      <tr><td>Input preview PNG</td><td><code>{{ result.input_preview_png }}</code></td></tr>
      <tr>
        <td>Anonymized preview PNG</td>
        <td><code>{{ result.anonymized_preview_png }}</code></td>
      </tr>
      <tr>
        <td>Pixel-redacted preview PNG</td>
        <td><code>{{ result.redacted_preview_png }}</code></td>
      </tr>
      <tr><td>Anonymized DICOM</td><td><code>{{ result.anonymized_dicom }}</code></td></tr>
      <tr><td>Pixel-redacted DICOM</td><td><code>{{ result.redacted_dicom }}</code></td></tr>
      <tr><td>Inspection HTML</td><td><code>{{ result.inspection_html }}</code></td></tr>
      <tr><td>Anonymization audit HTML</td><td><code>{{ result.audit_html }}</code></td></tr>
      <tr><td>Validation JSON</td><td><code>{{ result.validation_json }}</code></td></tr>
      <tr><td>Redaction audit JSON</td><td><code>{{ result.redaction_json }}</code></td></tr>
      <tr><td>Encrypted package</td><td><code>{{ result.package_path }}</code></td></tr>
      <tr><td>Package manifest</td><td><code>{{ result.manifest_json }}</code></td></tr>
      <tr><td>Package key</td><td><code>{{ result.key_path }}</code></td></tr>
      <tr><td>Package receipt JSON</td><td><code>{{ result.package_receipt_json }}</code></td></tr>
      <tr><td>Package receipt HTML</td><td><code>{{ result.package_receipt_html }}</code></td></tr>
      <tr><td>Audit chain</td><td><code>{{ result.audit_chain_json }}</code></td></tr>
      <tr>
        <td>Audit chain verification</td>
        <td><code>{{ result.audit_chain_verify_json }}</code></td>
      </tr>
    </tbody>
  </table>
</body>
</html>
"""
)

BATCH_SUMMARY_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Batch Summary</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Batch Summary</h1>
  <p class="warning">
    Synthetic-data-oriented workflow. Review all outputs before external sharing.
  </p>
  <ul>
    <li>Input directory: <code>{{ summary.input_dir }}</code></li>
    <li>Output directory: <code>{{ summary.output_dir }}</code></li>
    <li>Profile: {{ summary.profile }}</li>
    <li>Total files: {{ summary.total_files }}</li>
    <li>Processed files: {{ summary.processed_files }}</li>
    <li>Failed files: {{ summary.failed_files }}</li>
    <li>Validation failures: {{ summary.validation_failures }}</li>
    <li>Generated at: {{ summary.generated_at }}</li>
  </ul>
  <table>
    <thead>
      <tr>
        <th>Input</th>
        <th>Output</th>
        <th>Validation</th>
        <th>Error</th>
      </tr>
    </thead>
    <tbody>
      {% for item in summary.files %}
      <tr>
        <td><code>{{ item.input_path }}</code></td>
        <td><code>{{ item.output_path or "" }}</code></td>
        <td class="{{ "ok" if item.validation_passed else "fail" }}">
          {{ "passed" if item.validation_passed else "failed" }}
        </td>
        <td>{{ item.error or "" }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

INVENTORY_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Inventory Report</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2 { color: #123; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Inventory Report</h1>
  <p class="warning">
    Inventory is a read-only preflight scan. It records presence, counts, hashes, and
    risk signals without exporting raw patient names or IDs.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Root directory: <code>{{ report.root_dir }}</code></li>
    <li>Total files: {{ report.total_files }}</li>
    <li>Readable files: {{ report.readable_files }}</li>
    <li>Unreadable files: {{ report.unreadable_files }}</li>
    <li>High-risk tags: {{ report.high_risk_tags }}</li>
    <li>Medium-risk tags: {{ report.medium_risk_tags }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Modalities</h2>
  <table>
    <thead><tr><th>Modality</th><th>Files</th></tr></thead>
    <tbody>
      {% for modality, count in report.modalities.items() %}
      <tr><td>{{ modality }}</td><td>{{ count }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
  <h2>Files</h2>
  <table>
    <thead>
      <tr>
        <th>Path</th>
        <th>Readable</th>
        <th>Modality</th>
        <th>Size</th>
        <th>Patient Fields</th>
        <th>Risk Tags</th>
        <th>Recommended Actions</th>
        <th>Error</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.files %}
      <tr>
        <td><code>{{ item.path }}</code></td>
        <td class="{{ "ok" if item.readable else "fail" }}">
          {{ "yes" if item.readable else "no" }}
        </td>
        <td>{{ item.modality or "" }}</td>
        <td>
          {% if item.rows and item.columns %}
          {{ item.rows }} x {{ item.columns }}
          {% endif %}
        </td>
        <td>
          name={{ item.patient_name_present }},
          id={{ item.patient_id_present }},
          birth_date={{ item.patient_birth_date_present }}
        </td>
        <td>high={{ item.high_risk_tags }}, medium={{ item.medium_risk_tags }}</td>
        <td>{{ ", ".join(item.recommended_actions) }}</td>
        <td>{{ item.error or "" }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

WORKFLOW_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Workflow Report</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2 { color: #123; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Workflow Report</h1>
  <p class="warning">
    Synthetic-data workflow report only. This report records pipeline execution and
    artifacts; it is not legal certification or clinical validation.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Name: {{ report.name }}</li>
    <li>Recipe: <code>{{ report.recipe_path }}</code></li>
    <li>Root directory: <code>{{ report.root_dir }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "fail" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Steps</h2>
  <table>
    <thead>
      <tr>
        <th>Step</th>
        <th>Action</th>
        <th>Status</th>
        <th>Message</th>
        <th>Artifacts</th>
      </tr>
    </thead>
    <tbody>
      {% for step in report.steps %}
      <tr>
        <td>{{ step.id }}</td>
        <td>{{ step.action }}</td>
        <td class="{{ "ok" if step.passed else "fail" }}">
          {{ "PASS" if step.passed else "FAIL" }}
        </td>
        <td>{{ step.message }}</td>
        <td>
          {% for artifact in step.artifacts %}
          <code>{{ artifact }}</code>{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

RELEASE_AUDIT_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Release Audit</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2 { color: #123; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Release Audit</h1>
  <p class="warning">
    Public-release readiness check for a synthetic-data-only open-source repository.
    This is not clinical, legal, regulatory, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Root directory: <code>{{ report.root_dir }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "fail" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Passed checks: {{ report.passed_checks }}</li>
    <li>Failed checks: {{ report.failed_checks }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Checks</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Check</th>
        <th>Category</th>
        <th>Message</th>
        <th>Evidence</th>
      </tr>
    </thead>
    <tbody>
      {% for check in report.checks %}
      <tr>
        <td class="{{ "ok" if check.passed else "fail" }}">
          {{ "PASS" if check.passed else "FAIL" }}
        </td>
        <td>{{ check.id }}</td>
        <td>{{ check.category }}</td>
        <td>{{ check.message }}</td>
        <td>
          {% for item in check.evidence %}
          <code>{{ item }}</code>{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

EVIDENCE_BUNDLE_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Evidence Bundle</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2 { color: #123; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
    a { color: #0b65c2; }
  </style>
</head>
<body>
  <h1>Dental DICOM Evidence Bundle</h1>
  <p class="warning">
    Synthetic-data evidence bundle for local demonstration and open-source review.
    It is not clinical, legal, regulatory, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Repository root: <code>{{ result.repository_root }}</code></li>
    <li>Output directory: <code>{{ result.output_dir }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if result.passed else "fail" }}">
        {{ "PASS" if result.passed else "FAIL" }}
      </span>
    </li>
    <li>Doctor: {{ "PASS" if result.doctor_passed else "FAIL" }}</li>
    <li>Safety scan: {{ "PASS" if result.safety_passed else "FAIL" }}</li>
    <li>Release audit: {{ "PASS" if result.release_audit_passed else "FAIL" }}</li>
    <li>Demo workflow: {{ "PASS" if result.demo_passed else "FAIL" }}</li>
    <li>YAML workflow: {{ "PASS" if result.workflow_passed else "FAIL" }}</li>
    <li>Generated at: {{ result.generated_at }}</li>
  </ul>
  <h2>Artifacts</h2>
  <table>
    <thead>
      <tr>
        <th>Category</th>
        <th>Artifact</th>
        <th>Path</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      {% for item in result.artifacts %}
      <tr>
        <td>{{ item.category }}</td>
        <td>{{ item.label }}</td>
        <td><a href="../{{ item.path }}"><code>{{ item.path }}</code></a></td>
        <td>{{ item.description }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

PACKAGE_RECEIPT_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Package Verification Receipt</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2 { color: #123; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Package Verification Receipt</h1>
  <p class="warning">
    Synthetic-data sharing receipt. This confirms package integrity checks only;
    it is not legal, regulatory, clinical, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Package: <code>{{ receipt.package_path }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if receipt.passed else "fail" }}">
        {{ "PASS" if receipt.passed else "FAIL" }}
      </span>
    </li>
    <li>Package SHA-256: <code>{{ receipt.package_sha256 }}</code></li>
    <li>Key provided: {{ receipt.key_provided }}</li>
    <li>Manifest package name: {{ receipt.package_name or "" }}</li>
    <li>Encrypted: {{ receipt.encrypted }}</li>
    <li>Entries: {{ receipt.entries|length }}</li>
    <li>Total entry bytes: {{ receipt.total_size_bytes }}</li>
    <li>Generated at: {{ receipt.generated_at }}</li>
  </ul>
  {% if receipt.errors %}
  <h2>Errors</h2>
  <ul>
    {% for error in receipt.errors %}
    <li>{{ error }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  <h2>Manifest Entries</h2>
  <table>
    <thead>
      <tr>
        <th>Path</th>
        <th>Size</th>
        <th>SHA-256</th>
      </tr>
    </thead>
    <tbody>
      {% for item in receipt.entries %}
      <tr>
        <td><code>{{ item.path }}</code></td>
        <td>{{ item.size_bytes }}</td>
        <td><code>{{ item.sha256 }}</code></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)


def write_inspection_html(path: Path, report: InspectionReport) -> None:
    _write_html(path, INSPECTION_TEMPLATE.render(report=report))


def write_audit_html(path: Path, audit: AnonymizationAudit) -> None:
    _write_html(path, AUDIT_TEMPLATE.render(audit=audit))


def write_demo_summary_html(path: Path, result: DemoPipelineResult) -> None:
    preview_images = [
        {"label": "Input", "src": Path(result.input_preview_png).name},
        {"label": "Anonymized", "src": Path(result.anonymized_preview_png).name},
        {"label": "Pixel-redacted", "src": Path(result.redacted_preview_png).name},
    ]
    _write_html(
        path,
        DEMO_SUMMARY_TEMPLATE.render(result=result, preview_images=preview_images),
    )


def write_batch_summary_html(path: Path, summary: BatchSummary) -> None:
    _write_html(path, BATCH_SUMMARY_TEMPLATE.render(summary=summary))


def write_inventory_html(path: Path, report: InventoryReport) -> None:
    _write_html(path, INVENTORY_TEMPLATE.render(report=report))


def write_workflow_html(path: Path, report: WorkflowRunReport) -> None:
    _write_html(path, WORKFLOW_TEMPLATE.render(report=report))


def write_release_audit_html(path: Path, report: ReleaseAuditReport) -> None:
    _write_html(path, RELEASE_AUDIT_TEMPLATE.render(report=report))


def write_evidence_bundle_html(path: Path, result: EvidenceBundleResult) -> None:
    _write_html(path, EVIDENCE_BUNDLE_TEMPLATE.render(result=result))


def write_package_receipt_html(path: Path, receipt: PackageVerificationReceipt) -> None:
    _write_html(path, PACKAGE_RECEIPT_TEMPLATE.render(receipt=receipt))


def _write_html(path: Path, html: str) -> None:
    ensure_parent(path)
    path.write_text(html, encoding="utf-8")


def model_to_dict(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")
