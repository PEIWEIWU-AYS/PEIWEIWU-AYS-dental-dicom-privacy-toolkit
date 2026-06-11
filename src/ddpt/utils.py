from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def value_to_text(value: Any, max_length: int = 160) -> str:
    text = str(value)
    text = text.replace("\n", " ").replace("\r", " ")
    if len(text) > max_length:
        return f"{text[:max_length]}..."
    return text
