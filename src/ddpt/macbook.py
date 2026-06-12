from __future__ import annotations

from pathlib import Path

from ddpt.capability import build_capability_matrix
from ddpt.competitor import build_competitor_coverage
from ddpt.completion import run_objective_audit
from ddpt.doctor import run_doctor
from ddpt.evidence import run_evidence_bundle
from ddpt.models import MacBookValidationCheck, MacBookValidationReport
from ddpt.publish import build_publish_preflight
from ddpt.release import run_release_audit


def run_macbook_validation(
    repository_root: Path,
    output_dir: Path,
    *,
    check_remote: bool = True,
    require_remote: bool = False,
) -> MacBookValidationReport:
    root = repository_root.resolve()
    output = output_dir.resolve()
    evidence_dir = output / "evidence-run"
    dashboard_html = evidence_dir / "reports" / "review-dashboard.html"
    output.mkdir(parents=True, exist_ok=True)

    checks: list[MacBookValidationCheck] = []

    doctor_report = run_doctor()
    checks.append(
        _check(
            "environment-doctor",
            "environment",
            doctor_report.passed,
            "Python runtime and required modules are available."
            if doctor_report.passed
            else "Python runtime or required modules are missing.",
            [
                f"python={doctor_report.python_version}",
                f"platform={doctor_report.platform}",
                f"package={doctor_report.package_version}",
            ],
        )
    )

    release_report = run_release_audit(root)
    checks.append(
        _check(
            "release-audit",
            "release",
            release_report.passed,
            f"Release audit passed {release_report.passed_checks}/"
            f"{len(release_report.checks)} checks.",
            ["ddpt release audit ."],
        )
    )

    capability_report = build_capability_matrix(root)
    checks.append(
        _check(
            "capability-matrix",
            "strategy",
            capability_report.passed,
            f"Competitor-informed capabilities implemented: "
            f"{capability_report.implemented_items}/{capability_report.total_items}.",
            ["ddpt capability matrix --root ."],
        )
    )

    competitor_report = build_competitor_coverage(root)
    checks.append(
        _check(
            "competitor-coverage",
            "strategy",
            competitor_report.passed,
            f"Reference tools covered: {competitor_report.covered_tools}/"
            f"{competitor_report.total_tools}.",
            ["ddpt competitor coverage --root ."],
        )
    )

    objective_report = run_objective_audit(root)
    checks.append(
        _check(
            "objective-completion",
            "objective",
            objective_report.passed,
            f"Original objective audit passed {objective_report.passed_items}/"
            f"{objective_report.total_items} requirements.",
            ["ddpt completion audit ."],
        )
    )

    try:
        evidence_report = run_evidence_bundle(root, evidence_dir)
        evidence_passed = evidence_report.passed
        evidence_message = (
            f"Evidence bundle generated with {len(evidence_report.artifacts)} artifacts."
        )
        evidence_paths = [
            str(evidence_dir / "reports" / "evidence-bundle.html"),
            str(dashboard_html),
        ]
    except Exception as exc:  # pragma: no cover - exercised through report status
        evidence_passed = False
        evidence_message = f"Evidence bundle generation failed: {exc}"
        evidence_paths = [str(evidence_dir)]
    checks.append(
        _check(
            "evidence-bundle",
            "evidence",
            evidence_passed,
            evidence_message,
            evidence_paths,
        )
    )

    dashboard_passed = dashboard_html.is_file()
    checks.append(
        _check(
            "review-dashboard",
            "evidence",
            dashboard_passed,
            "MacBook review dashboard is available."
            if dashboard_passed
            else "MacBook review dashboard is missing.",
            [str(dashboard_html)],
        )
    )

    publish_report = build_publish_preflight(root, check_remote=check_remote)
    if publish_report.ready_to_push:
        publish_status = "pass"
        publish_passed = True
        publish_message = "GitHub remote exists and the local repository is ready to push."
    elif publish_report.failed_checks:
        publish_status = "fail"
        publish_passed = False
        publish_message = "GitHub publish preflight has blocking failures."
    else:
        publish_status = "action-required"
        publish_passed = not require_remote
        publish_message = (
            "Local validation passed, but GitHub repository creation or access is still required."
        )
    checks.append(
        MacBookValidationCheck(
            id="github-publish-preflight",
            category="publishing",
            status=publish_status,
            required=require_remote,
            passed=publish_passed,
            message=publish_message,
            evidence=[
                publish_report.expected_remote_url,
                f"ready_to_push={publish_report.ready_to_push}",
                f"check_remote={publish_report.check_remote}",
            ],
        )
    )

    local_passed = all(
        check.passed for check in checks if check.id != "github-publish-preflight"
    )
    github_ready = publish_report.ready_to_push
    passed = local_passed and (github_ready if require_remote else True)

    return MacBookValidationReport(
        root_dir=str(root),
        output_dir=str(output),
        evidence_dir=str(evidence_dir),
        dashboard_html=str(dashboard_html),
        local_passed=local_passed,
        github_ready=github_ready,
        require_remote=require_remote,
        passed=passed,
        checks=checks,
        next_steps=_next_steps(local_passed, github_ready, require_remote),
    )


def _check(
    check_id: str,
    category: str,
    passed: bool,
    message: str,
    evidence: list[str],
) -> MacBookValidationCheck:
    return MacBookValidationCheck(
        id=check_id,
        category=category,
        status="pass" if passed else "fail",
        required=True,
        passed=passed,
        message=message,
        evidence=evidence,
    )


def _next_steps(
    local_passed: bool,
    github_ready: bool,
    require_remote: bool,
) -> list[str]:
    steps: list[str] = []
    if local_passed:
        steps.append("Open the review dashboard HTML and inspect the generated reports.")
    else:
        steps.append("Fix failed local checks, then rerun `ddpt macbook validate`.")
    if github_ready:
        steps.append("Push the local main branch to GitHub.")
    else:
        steps.append(
            "Create the empty GitHub repository "
            "PEIWEIWU-AYS/PEIWEIWU-AYS-dental-dicom-privacy-toolkit, "
            "then rerun with `--check-remote`."
        )
    if require_remote and not github_ready:
        steps.append("Remote publishing is required for this run, so overall status is FAIL.")
    return steps
