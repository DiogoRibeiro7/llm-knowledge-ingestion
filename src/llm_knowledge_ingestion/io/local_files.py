from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_SUFFIXES = {".txt": "text", ".md": "markdown", ".json": "json"}


@dataclass(frozen=True, slots=True)
class RawDocument:
    source_type: str
    source_uri: str
    content: str
    title: str
    metadata: dict[str, str]


def _json_to_content(payload: Any) -> str:
    """Render JSON deterministically so hashes remain stable across runs."""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_local_document(path: Path) -> RawDocument:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    text = path.read_text(encoding="utf-8")
    source_type = SUPPORTED_SUFFIXES[suffix]
    title = path.stem
    metadata = {"file_name": path.name, "file_suffix": suffix}

    if source_type == "json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON file: {path}") from exc
        text = _json_to_content(payload)
        if isinstance(payload, dict):
            for candidate in ("title", "name", "id"):
                if candidate in payload and str(payload[candidate]).strip():
                    title = str(payload[candidate]).strip()
                    break

    return RawDocument(
        source_type=source_type,
        source_uri=str(path.resolve()),
        content=text,
        title=title,
        metadata=metadata,
    )


def discover_input_files(input_path: Path) -> list[Path]:
    if not input_path.exists():
        raise ValueError(f"Input path does not exist: {input_path}")
    if input_path.is_file():
        return [input_path]

    return sorted(
        file
        for file in input_path.rglob("*")
        if file.is_file() and file.suffix.lower() in SUPPORTED_SUFFIXES
    )
