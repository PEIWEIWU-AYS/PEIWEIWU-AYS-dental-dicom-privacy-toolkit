from __future__ import annotations

import os
import subprocess
from pathlib import Path

from ddpt.models import (
    PublishPreflightCheck,
    PublishPreflightReport,
    PublishPreflightStep,
)
from ddpt.safety import scan_repository_safety

DEFAULT_OWNER = "PEIWEIWU-AYS"
DEFAULT_REPO_SLUG = "dental-dicom-privacy-toolkit"
DEFAULT_DESCRIPTION = (
    "Dental DICOM anonymization, de-identification, privacy regression, "
    "audit evidence, and encrypted sharing toolkit."
)
SUGGESTED_TOPICS = [
    "dicom",
    "dental-imaging",
    "medical-imaging",
    "dicom-anonymization",
    "de-identification",
    "dicom-confidentiality",
    "orthanc",
    "dcmodify",
    "privacy",
    "privacy-regression",
    "pseudonymization",
    "local-first",
    "healthcare",
    "dentistry",
    "open-source-healthcare",
]


def build_publish_preflight(
    root_dir: Path,
    owner: str = DEFAULT_OWNER,
    repo_slug: str = DEFAULT_REPO_SLUG,
    check_remote: bool = False,
) -> PublishPreflightReport:
    root = root_dir.resolve()
    expected_remote_url = f"https://github.com/{owner}/{repo_slug}.git"

    git_repo = _git(root, "rev-parse", "--is-inside-work-tree")
    branch = _git(root, "branch", "--show-current")
    head = _git(root, "rev-parse", "--short", "HEAD")
    status = _git(root, "status", "--short")
    remote = _git(root, "remote", "get-url", "origin")
    git_user_name = _git(root, "config", "user.name")
    git_user_email = _git(root, "config", "user.email")

    checks: list[PublishPreflightCheck] = [
        _check(
            "git-repository",
            "git",
            "pass" if git_repo.output == "true" else "fail",
            "Local folder is a Git repository."
            if git_repo.output == "true"
            else "Local folder is not a Git repository.",
            [git_repo.output or git_repo.error],
        ),
        _check(
            "git-identity",
            "git",
            "pass" if git_user_name.output and git_user_email.output else "fail",
            "Git commit identity is configured."
            if git_user_name.output and git_user_email.output
            else "Git commit identity is missing.",
            [
                f"user.name={git_user_name.output}",
                f"user.email={git_user_email.output}",
            ],
        ),
        _check(
            "current-branch",
            "git",
            "pass" if branch.output and head.output else "fail",
            "Current branch and HEAD commit are available."
            if branch.output and head.output
            else "Current branch or HEAD commit could not be read.",
            [f"branch={branch.output}", f"head={head.output or head.error}"],
        ),
        _check(
            "clean-working-tree",
            "git",
            "pass" if status.output == "" and status.returncode == 0 else "action-required",
            "Working tree is clean."
            if status.output == ""
            else "Commit or intentionally ignore local changes before publishing.",
            status.output.splitlines() if status.output else ["clean"],
        ),
        _remote_config_check(remote.output, expected_remote_url),
        _readme_check(root),
        _discoverability_check(root),
        _ci_check(root),
        _safety_check(root),
    ]
    if check_remote:
        checks.append(_remote_exists_check(root))
    else:
        checks.append(
            _check(
                "remote-exists",
                "github",
                "not-checked",
                "Remote existence was not checked. Use --check-remote before pushing.",
                [expected_remote_url],
            )
        )

    blocking_failure = any(check.status == "fail" for check in checks)
    remote_ready = any(
        check.id == "remote-exists" and check.status == "pass" for check in checks
    )
    clean_tree = any(
        check.id == "clean-working-tree" and check.status == "pass" for check in checks
    )
    passed = not blocking_failure
    ready_to_push = passed and remote_ready and clean_tree

    return PublishPreflightReport(
        root_dir=str(root),
        owner=owner,
        repo_slug=repo_slug,
        expected_remote_url=expected_remote_url,
        remote_url=remote.output or None,
        default_branch=branch.output or None,
        head_sha=head.output or None,
        git_user_name=git_user_name.output or None,
        git_user_email=git_user_email.output or None,
        public_description=DEFAULT_DESCRIPTION,
        suggested_topics=SUGGESTED_TOPICS,
        check_remote=check_remote,
        passed=passed,
        ready_to_push=ready_to_push,
        checks=checks,
        create_repository_steps=_create_repository_steps(owner, repo_slug),
        push_commands=[
            f"git remote set-url origin {expected_remote_url}",
            "git push -u origin main",
        ],
    )


class _CommandResult:
    def __init__(self, returncode: int, output: str, error: str) -> None:
        self.returncode = returncode
        self.output = output.strip()
        self.error = error.strip()


def _git(root_dir: Path, *args: str) -> _CommandResult:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _CommandResult(1, "", str(exc))
    return _CommandResult(result.returncode, result.stdout, result.stderr)


def _remote_exists_check(root_dir: Path) -> PublishPreflightCheck:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--exit-code", "origin", "HEAD"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _check(
            "remote-exists",
            "github",
            "action-required",
            "Remote repository could not be checked.",
            [str(exc)],
        )
    evidence = [line for line in (result.stdout + result.stderr).splitlines() if line.strip()]
    if result.returncode == 0:
        return _check(
            "remote-exists",
            "github",
            "pass",
            "GitHub remote exists and is reachable.",
            evidence or ["git ls-remote succeeded"],
        )
    return _check(
        "remote-exists",
        "github",
        "action-required",
        "GitHub remote is not reachable. Create the repository or confirm access.",
        evidence or [f"git ls-remote exited with {result.returncode}"],
    )


def _remote_config_check(remote_url: str, expected_remote_url: str) -> PublishPreflightCheck:
    if not remote_url:
        return _check(
            "remote-url",
            "github",
            "action-required",
            "No origin remote is configured.",
            [f"expected={expected_remote_url}"],
        )
    status = "pass" if remote_url == expected_remote_url else "warning"
    return _check(
        "remote-url",
        "github",
        status,
        "Origin remote matches the expected GitHub repository."
        if status == "pass"
        else "Origin remote differs from the expected GitHub repository.",
        [f"origin={remote_url}", f"expected={expected_remote_url}"],
    )


def _readme_check(root_dir: Path) -> PublishPreflightCheck:
    readme = _read(root_dir / "README.md")
    required = [
        "Dental DICOM Privacy Toolkit | 牙科 DICOM 脱敏加密共享工具包",
        "Keywords:",
        "DICOM anonymization",
        "隐私回归测试",
        "Suggested GitHub Topics",
        "synthetic",
    ]
    missing = [term for term in required if term not in readme]
    return _check(
        "readme-discoverability",
        "discoverability",
        "pass" if not missing else "fail",
        "README has bilingual naming, keywords, topics, and synthetic safety language."
        if not missing
        else "README is missing required discoverability language.",
        missing or required,
    )


def _discoverability_check(root_dir: Path) -> PublishPreflightCheck:
    doc = _read(root_dir / "docs" / "discoverability.md")
    required = [
        "Dental DICOM Privacy Toolkit",
        "牙科 DICOM 脱敏加密共享工具包",
        "GitHub Topics",
        "Target Search Phrases",
    ]
    missing = [term for term in required if term not in doc]
    return _check(
        "discoverability-doc",
        "discoverability",
        "pass" if not missing else "fail",
        "Discoverability documentation is ready for public GitHub setup."
        if not missing
        else "Discoverability documentation is incomplete.",
        missing or required,
    )


def _ci_check(root_dir: Path) -> PublishPreflightCheck:
    ci = _read(root_dir / ".github" / "workflows" / "ci.yml")
    required = ["ruff check .", "pytest", "python -m ddpt release audit"]
    missing = [term for term in required if term not in ci]
    return _check(
        "github-actions",
        "automation",
        "pass" if not missing else "fail",
        "GitHub Actions workflow includes lint, tests, and release audit."
        if not missing
        else "GitHub Actions workflow is missing core public gates.",
        missing or required,
    )


def _safety_check(root_dir: Path) -> PublishPreflightCheck:
    report = scan_repository_safety(root_dir)
    return _check(
        "repository-safety",
        "safety",
        "pass" if report.passed else "fail",
        f"Repository safety scan passed across {report.scanned_files} files."
        if report.passed
        else f"Repository safety scan found {len(report.findings)} issue(s).",
        [f"{finding.rule_id}: {finding.path}" for finding in report.findings]
        or [f"scanned_files={report.scanned_files}"],
    )


def _create_repository_steps(owner: str, repo_slug: str) -> list[PublishPreflightStep]:
    return [
        PublishPreflightStep(
            order=1,
            title="Create empty GitHub repository",
            command=f"https://github.com/new?owner={owner}&name={repo_slug}",
            note="Use Public visibility. Do not initialize README, .gitignore, or license.",
        ),
        PublishPreflightStep(
            order=2,
            title="Paste public description",
            command=DEFAULT_DESCRIPTION,
            note="Keep the description concise and keyword-rich without clinical claims.",
        ),
        PublishPreflightStep(
            order=3,
            title="Add GitHub topics",
            command=" ".join(SUGGESTED_TOPICS),
            note="Topics are added after the repository exists, from the repository About panel.",
        ),
        PublishPreflightStep(
            order=4,
            title="Push local main branch",
            command=f"git push -u https://github.com/{owner}/{repo_slug}.git main",
            note="Run from the local repository after GitHub repository creation.",
        ),
    ]


def _check(
    check_id: str,
    category: str,
    status: str,
    message: str,
    evidence: list[str],
) -> PublishPreflightCheck:
    return PublishPreflightCheck(
        id=check_id,
        category=category,
        status=status,  # type: ignore[arg-type]
        passed=status in {"pass", "warning", "not-checked", "action-required"},
        message=message,
        evidence=evidence,
    )


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")
