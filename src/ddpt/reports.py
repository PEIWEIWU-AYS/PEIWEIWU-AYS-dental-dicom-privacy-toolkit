from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Template

from ddpt.models import (
    AnonymizationAudit,
    BatchSummary,
    CapabilityMatrixReport,
    DeidentificationCertificate,
    DeidentificationComparisonReport,
    DemoPipelineResult,
    EvidenceBundleResult,
    InspectionReport,
    InventoryReport,
    ObjectiveAuditReport,
    PackageVerificationReceipt,
    PixelReviewReport,
    PolicyRegistryReport,
    PrivacyRemediationPlanReport,
    ProfileComparisonReport,
    ProfileLintReport,
    ReleaseAuditReport,
    ReviewDashboardReport,
    ShareReadinessReport,
    WorkflowQualityGateReport,
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
      <tr>
        <td>De-identification comparison HTML</td>
        <td><code>{{ result.deid_comparison_html }}</code></td>
      </tr>
      <tr><td>Validation JSON</td><td><code>{{ result.validation_json }}</code></td></tr>
      <tr>
        <td>Share readiness HTML</td>
        <td><code>{{ result.share_readiness_html }}</code></td>
      </tr>
      <tr><td>Pixel review JSON</td><td><code>{{ result.pixel_review_json }}</code></td></tr>
      <tr><td>Pixel review HTML</td><td><code>{{ result.pixel_review_html }}</code></td></tr>
      <tr><td>Redaction audit JSON</td><td><code>{{ result.redaction_json }}</code></td></tr>
      <tr><td>Encrypted package</td><td><code>{{ result.package_path }}</code></td></tr>
      <tr><td>Package manifest</td><td><code>{{ result.manifest_json }}</code></td></tr>
      <tr><td>Package key</td><td><code>{{ result.key_path }}</code></td></tr>
      <tr><td>Package receipt JSON</td><td><code>{{ result.package_receipt_json }}</code></td></tr>
      <tr><td>Package receipt HTML</td><td><code>{{ result.package_receipt_html }}</code></td></tr>
      <tr>
        <td>De-identification certificate JSON</td>
        <td><code>{{ result.deid_certificate_json }}</code></td>
      </tr>
      <tr>
        <td>De-identification certificate HTML</td>
        <td><code>{{ result.deid_certificate_html }}</code></td>
      </tr>
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
    <li>De-identification comparison failures: {{ summary.comparison_failures }}</li>
    <li>Generated at: {{ summary.generated_at }}</li>
  </ul>
  <table>
    <thead>
      <tr>
        <th>Input</th>
        <th>Output</th>
        <th>Validation</th>
        <th>De-id Comparison</th>
        <th>Evidence</th>
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
        <td class="{{ "ok" if item.deid_comparison_passed else "fail" }}">
          {{ "passed" if item.deid_comparison_passed else "failed" }}
        </td>
        <td>
          {% if item.inspection_json %}<code>{{ item.inspection_json }}</code><br>{% endif %}
          {% if item.audit_json %}<code>{{ item.audit_json }}</code><br>{% endif %}
          {% if item.validation_json %}<code>{{ item.validation_json }}</code><br>{% endif %}
          {% if item.deid_comparison_json %}<code>{{ item.deid_comparison_json }}</code>{% endif %}
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

WORKFLOW_QUALITY_GATE_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Workflow Quality Gate</title>
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
    .optional { color: #4b5563; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Workflow Quality Gate</h1>
  <p class="warning">
    Synthetic-data workflow gate for reproducibility and public review. It checks
    report evidence already generated by the toolkit; it is not clinical,
    regulatory, legal, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Root directory: <code>{{ report.root_dir }}</code></li>
    <li>Workflow report: <code>{{ report.workflow_report_path or "" }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "fail" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Required checks: {{ report.passed_checks }} / {{ report.required_checks }}</li>
    <li>Failed required checks: {{ report.failed_checks }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Gate Checks</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Required</th>
        <th>Check</th>
        <th>Stage</th>
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
        <td class="{{ "optional" if not check.required else "" }}">
          {{ "yes" if check.required else "optional" }}
        </td>
        <td>{{ check.id }}</td>
        <td>{{ check.stage }}</td>
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

PRIVACY_REMEDIATION_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Privacy Remediation Plan</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
    }
    h1, h2, h3 { color: #123; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    .high { color: #b00020; font-weight: 700; }
    .medium { color: #8a5a00; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Privacy Remediation Plan</h1>
  <p class="warning">
    Synthetic-data planning report only. This plan helps explain metadata and
    pixel-review work before anonymization; it is not legal, clinical,
    regulatory, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Input: <code>{{ report.input_path }}</code></li>
    <li>Profile: <code>{{ report.profile }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "fail" }}">
        {{ "PASS" if report.passed else "REVIEW" }}
      </span>
    </li>
    <li>Files: {{ report.readable_files }} readable / {{ report.total_files }} total</li>
    <li>Covered items: {{ report.covered_items }} / {{ report.total_items }}</li>
    <li>Uncovered high-risk items: {{ report.uncovered_high_risk_items }}</li>
    <li>Uncovered medium-risk items: {{ report.uncovered_medium_risk_items }}</li>
    <li>Private tags present: {{ report.private_tags_present }}</li>
    <li>Pixel review recommended files: {{ report.pixel_review_recommended_files }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Next Steps</h2>
  <ul>
    {% for step in report.next_steps %}
    <li>{{ step }}</li>
    {% endfor %}
  </ul>
  <h2>Files</h2>
  {% for file in report.files %}
  <h3><code>{{ file.path }}</code></h3>
  <ul>
    <li>Readable: {{ file.readable }}</li>
    <li>Modality: {{ file.modality or "unknown" }}</li>
    <li>High-risk items: {{ file.high_risk_items }}</li>
    <li>Medium-risk items: {{ file.medium_risk_items }}</li>
    <li>Uncovered high-risk items: {{ file.uncovered_high_risk_items }}</li>
    <li>Uncovered medium-risk items: {{ file.uncovered_medium_risk_items }}</li>
    <li>Private tags present: {{ file.private_tags_present }}</li>
    <li>BurnedInAnnotation: {{ file.burned_in_annotation or "missing" }}</li>
    <li>Pixel review recommended: {{ file.pixel_review_recommended }}</li>
    {% if file.error %}<li>Error: {{ file.error }}</li>{% endif %}
  </ul>
  {% if file.items %}
  <table>
    <thead>
      <tr>
        <th>Covered</th>
        <th>Risk</th>
        <th>Tag</th>
        <th>Keyword</th>
        <th>Recommended</th>
        <th>Profile</th>
        <th>DICOM Code</th>
        <th>Value</th>
        <th>Note</th>
      </tr>
    </thead>
    <tbody>
      {% for item in file.items %}
      <tr>
        <td class="{{ "ok" if item.covered_by_profile else "fail" }}">
          {{ "yes" if item.covered_by_profile else "no" }}
        </td>
        <td class="{{ item.risk }}">{{ item.risk }}</td>
        <td>{{ item.tag }}</td>
        <td>{{ item.keyword }}</td>
        <td>{{ item.recommended_action }}</td>
        <td>{{ item.profile_action }}</td>
        <td>{{ item.dicom_action_code }}</td>
        <td>{{ item.current_value }}</td>
        <td>{{ item.note }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}
  {% endfor %}
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

CAPABILITY_MATRIX_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Capability Matrix</title>
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
    .implemented { color: #1f6f43; font-weight: 700; }
    .partial { color: #8a5a00; font-weight: 700; }
    .missing { color: #b00020; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
    a { color: #0b65c2; }
  </style>
</head>
<body>
  <h1>Dental DICOM Capability Matrix</h1>
  <p class="warning">
    Competitor-informed capability audit for an open-source dental DICOM privacy toolkit.
    This report maps public project claims to repository evidence. It is not clinical,
    legal, regulatory, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Repository root: <code>{{ report.root_dir }}</code></li>
    <li>
      Overall:
      <span class="{{ "implemented" if report.passed else "missing" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Implemented: {{ report.implemented_items }} / {{ report.total_items }}</li>
    <li>Partial: {{ report.partial_items }}</li>
    <li>Missing: {{ report.missing_items }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Reference Tools</h2>
  <table>
    <thead>
      <tr>
        <th>Tool</th>
        <th>Category</th>
        <th>Strengths</th>
        <th>Gaps for This Toolkit</th>
      </tr>
    </thead>
    <tbody>
      {% for tool in report.references %}
      <tr>
        <td><a href="{{ tool.url }}">{{ tool.name }}</a></td>
        <td>{{ tool.category }}</td>
        <td>
          {% for item in tool.strengths %}
          {{ item }}{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
        <td>
          {% for item in tool.gaps_for_dental_toolkit %}
          {{ item }}{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  <h2>Capability Evidence</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Capability</th>
        <th>Learned From</th>
        <th>Differentiator</th>
        <th>Evidence</th>
        <th>Missing Evidence</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.items %}
      <tr>
        <td class="{{ item.status }}">{{ item.status }}</td>
        <td>{{ item.capability }}<br><small>{{ item.note }}</small></td>
        <td>
          {% for tool in item.source_tools %}
          {{ tool }}{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
        <td>{{ item.differentiator }}</td>
        <td>
          {% for evidence in item.evidence %}
          <code>{{ evidence }}</code>{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
        <td>
          {% for evidence in item.missing_evidence %}
          <code>{{ evidence }}</code>{% if not loop.last %}<br>{% endif %}
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

OBJECTIVE_AUDIT_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Objective Completion Audit</title>
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
  <h1>Dental DICOM Objective Completion Audit</h1>
  <p class="warning">
    Requirement-by-requirement audit against the original competitor-learning
    objective. This report maps claims to local repository evidence. It is not
    clinical, legal, regulatory, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Repository root: <code>{{ report.root_dir }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "fail" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Passed items: {{ report.passed_items }} / {{ report.total_items }}</li>
    <li>Failed items: {{ report.failed_items }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Requirement Evidence</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Category</th>
        <th>Requirement</th>
        <th>Evidence</th>
        <th>Missing Evidence</th>
        <th>Note</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.items %}
      <tr>
        <td class="{{ "ok" if item.passed else "fail" }}">
          {{ "PASS" if item.passed else "FAIL" }}
        </td>
        <td>{{ item.category }}<br><code>{{ item.id }}</code></td>
        <td>{{ item.requirement }}</td>
        <td>
          {% for evidence in item.evidence %}
          <code>{{ evidence }}</code>{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
        <td>
          {% for evidence in item.missing_evidence %}
          <code>{{ evidence }}</code>{% if not loop.last %}<br>{% endif %}
          {% endfor %}
        </td>
        <td>{{ item.note }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

REVIEW_DASHBOARD_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Review Dashboard</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 32px;
      color: #17202a;
      background: #fbfcfd;
    }
    h1, h2 { color: #123; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; background: white; }
    th, td { border: 1px solid #d9dee3; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f3f6f8; }
    .warning { padding: 12px; background: #fff3cd; border: 1px solid #ffe08a; border-radius: 6px; }
    .ok { color: #1f6f43; font-weight: 700; }
    .fail { color: #b00020; font-weight: 700; }
    .quick-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }
    .quick-card {
      border: 1px solid #d9dee3;
      background: white;
      border-radius: 6px;
      padding: 12px;
    }
    .quick-card a { color: #0b65c2; font-weight: 700; text-decoration: none; }
    .preview-grid { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }
    .preview-grid figure { margin: 0; background: white; border: 1px solid #d9dee3; padding: 10px; }
    .preview-grid img {
      image-rendering: pixelated;
      width: 180px;
      height: 180px;
      object-fit: contain;
      background: #f3f6f8;
      border: 1px solid #d9dee3;
    }
    .preview-grid figcaption { margin-top: 6px; font-size: 0.9rem; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
    a { color: #0b65c2; }
  </style>
</head>
<body>
  <h1>Dental DICOM Review Dashboard</h1>
  <p class="warning">
    Local static dashboard for synthetic-data review. It gathers the strongest
    reports from the evidence bundle into one MacBook-friendly page. It is not
    clinical, legal, regulatory, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Evidence directory: <code>{{ report.evidence_dir }}</code></li>
    <li>Output path: <code>{{ report.output_path }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "fail" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Evidence bundle: {{ "PASS" if report.evidence_bundle_passed else "FAIL" }}</li>
    <li>Artifacts available: {{ report.available_artifacts }} / {{ report.total_artifacts }}</li>
    <li>Missing artifacts: {{ report.missing_artifacts }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Open First</h2>
  <div class="quick-grid">
    {% for item in quick_links %}
    <div class="quick-card">
      <a href="{{ item.href }}">{{ item.label }}</a>
      <p>{{ item.description }}</p>
    </div>
    {% endfor %}
  </div>
  <h2>Visual Previews</h2>
  <div class="preview-grid">
    {% for item in preview_links %}
    {% if item.exists %}
    <figure>
      <img src="{{ item.href }}" alt="{{ item.label }}">
      <figcaption>{{ item.label }}</figcaption>
    </figure>
    {% endif %}
    {% endfor %}
  </div>
  <h2>All Evidence Artifacts</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Category</th>
        <th>Artifact</th>
        <th>Path</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      {% for item in artifact_links %}
      <tr>
        <td class="{{ "ok" if item.exists else "fail" }}">
          {{ "available" if item.exists else "missing" }}
        </td>
        <td>{{ item.category }}</td>
        <td>{{ item.label }}</td>
        <td>
          {% if item.exists %}
          <a href="{{ item.href }}"><code>{{ item.path }}</code></a>
          {% else %}
          <code>{{ item.path }}</code>
          {% endif %}
        </td>
        <td>{{ item.description }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

DEID_COMPARISON_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM De-identification Comparison</title>
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
    .high { color: #b00020; font-weight: 700; }
    .medium { color: #8a5a00; font-weight: 700; }
    .low { color: #1f6f43; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM De-identification Comparison</h1>
  <p class="warning">
    Before/after comparison for synthetic-data de-identification review. This
    report explains observed metadata changes and residual policy items. It is
    not legal, regulatory, clinical, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Source: <code>{{ report.source_path }}</code></li>
    <li>Anonymized: <code>{{ report.anonymized_path }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "fail" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Passed policy items: {{ report.passed_items }} / {{ report.total_items }}</li>
    <li>Changed items: {{ report.changed_items }}</li>
    <li>Removed items: {{ report.removed_items }}</li>
    <li>Unchanged items: {{ report.unchanged_items }}</li>
    <li>Private tags before: {{ report.private_tags_before }}</li>
    <li>Private tags after: {{ report.private_tags_after }}</li>
    <li>Pixel data changed: {{ report.pixel_data_changed }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  {% if report.residual_high_risk_keywords or report.residual_medium_risk_keywords %}
  <h2>Residual Risk Keywords</h2>
  <ul>
    <li>High risk: {{ report.residual_high_risk_keywords|join(", ") }}</li>
    <li>Medium risk: {{ report.residual_medium_risk_keywords|join(", ") }}</li>
  </ul>
  {% endif %}
  <h2>Policy Item Comparison</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Pass</th>
        <th>Risk</th>
        <th>Keyword</th>
        <th>Recommended</th>
        <th>Before</th>
        <th>After</th>
        <th>Note</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.items %}
      <tr>
        <td>{{ item.status }}</td>
        <td class="{{ "ok" if item.passed else "fail" }}">
          {{ "yes" if item.passed else "no" }}
        </td>
        <td class="{{ item.risk }}">{{ item.risk }}</td>
        <td><code>{{ item.keyword }}</code></td>
        <td>{{ item.recommended_action }}</td>
        <td>{{ item.before }}</td>
        <td>{{ item.after }}</td>
        <td>{{ item.note }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

SHARE_READINESS_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Share Readiness</title>
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
  <h1>Dental DICOM Share Readiness</h1>
  <p class="warning">
    Local synthetic-data sharing readiness gate. This report checks whether the
    demo artifacts needed for privacy review, package verification, and audit
    traceability are present and passing. It is not legal, regulatory, clinical,
    or security certification.
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
    <li>Passed checks: {{ report.passed_checks }} / {{ report.checks|length }}</li>
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

DEID_CERTIFICATE_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM De-identification Certificate</title>
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
  <h1>Dental DICOM De-identification Certificate</h1>
  <p class="warning">
    Synthetic-data certificate for local demonstration and collaborator review.
    This summarizes project evidence only; it is not legal, regulatory,
    clinical, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Root directory: <code>{{ certificate.root_dir }}</code></li>
    <li>
      Overall:
      <span class="{{ "ok" if certificate.passed else "fail" }}">
        {{ "PASS" if certificate.passed else "FAIL" }}
      </span>
    </li>
    <li>Profile: <code>{{ certificate.profile }}</code></li>
    <li>Input: <code>{{ certificate.input_path }}</code></li>
    <li>Anonymized: <code>{{ certificate.anonymized_path }}</code></li>
    <li>Checks: {{ certificate.passed_checks }} / {{ certificate.total_checks }}</li>
    <li>Private tags after: {{ certificate.private_tags_after }}</li>
    <li>Residual high-risk keywords: {{ certificate.residual_high_risk_keywords|join(", ") }}</li>
    <li>
      Residual medium-risk keywords:
      {{ certificate.residual_medium_risk_keywords|join(", ") }}
    </li>
    <li>Pixel review regions: {{ certificate.pixel_review_regions }}</li>
    <li>Package entries: {{ certificate.package_entries }}</li>
    <li>Package: <code>{{ certificate.package_path or "" }}</code></li>
    <li>Package SHA-256: <code>{{ certificate.package_sha256 or "" }}</code></li>
    <li>Share readiness: {{ "PASS" if certificate.share_readiness_passed else "FAIL" }}</li>
    <li>Generated at: {{ certificate.generated_at }}</li>
  </ul>
  <h2>Evidence Checks</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Check</th>
        <th>Category</th>
        <th>Summary</th>
        <th>Evidence</th>
      </tr>
    </thead>
    <tbody>
      {% for check in certificate.checks %}
      <tr>
        <td class="{{ "ok" if check.passed else "fail" }}">
          {{ "PASS" if check.passed else "FAIL" }}
        </td>
        <td>{{ check.id }}</td>
        <td>{{ check.category }}</td>
        <td>{{ check.summary }}</td>
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

PROFILE_COMPARISON_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Profile Comparison</title>
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
    .changed { color: #8a5a00; font-weight: 700; }
    .same { color: #1f6f43; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Profile Comparison</h1>
  <p class="warning">
    Synthetic-data profile comparison. This explains configuration differences;
    it is not legal, regulatory, clinical, or security certification.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Baseline: {{ report.baseline_profile }}</li>
    <li>Candidate: {{ report.candidate_profile }}</li>
    <li>Changed items: {{ report.changed_items }} / {{ report.total_items }}</li>
    <li>Baseline coverage: {{ report.baseline_covered_items }} / {{ report.total_items }}</li>
    <li>Candidate coverage: {{ report.candidate_covered_items }} / {{ report.total_items }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Policy Items</h2>
  <table>
    <thead>
      <tr>
        <th>Changed</th>
        <th>Risk</th>
        <th>Keyword</th>
        <th>Category</th>
        <th>Recommended</th>
        <th>Baseline</th>
        <th>Candidate</th>
        <th>Note</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.items %}
      <tr>
        <td class="{{ "changed" if item.changed else "same" }}">
          {{ "yes" if item.changed else "no" }}
        </td>
        <td>{{ item.risk }}</td>
        <td>{{ item.keyword }}</td>
        <td>{{ item.category }}</td>
        <td>{{ item.recommended_action }}</td>
        <td>{{ item.baseline_action }}</td>
        <td>{{ item.candidate_action }}</td>
        <td>{{ item.note }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

POLICY_REGISTRY_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Policy Registry</title>
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
    .high { color: #b00020; font-weight: 700; }
    .medium { color: #8a5a00; font-weight: 700; }
    .low { color: #1f6f43; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Policy Registry</h1>
  <p class="warning">
    DICOM PS3.15-inspired dental privacy baseline for explanation and testing.
    This is not regulatory certification or complete DICOM conformance.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Source: {{ report.source }}</li>
    <li>Total items: {{ report.total_items }}</li>
    <li>High-risk items: {{ report.high_risk_items }}</li>
    <li>Medium-risk items: {{ report.medium_risk_items }}</li>
    <li>Low-risk items: {{ report.low_risk_items }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Policy Items</h2>
  <table>
    <thead>
      <tr>
        <th>Risk</th>
        <th>Keyword</th>
        <th>Category</th>
        <th>Recommended</th>
        <th>DICOM Code</th>
        <th>Reason</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.items %}
      <tr>
        <td class="{{ item.risk }}">{{ item.risk }}</td>
        <td><code>{{ item.keyword }}</code></td>
        <td>{{ item.category }}</td>
        <td>{{ item.recommended_action }}</td>
        <td>{{ item.dicom_action_code }}</td>
        <td>{{ item.reason }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""
)

PROFILE_LINT_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Profile Lint</title>
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
    .error { color: #b00020; font-weight: 700; }
    .warn { color: #8a5a00; font-weight: 700; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Profile Lint</h1>
  <p class="warning">
    Configuration lint report for anonymization profiles. Passing this lint check
    does not certify de-identification or legal compliance.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Profile: {{ report.profile }}</li>
    <li>
      Overall:
      <span class="{{ "ok" if report.passed else "error" }}">
        {{ "PASS" if report.passed else "FAIL" }}
      </span>
    </li>
    <li>Errors: {{ report.error_count }}</li>
    <li>Warnings: {{ report.warning_count }}</li>
    <li>Policy coverage: {{ report.covered_items }} / {{ report.total_policy_items }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Findings</h2>
  <table>
    <thead>
      <tr>
        <th>Severity</th>
        <th>Rule</th>
        <th>Keyword</th>
        <th>Message</th>
      </tr>
    </thead>
    <tbody>
      {% for item in report.findings %}
      <tr>
        <td class="{{ "error" if item.severity == "error" else "warn" }}">
          {{ item.severity }}
        </td>
        <td>{{ item.rule_id }}</td>
        <td>{{ item.keyword or "" }}</td>
        <td>{{ item.message }}</td>
      </tr>
      {% endfor %}
      {% if not report.findings %}
      <tr><td colspan="4" class="ok">No findings.</td></tr>
      {% endif %}
    </tbody>
  </table>
</body>
</html>
"""
)

PIXEL_REVIEW_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dental DICOM Pixel Review</title>
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
    .preview-grid { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }
    .preview-grid figure { margin: 0; }
    .preview-grid img {
      image-rendering: pixelated;
      width: 192px;
      height: 192px;
      object-fit: contain;
      border: 1px solid #d9dee3;
      background: #f3f6f8;
    }
    .preview-grid figcaption { margin-top: 6px; font-size: 0.9rem; }
    code { background: #f3f6f8; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Dental DICOM Pixel Review</h1>
  <p class="warning">
    Pixel review report for known redaction regions. This does not automatically
    detect every burned-in identifier and is not diagnostic interpretation.
  </p>
  <h2>Summary</h2>
  <ul>
    <li>Input: <code>{{ report.input_path }}</code></li>
    <li>Plan: <code>{{ report.plan_path or "" }}</code></li>
    <li>Pixel size: {{ report.columns }} x {{ report.rows }}</li>
    <li>Rendered size: {{ report.rendered_width }} x {{ report.rendered_height }}</li>
    <li>BurnedInAnnotation: {{ report.burned_in_annotation or "missing" }}</li>
    <li>Regions: {{ report.regions|length }}</li>
    <li>Generated at: {{ report.generated_at }}</li>
  </ul>
  <h2>Previews</h2>
  <div class="preview-grid">
    <figure>
      <img src="{{ original_src }}" alt="Original preview">
      <figcaption>Original</figcaption>
    </figure>
    <figure>
      <img src="{{ overlay_src }}" alt="Redaction overlay preview">
      <figcaption>Overlay</figcaption>
    </figure>
    <figure>
      <img src="{{ redacted_src }}" alt="Redacted preview">
      <figcaption>Redacted</figcaption>
    </figure>
  </div>
  <h2>Regions</h2>
  <table>
    <thead>
      <tr><th>Label</th><th>X</th><th>Y</th><th>Width</th><th>Height</th></tr>
    </thead>
    <tbody>
      {% for item in report.regions %}
      <tr>
        <td>{{ item.label }}</td>
        <td>{{ item.x }}</td>
        <td>{{ item.y }}</td>
        <td>{{ item.width }}</td>
        <td>{{ item.height }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  <h2>Warnings</h2>
  <ul>
    {% for warning in report.warnings %}
    <li>{{ warning }}</li>
    {% endfor %}
  </ul>
  <p>{{ report.note }}</p>
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


def write_workflow_quality_gate_html(
    path: Path,
    report: WorkflowQualityGateReport,
) -> None:
    _write_html(path, WORKFLOW_QUALITY_GATE_TEMPLATE.render(report=report))


def write_privacy_remediation_html(
    path: Path,
    report: PrivacyRemediationPlanReport,
) -> None:
    _write_html(path, PRIVACY_REMEDIATION_TEMPLATE.render(report=report))


def write_release_audit_html(path: Path, report: ReleaseAuditReport) -> None:
    _write_html(path, RELEASE_AUDIT_TEMPLATE.render(report=report))


def write_evidence_bundle_html(path: Path, result: EvidenceBundleResult) -> None:
    _write_html(path, EVIDENCE_BUNDLE_TEMPLATE.render(result=result))


def write_capability_matrix_html(path: Path, report: CapabilityMatrixReport) -> None:
    _write_html(path, CAPABILITY_MATRIX_TEMPLATE.render(report=report))


def write_objective_audit_html(path: Path, report: ObjectiveAuditReport) -> None:
    _write_html(path, OBJECTIVE_AUDIT_TEMPLATE.render(report=report))


def write_review_dashboard_html(path: Path, report: ReviewDashboardReport) -> None:
    artifact_links = [
        {
            "label": artifact.label,
            "category": artifact.category,
            "path": artifact.path,
            "description": artifact.description,
            "exists": artifact.exists,
            "href": _relative_html_src(path, Path(report.evidence_dir) / artifact.path),
        }
        for artifact in report.artifacts
    ]
    preview_links = [
        {
            "label": preview.label,
            "path": preview.path,
            "exists": preview.exists,
            "href": _relative_html_src(path, Path(report.evidence_dir) / preview.path),
        }
        for preview in report.previews
    ]
    quick_labels = {
        "Review dashboard HTML",
        "Evidence bundle HTML",
        "Demo summary HTML",
        "De-identification comparison HTML",
        "De-identification certificate HTML",
        "Share readiness HTML",
        "Capability matrix HTML",
        "Objective completion audit HTML",
        "Release audit HTML",
        "Pixel review HTML",
        "Package verification receipt",
    }
    quick_links = [item for item in artifact_links if item["label"] in quick_labels]
    _write_html(
        path,
        REVIEW_DASHBOARD_TEMPLATE.render(
            report=report,
            artifact_links=artifact_links,
            preview_links=preview_links,
            quick_links=quick_links,
        ),
    )


def write_deid_comparison_html(
    path: Path,
    report: DeidentificationComparisonReport,
) -> None:
    _write_html(path, DEID_COMPARISON_TEMPLATE.render(report=report))


def write_share_readiness_html(path: Path, report: ShareReadinessReport) -> None:
    _write_html(path, SHARE_READINESS_TEMPLATE.render(report=report))


def write_deid_certificate_html(path: Path, certificate: DeidentificationCertificate) -> None:
    _write_html(path, DEID_CERTIFICATE_TEMPLATE.render(certificate=certificate))


def write_package_receipt_html(path: Path, receipt: PackageVerificationReceipt) -> None:
    _write_html(path, PACKAGE_RECEIPT_TEMPLATE.render(receipt=receipt))


def write_profile_comparison_html(path: Path, report: ProfileComparisonReport) -> None:
    _write_html(path, PROFILE_COMPARISON_TEMPLATE.render(report=report))


def write_profile_lint_html(path: Path, report: ProfileLintReport) -> None:
    _write_html(path, PROFILE_LINT_TEMPLATE.render(report=report))


def write_policy_registry_html(path: Path, report: PolicyRegistryReport) -> None:
    _write_html(path, POLICY_REGISTRY_TEMPLATE.render(report=report))


def write_pixel_review_html(path: Path, report: PixelReviewReport) -> None:
    _write_html(
        path,
        PIXEL_REVIEW_TEMPLATE.render(
            report=report,
            original_src=_relative_html_src(path, Path(report.original_preview_png)),
            overlay_src=_relative_html_src(path, Path(report.overlay_preview_png)),
            redacted_src=_relative_html_src(path, Path(report.redacted_preview_png)),
        ),
    )


def _write_html(path: Path, html: str) -> None:
    ensure_parent(path)
    path.write_text(html, encoding="utf-8")


def _relative_html_src(html_path: Path, image_path: Path) -> str:
    try:
        return str(image_path.resolve().relative_to(html_path.parent.resolve()))
    except ValueError:
        return str(image_path)


def model_to_dict(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")
