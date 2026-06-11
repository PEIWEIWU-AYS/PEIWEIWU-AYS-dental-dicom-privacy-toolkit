from __future__ import annotations

from pathlib import Path

from ddpt.anonymize import anonymize_dicom
from ddpt.inspection import inspect_dicom
from ddpt.models import BatchFileResult, BatchSummary
from ddpt.reports import model_to_dict, write_batch_summary_html
from ddpt.utils import write_json
from ddpt.validation import validate_anonymized_dicom

DICOM_SUFFIXES = {".dcm", ".dicom"}


def find_dicom_files(input_dir: Path, recursive: bool = True) -> list[Path]:
    iterator = input_dir.rglob("*") if recursive else input_dir.glob("*")
    return sorted(
        path for path in iterator if path.is_file() and path.suffix.lower() in DICOM_SUFFIXES
    )


def run_batch_workflow(
    input_dir: Path,
    output_dir: Path,
    profile: str = "dental-basic",
    recursive: bool = True,
) -> BatchSummary:
    files = find_dicom_files(input_dir, recursive=recursive)
    results: list[BatchFileResult] = []
    reports_dir = output_dir / "reports"
    dicom_output_dir = output_dir / "dicom"

    for input_path in files:
        relative = input_path.relative_to(input_dir)
        stem = _safe_stem(relative)
        output_path = dicom_output_dir / relative.with_suffix(".anonymized.dcm")
        inspection_json = reports_dir / f"{stem}.inspect.json"
        audit_json = reports_dir / f"{stem}.audit.json"
        validation_json = reports_dir / f"{stem}.validation.json"

        try:
            inspection = inspect_dicom(input_path)
            write_json(inspection_json, model_to_dict(inspection))

            audit = anonymize_dicom(input_path, output_path, profile)
            write_json(audit_json, model_to_dict(audit))

            validation = validate_anonymized_dicom(output_path)
            write_json(validation_json, model_to_dict(validation))

            results.append(
                BatchFileResult(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    inspection_json=str(inspection_json),
                    audit_json=str(audit_json),
                    validation_json=str(validation_json),
                    validation_passed=validation.passed,
                )
            )
        except Exception as exc:  # pragma: no cover - defensive batch path
            results.append(BatchFileResult(input_path=str(input_path), error=str(exc)))

    summary = BatchSummary(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        profile=profile,
        total_files=len(files),
        processed_files=sum(1 for item in results if item.error is None),
        failed_files=sum(1 for item in results if item.error is not None),
        validation_failures=sum(
            1 for item in results if item.error is None and not item.validation_passed
        ),
        files=results,
    )
    write_json(output_dir / "batch-summary.json", model_to_dict(summary))
    write_batch_summary_html(output_dir / "batch-summary.html", summary)
    return summary


def _safe_stem(path: Path) -> str:
    return "__".join(path.with_suffix("").parts)
