from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, cast

INGESTION_CONTRACT_VERSION = "1.0"
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,127}$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
SUPPORTED_SOURCE_TYPES = {"pdf", "markdown", "html", "json", "text"}


def _is_tz_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None


def _assert_non_empty(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _assert_id(value: str, name: str) -> None:
    _assert_non_empty(value, name)
    if not ID_PATTERN.fullmatch(value):
        raise ValueError(f"{name} must match {ID_PATTERN.pattern}")


def _validate_contract_version(value: str) -> None:
    if value != INGESTION_CONTRACT_VERSION:
        raise ValueError(
            f"Unsupported contract_version={value!r}; expected {INGESTION_CONTRACT_VERSION!r}"
        )


def _serialize(value: Any) -> Any:
    # Datetimes need explicit conversion for JSON-safe payloads.
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    return value


class ContractModel:
    def to_dict(self) -> dict[str, Any]:
        return cast(dict[str, Any], _serialize(asdict(cast(Any, self))))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass(frozen=True, slots=True)
class DocumentMetadata(ContractModel):
    source_name: str | None = None
    mime_type: str | None = None
    tags: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source_name is not None:
            _assert_non_empty(self.source_name, "source_name")
        if self.mime_type is not None:
            _assert_non_empty(self.mime_type, "mime_type")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("tags must not contain empty values")
        if any(not key.strip() for key in self.attributes):
            raise ValueError("attributes keys must not be empty")


@dataclass(frozen=True, slots=True)
class LineageReference(ContractModel):
    source_id: str
    document_id: str
    chunk_id: str | None = None
    pipeline_run_id: str | None = None
    parent_document_id: str | None = None
    contract_version: str = INGESTION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.source_id, "source_id")
        _assert_id(self.document_id, "document_id")
        if self.chunk_id is not None:
            _assert_id(self.chunk_id, "chunk_id")
        if self.pipeline_run_id is not None:
            _assert_id(self.pipeline_run_id, "pipeline_run_id")
        if self.parent_document_id is not None:
            _assert_id(self.parent_document_id, "parent_document_id")
        _validate_contract_version(self.contract_version)


@dataclass(frozen=True, slots=True)
class NormalizedDocument(ContractModel):
    document_id: str
    source_id: str
    source_type: str
    source_uri: str | None
    title: str
    language: str | None
    created_at: datetime
    updated_at: datetime
    content: str
    content_hash: str
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    ingestion_timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    contract_version: str = INGESTION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.document_id, "document_id")
        _assert_id(self.source_id, "source_id")
        if self.source_type not in SUPPORTED_SOURCE_TYPES:
            raise ValueError(
                f"source_type must be one of {sorted(SUPPORTED_SOURCE_TYPES)}, got {self.source_type!r}"
            )
        _assert_non_empty(self.title, "title")
        _assert_non_empty(self.content, "content")
        if self.language is not None:
            _assert_non_empty(self.language, "language")
        if self.source_uri is not None:
            _assert_non_empty(self.source_uri, "source_uri")
        if not _is_tz_aware(self.created_at):
            raise ValueError("created_at must be timezone-aware")
        if not _is_tz_aware(self.updated_at):
            raise ValueError("updated_at must be timezone-aware")
        if not _is_tz_aware(self.ingestion_timestamp):
            raise ValueError("ingestion_timestamp must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must be >= created_at")
        if not SHA256_PATTERN.fullmatch(self.content_hash):
            raise ValueError("content_hash must be a lowercase 64-char SHA-256 hex digest")
        _validate_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> NormalizedDocument:
        metadata_payload = payload.get("metadata", {})
        metadata = (
            metadata_payload
            if isinstance(metadata_payload, DocumentMetadata)
            else DocumentMetadata(**metadata_payload)
        )
        return cls(
            document_id=str(payload["document_id"]),
            source_id=str(payload["source_id"]),
            source_type=str(payload["source_type"]),
            source_uri=payload.get("source_uri"),
            title=str(payload["title"]),
            language=payload.get("language"),
            created_at=datetime.fromisoformat(str(payload["created_at"])),
            updated_at=datetime.fromisoformat(str(payload["updated_at"])),
            content=str(payload["content"]),
            content_hash=str(payload["content_hash"]),
            metadata=metadata,
            ingestion_timestamp=datetime.fromisoformat(str(payload["ingestion_timestamp"])),
            contract_version=str(payload.get("contract_version", INGESTION_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> NormalizedDocument:
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True, slots=True)
class Chunk(ContractModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    token_count_estimate: int
    start_offset: int
    end_offset: int
    section: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    contract_version: str = INGESTION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.chunk_id, "chunk_id")
        _assert_id(self.document_id, "document_id")
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be >= 0")
        _assert_non_empty(self.text, "text")
        if self.token_count_estimate < 0:
            raise ValueError("token_count_estimate must be >= 0")
        if self.start_offset < 0:
            raise ValueError("start_offset must be >= 0")
        if self.end_offset <= self.start_offset:
            raise ValueError("end_offset must be > start_offset")
        if self.section is not None:
            _assert_non_empty(self.section, "section")
        if any(not key.strip() for key in self.metadata):
            raise ValueError("metadata keys must not be empty")
        _validate_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Chunk:
        return cls(
            chunk_id=str(payload["chunk_id"]),
            document_id=str(payload["document_id"]),
            chunk_index=int(payload["chunk_index"]),
            text=str(payload["text"]),
            token_count_estimate=int(payload["token_count_estimate"]),
            start_offset=int(payload["start_offset"]),
            end_offset=int(payload["end_offset"]),
            section=payload.get("section"),
            metadata=dict(payload.get("metadata", {})),
            contract_version=str(payload.get("contract_version", INGESTION_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> Chunk:
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True, slots=True)
class IngestionResult(ContractModel):
    run_id: str
    source_id: str
    documents_processed: int
    chunks_generated: int
    deduplicated_documents: int
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    lineage_references: list[LineageReference] = field(default_factory=list)
    contract_version: str = INGESTION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.run_id, "run_id")
        _assert_id(self.source_id, "source_id")
        if self.documents_processed < 0:
            raise ValueError("documents_processed must be >= 0")
        if self.chunks_generated < 0:
            raise ValueError("chunks_generated must be >= 0")
        if self.deduplicated_documents < 0:
            raise ValueError("deduplicated_documents must be >= 0")
        if self.deduplicated_documents > self.documents_processed:
            raise ValueError("deduplicated_documents must be <= documents_processed")
        if any(not msg.strip() for msg in self.warnings):
            raise ValueError("warnings must not contain empty values")
        if any(not msg.strip() for msg in self.errors):
            raise ValueError("errors must not contain empty values")
        _validate_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> IngestionResult:
        lineage_raw = payload.get("lineage_references", [])
        lineage = [
            item if isinstance(item, LineageReference) else LineageReference(**item)
            for item in lineage_raw
        ]
        return cls(
            run_id=str(payload["run_id"]),
            source_id=str(payload["source_id"]),
            documents_processed=int(payload["documents_processed"]),
            chunks_generated=int(payload["chunks_generated"]),
            deduplicated_documents=int(payload["deduplicated_documents"]),
            warnings=[str(msg) for msg in payload.get("warnings", [])],
            errors=[str(msg) for msg in payload.get("errors", [])],
            lineage_references=lineage,
            contract_version=str(payload.get("contract_version", INGESTION_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> IngestionResult:
        return cls.from_dict(json.loads(payload))
