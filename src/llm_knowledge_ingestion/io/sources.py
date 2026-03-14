from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SourceDescriptor:
    source_id: str
    uri: str
    content_type: str
    path: Path | None = None
