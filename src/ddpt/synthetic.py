from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

from ddpt.utils import ensure_parent


def create_synthetic_dicom(
    output_path: Path,
    patient_name: str = "SYNTHETIC^DENTAL",
    patient_id: str = "SYNTHETIC-001",
    modality: str = "DX",
    study_description: str = "Synthetic Dental Radiograph",
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
    dataset.StudyInstanceUID = generate_uid()
    dataset.SeriesInstanceUID = generate_uid()
    dataset.StudyDate = now.strftime("%Y%m%d")
    dataset.SeriesDate = now.strftime("%Y%m%d")
    dataset.ContentDate = now.strftime("%Y%m%d")
    dataset.StudyTime = now.strftime("%H%M%S")
    dataset.SeriesTime = now.strftime("%H%M%S")
    dataset.ContentTime = now.strftime("%H%M%S")
    dataset.AccessionNumber = "SYNTHETIC-ACCESS"
    dataset.StudyDescription = study_description
    dataset.SeriesDescription = "Synthetic Dental Series"
    dataset.InstitutionName = "Synthetic Dental Clinic"
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
    dataset.PixelData = bytes([0, 64, 128, 255])

    ensure_parent(output_path)
    dataset.save_as(output_path, enforce_file_format=True)
    return output_path
