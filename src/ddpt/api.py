from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from ddpt import __version__
from ddpt.anonymize import anonymize_dicom
from ddpt.dicom_json import export_dicom_json
from ddpt.inspection import inspect_dicom
from ddpt.inventory import build_inventory
from ddpt.pipeline import run_demo_pipeline
from ddpt.preview import render_dicom_preview
from ddpt.profiles import built_in_profiles
from ddpt.reports import model_to_dict
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
