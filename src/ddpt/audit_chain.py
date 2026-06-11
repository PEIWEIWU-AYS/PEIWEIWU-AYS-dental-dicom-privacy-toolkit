from __future__ import annotations

import hashlib
from pathlib import Path

from ddpt.models import AuditChainEntry, AuditChainManifest, AuditChainVerification
from ddpt.utils import sha256_file, write_json

ZERO_HASH = "0" * 64
DEFAULT_EXCLUDED_PATTERNS = ["*.key", "audit-chain.json", "audit-chain-verify.json"]


def create_audit_chain(
    root_dir: Path,
    output_path: Path,
    include_key_files: bool = False,
) -> AuditChainManifest:
    excluded_patterns = [] if include_key_files else DEFAULT_EXCLUDED_PATTERNS
    files = _discover_files(root_dir, output_path, excluded_patterns)
    previous_hash = ZERO_HASH
    entries: list[AuditChainEntry] = []

    for file_path in files:
        relative = file_path.relative_to(root_dir).as_posix()
        file_hash = sha256_file(file_path)
        chain_hash = _chain_hash(previous_hash, relative, file_hash)
        entries.append(
            AuditChainEntry(
                path=relative,
                sha256=file_hash,
                size_bytes=file_path.stat().st_size,
                previous_chain_hash=previous_hash,
                chain_hash=chain_hash,
            )
        )
        previous_hash = chain_hash

    manifest = AuditChainManifest(
        root_dir=str(root_dir),
        root_hash=previous_hash,
        entries=entries,
        excluded_patterns=excluded_patterns,
    )
    write_json(output_path, manifest.model_dump(mode="json"))
    return manifest


def verify_audit_chain(manifest_path: Path) -> AuditChainVerification:
    manifest = AuditChainManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    root_dir = Path(manifest.root_dir)
    errors: list[str] = []
    previous_hash = ZERO_HASH

    for entry in manifest.entries:
        file_path = root_dir / entry.path
        if not file_path.exists():
            errors.append(f"Missing file: {entry.path}")
            continue

        actual_file_hash = sha256_file(file_path)
        if actual_file_hash != entry.sha256:
            errors.append(f"File hash mismatch: {entry.path}")

        if previous_hash != entry.previous_chain_hash:
            errors.append(f"Previous chain hash mismatch: {entry.path}")

        actual_chain_hash = _chain_hash(previous_hash, entry.path, actual_file_hash)
        if actual_chain_hash != entry.chain_hash:
            errors.append(f"Chain hash mismatch: {entry.path}")
        previous_hash = actual_chain_hash

    if previous_hash != manifest.root_hash:
        errors.append("Root hash mismatch")

    return AuditChainVerification(
        manifest_path=str(manifest_path),
        passed=not errors,
        checked_files=len(manifest.entries),
        errors=errors,
    )


def _discover_files(root_dir: Path, output_path: Path, excluded_patterns: list[str]) -> list[Path]:
    resolved_output = output_path.resolve()
    files: list[Path] = []
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.resolve() == resolved_output:
            continue
        if any(path.match(pattern) for pattern in excluded_patterns):
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root_dir).as_posix())


def _chain_hash(previous_hash: str, relative_path: str, file_hash: str) -> str:
    payload = f"{previous_hash}\n{relative_path}\n{file_hash}".encode()
    return hashlib.sha256(payload).hexdigest()
