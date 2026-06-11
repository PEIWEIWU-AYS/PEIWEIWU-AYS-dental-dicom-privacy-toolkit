from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

from ddpt.models import SyntheticStudyFile, SyntheticStudyReport
from ddpt.utils import ensure_parent

DEFAULT_STUDY_MODALITIES = ("DX", "PX", "CT")


def create_synthetic_dicom(
    output_path: Path,
    patient_name: str = "SYNTHETIC^DENTAL",
    patient_id: str = "SYNTHETIC-001",
    modality: str = "DX",
    study_description: str = "Synthetic Dental Radiograph",
    study_instance_uid: str | None = None,
    series_instance_uid: str | None = None,
    accession_number: str = "SYNTHETIC-ACCESS",
    series_description: str = "Synthetic Dental Series",
    pixel_values: bytes | None = None,
) -> Path:
    now = datetime.now()
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()

    dataset = FileDataset(str(output_path), {}, file_meta=file_meta, preamble=b"\0" * 128)

    dataset.SOPClassUID = SecondaryCaptureImageStorage
    dataset.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    dataset.PatientName = patient_name
    dataset.PatientID = patient_id
    dataset.PatientBirthDate = "19700101"
    dataset.PatientAddress = "123 Synthetic Dental Street"
    dataset.PatientTelephoneNumbers = "555-0100"
    dataset.Modality = modality
    dataset.StudyInstanceUID = study_instance_uid or generate_uid()
    dataset.SeriesInstanceUID = series_instance_uid or generate_uid()
    dataset.StudyDate = now.strftime("%Y%m%d")
    dataset.SeriesDate = now.strftime("%Y%m%d")
    dataset.AcquisitionDate = now.strftime("%Y%m%d")
    dataset.ContentDate = now.strftime("%Y%m%d")
    dataset.StudyTime = now.strftime("%H%M%S")
    dataset.SeriesTime = now.strftime("%H%M%S")
    dataset.AcquisitionTime = now.strftime("%H%M%S")
    dataset.ContentTime = now.strftime("%H%M%S")
    dataset.AccessionNumber = accession_number
    dataset.StudyDescription = study_description
    dataset.SeriesDescription = series_description
    dataset.BurnedInAnnotation = "NO"
    dataset.InstitutionName = "Source Synthetic Dental Clinic"
    dataset.InstitutionAddress = "Synthetic City"
    dataset.ReferringPhysicianName = "SYNTHETIC^REFERRER"
    dataset.OperatorsName = "SYNTHETIC^OPERATOR"
    dataset.DeviceSerialNumber = "SYNTHETIC-DEVICE"
    dataset.StationName = "SYNTH-STATION"

    dataset.SamplesPerPixel = 1
    dataset.PhotometricInterpretation = "MONOCHROME2"
    dataset.Rows = 2
    dataset.Columns = 2
    dataset.BitsAllocated = 8
    dataset.BitsStored = 8
    dataset.HighBit = 7
    dataset.PixelRepresentation = 0
    dataset.PixelData = pixel_values or bytes([0, 64, 128, 255])

    ensure_parent(output_path)
    dataset.save_as(output_path, enforce_file_format=True)
    return output_path


def create_synthetic_study(
    output_dir: Path,
    patient_count: int = 2,
    files_per_patient: int = 2,
) -> SyntheticStudyReport:
    if patient_count < 1:
        raise ValueError("patient_count must be at least 1")
    if files_per_patient < 1:
        raise ValueError("files_per_patient must be at least 1")

    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[SyntheticStudyFile] = []
    modalities: Counter[str] = Counter()

    for patient_index in range(1, patient_count + 1):
        patient_id = f"SYNTH-STUDY-P{patient_index:03d}"
        patient_name = f"SYNTHETIC^PATIENT{patient_index:03d}"
        study_uid = generate_uid()
        for file_index in range(1, files_per_patient + 1):
            modality = DEFAULT_STUDY_MODALITIES[
                (patient_index + file_index - 2) % len(DEFAULT_STUDY_MODALITIES)
            ]
            series_uid = generate_uid()
            description = _study_description(modality)
            relative_path = (
                Path(f"patient-{patient_index:03d}")
                / "study-001"
                / f"{modality.lower()}-{file_index:03d}.dcm"
            )
            output_path = output_dir / relative_path
            create_synthetic_dicom(
                output_path,
                patient_name=patient_name,
                patient_id=patient_id,
                modality=modality,
                study_description=description,
                study_instance_uid=study_uid,
                series_instance_uid=series_uid,
                accession_number=f"SYN{patient_index:03d}{file_index:03d}",
                series_description=f"{description} Series {file_index:03d}",
                pixel_values=_pixel_values(patient_index, file_index),
            )
            dataset = pydicom.dcmread(output_path, stop_before_pixels=True)
            modalities[modality] += 1
            files.append(
                SyntheticStudyFile(
                    path=str(relative_path),
                    patient_id=patient_id,
                    patient_name=patient_name,
                    modality=modality,
                    study_description=description,
                    study_instance_uid=str(dataset.StudyInstanceUID),
                    series_instance_uid=str(dataset.SeriesInstanceUID),
                    sop_instance_uid=str(dataset.SOPInstanceUID),
                )
            )

    return SyntheticStudyReport(
        output_dir=str(output_dir),
        patient_count=patient_count,
        files_per_patient=files_per_patient,
        total_files=len(files),
        modalities=dict(sorted(modalities.items())),
        files=files,
    )


def _study_description(modality: str) -> str:
    descriptions = {
        "CT": "Synthetic Dental CBCT Study",
        "DX": "Synthetic Dental Radiograph Study",
        "PX": "Synthetic Dental Panoramic Study",
    }
    return descriptions.get(modality, "Synthetic Dental Imaging Study")


def _pixel_values(patient_index: int, file_index: int) -> bytes:
    base = (patient_index * 29 + file_index * 17) % 128
    return bytes([base, min(base + 48, 255), min(base + 96, 255), 255])
