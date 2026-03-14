from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmbeddingPreparationRecord:
    chunk_id: str
    content: str
    metadata: dict[str, str]


@dataclass(frozen=True, slots=True)
class IndexReadyRecord:
    chunk_id: str
    document_id: str
    source_id: str
    text: str
    token_count_estimate: int
    source_uri: str | None
    title: str
    metadata: dict[str, str]
