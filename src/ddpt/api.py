from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from ddpt import __version__
from ddpt.anonymize import anonymize_dicom
from ddpt.competitor import build_competitor_coverage
from ddpt.dicom_json import export_dicom_json
from ddpt.filename_privacy import scan_filename_privacy
from ddpt.inspection import inspect_dicom
from ddpt.inventory import build_inventory
from ddpt.pipeline import run_demo_pipeline
from ddpt.pixel_risk import scan_pixel_risk
from ddpt.preview import render_dicom_preview
from ddpt.profiles import built_in_profiles
from ddpt.publish import DEFAULT_OWNER, DEFAULT_REPO_SLUG, build_publish_preflight
from ddpt.regression import run_privacy_regression_suite
from ddpt.remediation import build_privacy_remediation_plan
from ddpt.reports import (
    model_to_dict,
    write_filename_privacy_html,
    write_pixel_risk_scan_html,
    write_privacy_regression_html,
    write_privacy_remediation_html,
    write_publish_preflight_html,
)
from ddpt.utils import write_json
from ddpt.validation import validate_anonymized_dicom
from ddpt.workbench import render_workbench_html


class PathRequest(BaseModel):
    path: str


class DicomJsonRequest(BaseModel):
    path: str
    include_values: bool = False


class AnonymizeRequest(BaseModel):
    input_path: str
    output_path: str
    profile: str = "dental-basic"


class PreviewRequest(BaseModel):
    input_path: str
    output_path: str
    max_size: int = 512


class FilenameScanRequest(BaseModel):
    path: str
    recursive: bool = True
    json_path: str = "reports/api-filename-privacy.json"
    html_path: str = "reports/api-filename-privacy.html"


class RemediationPlanRequest(BaseModel):
    path: str
    profile: str = "dental-basic"
    recursive: bool = True
    json_path: str = "reports/api-remediation-plan.json"
    html_path: str = "reports/api-remediation-plan.html"


class PixelRiskRequest(BaseModel):
    path: str
    json_path: str = "reports/api-pixel-risk.json"
    html_path: str = "reports/api-pixel-risk.html"


class RegressionSuiteRequest(BaseModel):
    output_dir: str = "api-regression-run"


class PublishPreflightRequest(BaseModel):
    owner: str = DEFAULT_OWNER
    repo_slug: str = DEFAULT_REPO_SLUG
    check_remote: bool = False
    json_path: str = "reports/api-publish-preflight.json"
    html_path: str = "reports/api-publish-preflight.html"


class DemoRequest(BaseModel):
    output_dir: str = "workbench-demo"
    profile: str = "dental-basic"
    rect: str = "1,0,1,1"


def create_api_app(root_dir: Path) -> FastAPI:
    root = root_dir.resolve()
    app = FastAPI(
        title="Dental DICOM Privacy Toolkit API",
        version=__version__,
        description=(
            "Local synthetic-data-oriented REST API for dental DICOM privacy "
            "workflow integration demos."
        ),
    )

    @app.get("/")
    def root_info() -> dict:
        return {
            "name": "Dental DICOM Privacy Toolkit API",
            "version": __version__,
            "root_dir": str(root),
            "safety": (
                "Local demo API only. Use synthetic or explicitly approved test DICOM files."
            ),
            "endpoints": [
                "/health",
                "/workbench",
                "/demo",
                "/inventory",
                "/inspect",
                "/dicom-json",
                "/filename-scan",
                "/remediation-plan",
                "/pixel-risk",
                "/regression-suite",
                "/publish-preflight",
                "/competitor-coverage",
                "/anonymize",
                "/validate",
                "/preview",
                "/files/{path}",
            ],
        }

    @app.get("/workbench", response_class=HTMLResponse)
    def workbench() -> str:
        return render_workbench_html(root, built_in_profiles())

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "version": __version__}

    @app.post("/demo")
    def demo(request: DemoRequest) -> dict:
        output_dir = _resolve_inside_root(root, request.output_dir)
        result = run_demo_pipeline(output_dir, profile=request.profile, rectangle=request.rect)
        return model_to_dict(result)

    @app.post("/inventory")
    def inventory(request: PathRequest) -> dict:
        directory = _resolve_inside_root(root, request.path)
        return model_to_dict(build_inventory(directory))

    @app.post("/inspect")
    def inspect(request: PathRequest) -> dict:
        dicom_path = _resolve_inside_root(root, request.path)
        return model_to_dict(inspect_dicom(dicom_path))

    @app.post("/dicom-json")
    def dicom_json(request: DicomJsonRequest) -> dict:
        dicom_path = _resolve_inside_root(root, request.path)
        return model_to_dict(
            export_dicom_json(dicom_path, include_values=request.include_values)
        )

    @app.post("/filename-scan")
    def filename_scan(request: FilenameScanRequest) -> dict:
        input_path = _resolve_inside_root(root, request.path)
        json_path = _resolve_inside_root(root, request.json_path)
        html_path = _resolve_inside_root(root, request.html_path)
        report = scan_filename_privacy(input_path, recursive=request.recursive)
        write_json(json_path, model_to_dict(report))
        write_filename_privacy_html(html_path, report)
        return _with_api_artifacts(root, report, json_path, html_path)

    @app.post("/remediation-plan")
    def remediation_plan(request: RemediationPlanRequest) -> dict:
        input_path = _resolve_inside_root(root, request.path)
        json_path = _resolve_inside_root(root, request.json_path)
        html_path = _resolve_inside_root(root, request.html_path)
        report = build_privacy_remediation_plan(
            input_path,
            profile=request.profile,
            recursive=request.recursive,
        )
        write_json(json_path, model_to_dict(report))
        write_privacy_remediation_html(html_path, report)
        return _with_api_artifacts(root, report, json_path, html_path)

    @app.post("/pixel-risk")
    def pixel_risk(request: PixelRiskRequest) -> dict:
        dicom_path = _resolve_inside_root(root, request.path)
        json_path = _resolve_inside_root(root, request.json_path)
        html_path = _resolve_inside_root(root, request.html_path)
        report = scan_pixel_risk(dicom_path)
        write_json(json_path, model_to_dict(report))
        write_pixel_risk_scan_html(html_path, report)
        return _with_api_artifacts(root, report, json_path, html_path)

    @app.post("/regression-suite")
    def regression_suite(request: RegressionSuiteRequest) -> dict:
        output_dir = _resolve_inside_root(root, request.output_dir)
        report = run_privacy_regression_suite(output_dir)
        json_path = output_dir / "reports" / "privacy-regression-suite.json"
        html_path = output_dir / "reports" / "privacy-regression-suite.html"
        write_json(json_path, model_to_dict(report))
        write_privacy_regression_html(html_path, report)
        return _with_api_artifacts(root, report, json_path, html_path)

    @app.post("/publish-preflight")
    def publish_preflight(request: PublishPreflightRequest) -> dict:
        repository_root = _find_repository_root(root) or root
        json_path = _resolve_inside_root(root, request.json_path)
        html_path = _resolve_inside_root(root, request.html_path)
        report = build_publish_preflight(
            repository_root,
            owner=request.owner,
            repo_slug=request.repo_slug,
            check_remote=request.check_remote,
        )
        write_json(json_path, model_to_dict(report))
        write_publish_preflight_html(html_path, report)
        return _with_api_artifacts(root, report, json_path, html_path)

    @app.get("/competitor-coverage")
    def competitor_coverage() -> dict:
        repository_root = _find_repository_root(root)
        if repository_root is None:
            raise HTTPException(
                status_code=400,
                detail="API root is not inside a DDPT repository checkout.",
            )
        return model_to_dict(build_competitor_coverage(repository_root))

    @app.post("/anonymize")
    def anonymize(request: AnonymizeRequest) -> dict:
        input_path = _resolve_inside_root(root, request.input_path)
        output_path = _resolve_inside_root(root, request.output_path)
        audit = anonymize_dicom(input_path, output_path, request.profile)
        return model_to_dict(audit)

    @app.post("/validate")
    def validate(request: PathRequest) -> dict:
        dicom_path = _resolve_inside_root(root, request.path)
        return model_to_dict(validate_anonymized_dicom(dicom_path))

    @app.post("/preview")
    def preview(request: PreviewRequest) -> dict:
        input_path = _resolve_inside_root(root, request.input_path)
        output_path = _resolve_inside_root(root, request.output_path)
        report = render_dicom_preview(input_path, output_path, max_size=request.max_size)
        return model_to_dict(report)

    @app.get("/files/{file_path:path}")
    def files(file_path: str) -> FileResponse:
        path = _resolve_inside_root(root, file_path)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path)

    return app


def _with_api_artifacts(root: Path, report, json_path: Path, html_path: Path) -> dict:
    data = model_to_dict(report)
    data["_api_artifacts"] = {
        "json": _relative_path(root, json_path),
        "html": _relative_path(root, html_path),
    }
    return data


def _resolve_inside_root(root: Path, value: str) -> Path:
    requested = Path(value)
    if requested.is_absolute():
        candidate = requested.resolve()
    else:
        candidate = (root / requested).resolve()

    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Path must stay inside API root") from exc
    return candidate


def _relative_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def _find_repository_root(start: Path) -> Path | None:
    for candidate in [start.resolve(), *start.resolve().parents]:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "src" / "ddpt"
        ).is_dir():
            return candidate
    return None
