from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet

from ddpt.models import ManifestEntry, PackageManifest, PackageVerificationReceipt
from ddpt.utils import ensure_parent, sha256_file, write_json

MANIFEST_NAME = "manifest.json"


def create_package(
    input_dir: Path,
    output_path: Path,
    manifest_path: Path | None = None,
    encrypt: bool = False,
    key_output: Path | None = None,
) -> PackageManifest:
    files = sorted(path for path in input_dir.rglob("*") if path.is_file())
    if not files:
        raise ValueError(f"No files found to package in: {input_dir}")

    manifest = PackageManifest(
        package_name=output_path.name,
        encrypted=encrypt,
        entries=[
            ManifestEntry(
                path=str(path.relative_to(input_dir)),
                sha256=sha256_file(path),
                size_bytes=path.stat().st_size,
            )
            for path in files
        ],
    )

    ensure_parent(output_path)
    if manifest_path:
        write_json(manifest_path, manifest.model_dump(mode="json"))

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "package.zip"
        _write_zip(input_dir, files, manifest, zip_path)
        payload = zip_path.read_bytes()

    if encrypt:
        key = Fernet.generate_key()
        if key_output is None:
            raise ValueError("--key-out is required when --encrypt is used")
        ensure_parent(key_output)
        key_output.write_bytes(key)
        payload = Fernet(key).encrypt(payload)

    output_path.write_bytes(payload)
    return manifest


def verify_package(package_path: Path, key_path: Path | None = None) -> PackageManifest:
    payload = _read_package_payload(package_path, key_path)
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "package.zip"
        extract_dir = Path(tmp) / "extract"
        zip_path.write_bytes(payload)
        with zipfile.ZipFile(zip_path) as archive:
            _safe_extract(archive, extract_dir)
        manifest = _load_manifest(extract_dir / MANIFEST_NAME)
        for entry in manifest.entries:
            file_path = extract_dir / entry.path
            if not file_path.exists():
                raise ValueError(f"Package is missing expected file: {entry.path}")
            if sha256_file(file_path) != entry.sha256:
                raise ValueError(f"Checksum mismatch for: {entry.path}")
        return manifest


def create_verification_receipt(
    package_path: Path,
    key_path: Path | None = None,
) -> PackageVerificationReceipt:
    package_sha256 = sha256_file(package_path)
    try:
        manifest = verify_package(package_path, key_path)
    except Exception as exc:
        return PackageVerificationReceipt(
            package_path=str(package_path),
            key_provided=key_path is not None,
            passed=False,
            package_sha256=package_sha256,
            errors=[str(exc)],
        )

    return PackageVerificationReceipt(
        package_path=str(package_path),
        key_provided=key_path is not None,
        passed=True,
        package_sha256=package_sha256,
        package_name=manifest.package_name,
        encrypted=manifest.encrypted,
        entries=manifest.entries,
        total_size_bytes=sum(entry.size_bytes for entry in manifest.entries),
    )


def decrypt_package(package_path: Path, output_dir: Path, key_path: Path) -> PackageManifest:
    payload = _read_package_payload(package_path, key_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "package.zip"
        zip_path.write_bytes(payload)
        with zipfile.ZipFile(zip_path) as archive:
            _safe_extract(archive, output_dir)
    return _load_manifest(output_dir / MANIFEST_NAME)


def _write_zip(
    input_dir: Path,
    files: list[Path],
    manifest: PackageManifest,
    output_path: Path,
) -> None:
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, file_path.relative_to(input_dir))
        archive.writestr(MANIFEST_NAME, json.dumps(manifest.model_dump(mode="json"), indent=2))


def _read_package_payload(package_path: Path, key_path: Path | None) -> bytes:
    payload = package_path.read_bytes()
    if key_path:
        return Fernet(key_path.read_bytes().strip()).decrypt(payload)
    return payload


def _load_manifest(path: Path) -> PackageManifest:
    return PackageManifest.model_validate_json(path.read_text(encoding="utf-8"))


def _safe_extract(archive: zipfile.ZipFile, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_output = output_dir.resolve()
    for member in archive.infolist():
        target = (output_dir / member.filename).resolve()
        if resolved_output not in {target, *target.parents}:
            raise ValueError(f"Unsafe path in package: {member.filename}")
    archive.extractall(output_dir)
