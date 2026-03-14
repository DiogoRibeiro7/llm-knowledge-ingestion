from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from llm_knowledge_ingestion.contracts.models import DocumentMetadata, NormalizedDocument
from llm_knowledge_ingestion.dedup.hashing import sha256_text


def normalize_text_document(
    *,
    source_id: str,
    document_id: str,
    content: str,
    title: str = "untitled",
    source_type: str = "text",
    language: str | None = None,
    source_uri: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> NormalizedDocument:
    """Create a canonical normalized document from plain text inputs."""
    now = datetime.now(tz=UTC)
    return NormalizedDocument(
        document_id=document_id,
        source_id=source_id,
        source_type=source_type,
        source_uri=source_uri,
        title=title.strip() or "untitled",
        language=language,
        created_at=now,
        updated_at=now,
        content=content,
        content_hash=sha256_text(content),
        metadata=DocumentMetadata(attributes={k: str(v) for k, v in (metadata or {}).items()}),
        ingestion_timestamp=now,
    )
