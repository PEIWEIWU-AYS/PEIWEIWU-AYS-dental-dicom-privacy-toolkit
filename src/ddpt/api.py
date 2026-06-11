from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ddpt import __version__
from ddpt.anonymize import anonymize_dicom
from ddpt.inspection import inspect_dicom
from ddpt.inventory import build_inventory
from ddpt.preview import render_dicom_preview
from ddpt.reports import model_to_dict
from ddpt.validation import validate_anonymized_dicom


class PathRequest(BaseModel):
    path: str


class AnonymizeRequest(BaseModel):
    input_path: str
    output_path: str
    profile: str = "dental-basic"


class PreviewRequest(BaseModel):
    input_path: str
    output_path: str
    max_size: int = 512


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
                "/inventory",
                "/inspect",
                "/anonymize",
                "/validate",
                "/preview",
            ],
        }

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "version": __version__}

    @app.post("/inventory")
    def inventory(request: PathRequest) -> dict:
        directory = _resolve_inside_root(root, request.path)
        return model_to_dict(build_inventory(directory))

    @app.post("/inspect")
    def inspect(request: PathRequest) -> dict:
        dicom_path = _resolve_inside_root(root, request.path)
        return model_to_dict(inspect_dicom(dicom_path))

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
