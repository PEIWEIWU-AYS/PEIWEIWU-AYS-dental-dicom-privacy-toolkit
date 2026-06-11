from __future__ import annotations

from pathlib import Path

import yaml

from ddpt.models import ReleaseAuditCheck, ReleaseAuditReport
from ddpt.policy import profile_coverage
from ddpt.safety import scan_repository_safety

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "ROADMAP.md",
    "pyproject.toml",
    ".gitignore",
    ".github/workflows/ci.yml",
    "docs/capability-matrix.md",
    "docs/competitor-analysis.md",
    "docs/data-safety.md",
    "docs/demo-guide.md",
    "docs/deid-certificate.md",
    "docs/discoverability.md",
    "docs/evidence-bundle.md",
    "docs/linkable-research-profile.md",
    "docs/local-workbench.md",
    "docs/macbook-validation.md",
    "docs/objective-completion-audit.md",
    "docs/package-verification-receipts.md",
    "docs/profile-comparison.md",
    "docs/profile-lint.md",
    "docs/pixel-review.md",
    "docs/product-requirements.md",
    "docs/project-blueprint.md",
    "docs/release-audit.md",
    "docs/research-sharing-profile.md",
    "docs/review-dashboard.md",
    "docs/deid-comparison.md",
    "docs/share-readiness.md",
    "docs/synthetic-study.md",
    "profiles/dental-basic.yml",
    "profiles/dental-linkable-research.yml",
    "profiles/dental-pixel-redaction.yml",
    "profiles/dental-research-sharing.yml",
    "recipes/dental-demo-workflow.yml",
    "scripts/generate_demo_assets.py",
    "tests/test_cli_workflow.py",
]

README_KEYWORDS = [
    "Dental DICOM Privacy Toolkit",
    "牙科 DICOM 脱敏加密共享工具包",
    "Keywords:",
    "dental DICOM",
    "DICOM anonymization",
    "DICOM de-identification",
    "de-identification certificate",
    "deterministic pseudonymization",
    "local browser workbench",
    "objective completion audit",
    "encrypted DICOM sharing",
    "CBCT",
    "牙科DICOM",
    "DICOM脱敏",
    "去标识化证明书",
    "DICOM伪名化",
    "本地工作台",
    "原始目标完成度审计",
    "患者隐私保护",
    "Suggested GitHub Topics",
    "synthetic",
]

DOCUMENTED_COMMANDS = [
    "ddpt doctor",
    "ddpt safety scan",
    "ddpt release audit",
    "ddpt capability matrix",
    "ddpt completion audit",
    "ddpt evidence bundle",
    "ddpt dashboard build",
    "ddpt compare deid",
    "ddpt certificate create",
    "ddpt share readiness",
    "ddpt workflow run",
    "ddpt api serve",
    "ddpt synthetic-study",
    "ddpt inventory",
    "ddpt anonymize",
    "ddpt preview",
    "ddpt pixel-review",
    "ddpt redact-pixels",
    "ddpt tag dump",
    "ddpt policy export",
    "ddpt profile coverage",
    "ddpt profile compare",
    "ddpt profile lint",
    "ddpt package",
    "ddpt verify",
    "ddpt decrypt",
]

COMPETITOR_TERMS = [
    "RSNA DICOM Anonymizer",
    "DicomCleaner",
    "Orthanc",
    "RSNA CTP",
    "DCMTK",
    "pydicom",
]

REQUIRED_SOURCE_MODULES = [
    "src/ddpt/anonymize.py",
    "src/ddpt/api.py",
    "src/ddpt/audit_chain.py",
    "src/ddpt/batch.py",
    "src/ddpt/capability.py",
    "src/ddpt/certificate.py",
    "src/ddpt/completion.py",
    "src/ddpt/dashboard.py",
    "src/ddpt/deid_compare.py",
    "src/ddpt/doctor.py",
    "src/ddpt/evidence.py",
    "src/ddpt/inventory.py",
    "src/ddpt/pixel_review.py",
    "src/ddpt/pixels.py",
    "src/ddpt/preview.py",
    "src/ddpt/release.py",
    "src/ddpt/reports.py",
    "src/ddpt/safety.py",
    "src/ddpt/share_readiness.py",
    "src/ddpt/sharing.py",
    "src/ddpt/tag_ops.py",
    "src/ddpt/validation.py",
    "src/ddpt/workbench.py",
    "src/ddpt/workflow.py",
]

PYPROJECT_TERMS = [
    'name = "dental-dicom-privacy-toolkit"',
    "pydicom",
    "cryptography",
    "fastapi",
    "jinja2",
    "pillow",
    "pyyaml",
    "typer",
    "pytest",
    "ruff",
]

CI_TERMS = [
    "python -m ddpt doctor",
    "python -m ddpt safety scan",
    "python -m ddpt release audit",
    "python -m ddpt capability matrix",
    "python -m ddpt completion audit",
    "python -m ddpt profile lint",
    "python -m ddpt profile lint dental-linkable-research",
    "python -m ddpt evidence bundle",
    "python -m ddpt compare deid",
    "python -m ddpt certificate create",
    "python -m ddpt share readiness",
    "python -m ddpt dashboard build",
    "ruff check .",
    "pytest",
]

WORKFLOW_ACTIONS = {
    "synthetic",
    "inventory",
    "inspect",
    "anonymize",
    "validate",
    "preview",
    "redact-pixels",
    "compare-deid",
    "package",
    "verify-package",
    "audit-chain",
    "audit-verify",
    "share-readiness",
}

PROFILE_COVERAGE_FILES = [
    "profiles/dental-basic.yml",
    "profiles/dental-research-sharing.yml",
    "profiles/dental-linkable-research.yml",
]


def run_release_audit(root_dir: Path) -> ReleaseAuditReport:
    root_dir = root_dir.resolve()
    checks = [
        _required_files_check(root_dir),
        _readme_discoverability_check(root_dir),
        _readme_commands_check(root_dir),
        _competitor_learning_check(root_dir),
        _source_modules_check(root_dir),
        _pyproject_metadata_check(root_dir),
        _ci_check(root_dir),
        _workflow_recipe_check(root_dir),
        _profile_coverage_check(root_dir),
        _repository_safety_check(root_dir),
    ]
    return ReleaseAuditReport(
        root_dir=str(root_dir),
        passed=all(check.passed for check in checks),
        checks=checks,
    )


def _required_files_check(root_dir: Path) -> ReleaseAuditCheck:
    missing = [path for path in REQUIRED_FILES if not (root_dir / path).is_file()]
    if missing:
        return _check(
            "required-files",
            "repository",
            False,
            f"Missing {len(missing)} required public project file(s).",
            missing,
        )
    return _check(
        "required-files",
        "repository",
        True,
        f"Found {len(REQUIRED_FILES)} required public project files.",
        REQUIRED_FILES,
    )


def _readme_discoverability_check(root_dir: Path) -> ReleaseAuditCheck:
    readme = _read_text(root_dir / "README.md")
    missing = [term for term in README_KEYWORDS if term not in readme]
    stale_status = "Initial project skeleton" in readme
    if missing or stale_status:
        evidence = missing.copy()
        if stale_status:
            evidence.append("README status still says Initial project skeleton")
        return _check(
            "readme-discoverability",
            "discoverability",
            False,
            "README first screen is missing bilingual/keyword/safety signals.",
            evidence,
        )
    return _check(
        "readme-discoverability",
        "discoverability",
        True,
        "README includes bilingual naming, keywords, topics, and synthetic-data safety language.",
        README_KEYWORDS,
    )


def _readme_commands_check(root_dir: Path) -> ReleaseAuditCheck:
    readme = _read_text(root_dir / "README.md")
    missing = [command for command in DOCUMENTED_COMMANDS if command not in readme]
    return _term_check(
        "readme-commands",
        "documentation",
        missing,
        "README documents the core CLI workflow commands.",
        "README is missing one or more core CLI workflow commands.",
    )


def _competitor_learning_check(root_dir: Path) -> ReleaseAuditCheck:
    analysis = _read_text(root_dir / "docs" / "competitor-analysis.md")
    missing = [term for term in COMPETITOR_TERMS if term not in analysis]
    return _term_check(
        "competitor-learning",
        "strategy",
        missing,
        "Competitor analysis covers the named reference tools.",
        "Competitor analysis does not cover all required reference tools.",
    )


def _source_modules_check(root_dir: Path) -> ReleaseAuditCheck:
    missing = [path for path in REQUIRED_SOURCE_MODULES if not (root_dir / path).is_file()]
    if missing:
        return _check(
            "source-modules",
            "implementation",
            False,
            "Missing one or more implementation modules.",
            missing,
        )
    return _check(
        "source-modules",
        "implementation",
        True,
        "Core implementation modules are present.",
        REQUIRED_SOURCE_MODULES,
    )


def _pyproject_metadata_check(root_dir: Path) -> ReleaseAuditCheck:
    pyproject = _read_text(root_dir / "pyproject.toml")
    missing = [term for term in PYPROJECT_TERMS if term not in pyproject]
    return _term_check(
        "pyproject-metadata",
        "packaging",
        missing,
        "Package metadata and runtime/dev dependencies are declared.",
        "Package metadata or required dependencies are missing.",
    )


def _ci_check(root_dir: Path) -> ReleaseAuditCheck:
    ci = _read_text(root_dir / ".github" / "workflows" / "ci.yml")
    missing = [term for term in CI_TERMS if term not in ci]
    return _term_check(
        "ci-workflow",
        "automation",
        missing,
        "CI includes doctor, release audit, safety scan, lint, and tests.",
        "CI is missing one or more required gates.",
    )


def _workflow_recipe_check(root_dir: Path) -> ReleaseAuditCheck:
    recipe_path = root_dir / "recipes" / "dental-demo-workflow.yml"
    if not recipe_path.is_file():
        return _check(
            "workflow-recipe",
            "workflow",
            False,
            "Workflow recipe file is missing.",
            [str(recipe_path)],
        )

    data = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
    steps = data.get("steps") if isinstance(data, dict) else None
    if not isinstance(steps, list):
        return _check(
            "workflow-recipe",
            "workflow",
            False,
            "Workflow recipe does not contain a steps list.",
            [str(recipe_path)],
        )

    actions = {str(step.get("action")) for step in steps if isinstance(step, dict)}
    missing = sorted(WORKFLOW_ACTIONS - actions)
    if missing:
        return _check(
            "workflow-recipe",
            "workflow",
            False,
            "Workflow recipe is missing required staged actions.",
            missing,
        )
    return _check(
        "workflow-recipe",
        "workflow",
        True,
        "Workflow recipe covers the complete synthetic privacy pipeline.",
        sorted(actions),
    )


def _profile_coverage_check(root_dir: Path) -> ReleaseAuditCheck:
    missing = [path for path in PROFILE_COVERAGE_FILES if not (root_dir / path).is_file()]
    if missing:
        return _check(
            "profile-coverage",
            "privacy-profile",
            False,
            "One or more built-in profile files are missing.",
            missing,
        )

    coverage_reports = [
        profile_coverage(str(root_dir / path)) for path in PROFILE_COVERAGE_FILES
    ]
    uncovered = [
        f"{report.profile}: {keyword}"
        for report in coverage_reports
        for keyword in report.high_risk_uncovered + report.medium_risk_uncovered
    ]
    if uncovered:
        return _check(
            "profile-coverage",
            "privacy-profile",
            False,
            "One or more built-in profiles do not cover all high/medium risk policy items.",
            uncovered,
        )
    evidence = [
        f"{report.profile}: {report.covered_items}/{report.total_items} covered"
        for report in coverage_reports
    ]
    return _check(
        "profile-coverage",
        "privacy-profile",
        True,
        "Built-in profiles cover all high/medium risk policy items.",
        evidence,
    )


def _repository_safety_check(root_dir: Path) -> ReleaseAuditCheck:
    report = scan_repository_safety(root_dir)
    if not report.passed:
        return _check(
            "repository-safety",
            "safety",
            False,
            f"Safety scan found {len(report.findings)} issue(s).",
            [f"{finding.rule_id}: {finding.path}" for finding in report.findings],
        )
    return _check(
        "repository-safety",
        "safety",
        True,
        f"Safety scan passed across {report.scanned_files} public files.",
        [f"scanned_files={report.scanned_files}"],
    )


def _term_check(
    check_id: str,
    category: str,
    missing: list[str],
    pass_message: str,
    fail_message: str,
) -> ReleaseAuditCheck:
    return _check(
        check_id,
        category,
        not missing,
        pass_message if not missing else fail_message,
        missing,
    )


def _check(
    check_id: str,
    category: str,
    passed: bool,
    message: str,
    evidence: list[str],
) -> ReleaseAuditCheck:
    return ReleaseAuditCheck(
        id=check_id,
        category=category,
        passed=passed,
        message=message,
        evidence=evidence,
    )


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")
