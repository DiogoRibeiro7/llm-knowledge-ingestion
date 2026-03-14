from __future__ import annotations

from datetime import UTC, datetime

import pytest

from llm_knowledge_ingestion.contracts.models import (
    Chunk,
    DocumentMetadata,
    IngestionResult,
    LineageReference,
    NormalizedDocument,
)
from llm_knowledge_ingestion.dedup.hashing import sha256_text
from llm_knowledge_ingestion.normalize.schema import normalize_text_document


def _ts(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, 0, 0, tzinfo=UTC)


def test_normalize_text_document_populates_required_fields() -> None:
    doc = normalize_text_document(
        source_id="src-1",
        document_id="doc-1",
        content="body",
        metadata={"kind": "faq"},
    )
    assert doc.source_id == "src-1"
    assert doc.document_id == "doc-1"
    assert doc.source_type == "text"
    assert doc.content_hash == sha256_text("body")
    assert doc.metadata.attributes["kind"] == "faq"


def test_document_metadata_rejects_invalid_tags() -> None:
    with pytest.raises(ValueError, match="tags"):
        DocumentMetadata(tags=["ok", ""])


def test_normalized_document_round_trip_serialization() -> None:
    doc = NormalizedDocument(
        document_id="doc-1",
        source_id="src-1",
        source_type="markdown",
        source_uri="https://example.com/a.md",
        title="Doc A",
        language="en",
        created_at=_ts(10),
        updated_at=_ts(11),
        content="hello world",
        content_hash=sha256_text("hello world"),
        metadata=DocumentMetadata(source_name="wiki", tags=["a"]),
        ingestion_timestamp=_ts(12),
    )

    as_dict = doc.to_dict()
    assert as_dict["created_at"].endswith("+00:00")

    restored = NormalizedDocument.from_json(doc.to_json())
    assert restored == doc


def test_normalized_document_rejects_invalid_cases() -> None:
    with pytest.raises(ValueError, match="source_type"):
        NormalizedDocument(
            document_id="doc-1",
            source_id="src-1",
            source_type="xml",
            source_uri=None,
            title="Doc A",
            language=None,
            created_at=_ts(10),
            updated_at=_ts(11),
            content="hello world",
            content_hash=sha256_text("hello world"),
        )

    with pytest.raises(ValueError, match="content_hash"):
        NormalizedDocument(
            document_id="doc-1",
            source_id="src-1",
            source_type="text",
            source_uri=None,
            title="Doc A",
            language=None,
            created_at=_ts(10),
            updated_at=_ts(11),
            content="hello world",
            content_hash="bad",
        )


def test_chunk_round_trip_serialization() -> None:
    chunk = Chunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        text="example text",
        token_count_estimate=2,
        start_offset=0,
        end_offset=12,
        section="intro",
        metadata={"page": "1"},
    )
    assert Chunk.from_json(chunk.to_json()) == chunk


def test_chunk_rejects_invalid_offsets() -> None:
    with pytest.raises(ValueError, match="end_offset"):
        Chunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            chunk_index=0,
            text="x",
            token_count_estimate=1,
            start_offset=10,
            end_offset=10,
        )


def test_lineage_reference_validation() -> None:
    ref = LineageReference(
        source_id="src-1",
        document_id="doc-1",
        chunk_id="chunk-1",
        pipeline_run_id="run-1",
    )
    assert ref.to_dict()["chunk_id"] == "chunk-1"

    with pytest.raises(ValueError, match="source_id"):
        LineageReference(source_id="", document_id="doc-1")


def test_ingestion_result_validation_and_round_trip() -> None:
    result = IngestionResult(
        run_id="run-1",
        source_id="src-1",
        documents_processed=10,
        chunks_generated=24,
        deduplicated_documents=2,
        warnings=["minor"],
        errors=[],
        lineage_references=[LineageReference(source_id="src-1", document_id="doc-1")],
    )

    parsed = IngestionResult.from_json(result.to_json())
    assert parsed == result


def test_ingestion_result_rejects_invalid_counts() -> None:
    with pytest.raises(ValueError, match="deduplicated_documents"):
        IngestionResult(
            run_id="run-1",
            source_id="src-1",
            documents_processed=1,
            chunks_generated=1,
            deduplicated_documents=2,
        )


def test_contract_version_validation() -> None:
    with pytest.raises(ValueError, match="Unsupported contract_version"):
        Chunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            chunk_index=0,
            text="x",
            token_count_estimate=1,
            start_offset=0,
            end_offset=1,
            contract_version="2.0",
        )
