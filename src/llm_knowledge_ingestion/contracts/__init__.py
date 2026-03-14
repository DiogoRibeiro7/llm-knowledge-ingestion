"""Shared data contracts for ingestion artifacts."""

from llm_knowledge_ingestion.contracts.models import (
    INGESTION_CONTRACT_VERSION,
    Chunk,
    DocumentMetadata,
    IngestionResult,
    LineageReference,
    NormalizedDocument,
)

__all__ = [
    "Chunk",
    "DocumentMetadata",
    "INGESTION_CONTRACT_VERSION",
    "IngestionResult",
    "LineageReference",
    "NormalizedDocument",
]
