from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Template

from ddpt.models import AnonymizationAudit, InspectionReport
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
      <tr><th>Risk</th><th>Tag</th><th>Keyword</th><th>Name</th><th>Value</th><th>Reason</th></tr>
    </thead>
    <tbody>
      {% for item in report.findings %}
      <tr>
        <td class="{{ item.risk }}">{{ item.risk }}</td>
        <td>{{ item.tag }}</td>
        <td>{{ item.keyword }}</td>
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


def write_inspection_html(path: Path, report: InspectionReport) -> None:
    _write_html(path, INSPECTION_TEMPLATE.render(report=report))


def write_audit_html(path: Path, audit: AnonymizationAudit) -> None:
    _write_html(path, AUDIT_TEMPLATE.render(audit=audit))


def _write_html(path: Path, html: str) -> None:
    ensure_parent(path)
    path.write_text(html, encoding="utf-8")


def model_to_dict(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")
