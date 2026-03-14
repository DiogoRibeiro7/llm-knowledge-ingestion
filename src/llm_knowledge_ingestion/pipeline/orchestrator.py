from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from llm_knowledge_ingestion.chunking.strategies import ChunkingConfig, chunk_document
from llm_knowledge_ingestion.contracts.models import (
    DocumentMetadata,
    IngestionResult,
    LineageReference,
    NormalizedDocument,
)
from llm_knowledge_ingestion.dedup.hashing import sha256_text
from llm_knowledge_ingestion.io.artifacts import (
    write_chunks,
    write_documents,
    write_index_records,
    write_lineage,
    write_result,
)
from llm_knowledge_ingestion.io.local_files import discover_input_files, load_local_document
from llm_knowledge_ingestion.pipeline.config import PipelineConfig
from llm_knowledge_ingestion.pipeline.interfaces import IndexReadyRecord


@dataclass(slots=True)
class IngestionPipeline:
    config: PipelineConfig
    pipeline_name: str = "mvp-filesystem"

    def run(self) -> IngestionResult:
        files = discover_input_files(self.config.ingestion.input_path)
        selected_files = files[: self.config.ingestion.max_documents]

        chunk_cfg = ChunkingConfig(
            strategy=self.config.chunking.strategy,
            target_tokens=self.config.chunking.target_tokens,
            overlap_tokens=self.config.chunking.overlap_tokens,
        )
        run_id = self._build_run_id(self.config.ingestion.source_id)

        documents: list[NormalizedDocument] = []
        all_chunks = []
        lineage: list[LineageReference] = []
        index_records: list[dict[str, object]] = []
        warnings: list[str] = []

        for path in selected_files:
            raw = load_local_document(path)
            if not raw.content.strip():
                warnings.append(f"Skipping empty content file: {path}")
                continue

            now = datetime.now(tz=UTC)
            content_hash = sha256_text(raw.content)
            document_id = self._document_id(self.config.ingestion.source_id, path)
            document = NormalizedDocument(
                document_id=document_id,
                source_id=self.config.ingestion.source_id,
                source_type=raw.source_type,
                source_uri=raw.source_uri,
                title=raw.title,
                language=None,
                created_at=now,
                updated_at=now,
                content=raw.content,
                content_hash=content_hash,
                metadata=DocumentMetadata(attributes=raw.metadata),
                ingestion_timestamp=now,
            )
            documents.append(document)

            chunks = chunk_document(document.content, document.document_id, chunk_cfg)
            all_chunks.extend(chunks)

            for chunk in chunks:
                lineage.append(
                    LineageReference(
                        source_id=document.source_id,
                        document_id=document.document_id,
                        chunk_id=chunk.chunk_id,
                        pipeline_run_id=run_id,
                    )
                )
                index_records.append(
                    self._index_record(
                        IndexReadyRecord(
                            chunk_id=chunk.chunk_id,
                            document_id=document.document_id,
                            source_id=document.source_id,
                            text=chunk.text,
                            token_count_estimate=chunk.token_count_estimate,
                            source_uri=document.source_uri,
                            title=document.title,
                            metadata={"source_type": document.source_type},
                        )
                    )
                )

        result = IngestionResult(
            run_id=run_id,
            source_id=self.config.ingestion.source_id,
            documents_processed=len(documents),
            chunks_generated=len(all_chunks),
            deduplicated_documents=0,
            warnings=warnings,
            errors=[],
            lineage_references=lineage,
        )

        write_documents(self.config.output.normalized_documents_path / "documents.jsonl", documents)
        write_chunks(self.config.output.chunks_path / "chunks.jsonl", all_chunks)
        write_lineage(self.config.output.lineage_path / "lineage.jsonl", lineage)
        write_index_records(self.config.output.index_records_path / "index_records.jsonl", index_records)
        write_result(self.config.output.run_result_path, result)
        return result

    @staticmethod
    def _build_run_id(source_id: str) -> str:
        digest = sha256_text(f"{source_id}|{datetime.now(tz=UTC).isoformat()}")
        return f"run_{digest[:20]}"

    @staticmethod
    def _document_id(source_id: str, path: Path) -> str:
        digest = sha256_text(f"{source_id}|{path.resolve().as_posix().lower()}")
        return f"doc_{digest[:28]}"

    @staticmethod
    def _index_record(record: IndexReadyRecord) -> dict[str, object]:
        return {
            "chunk_id": record.chunk_id,
            "document_id": record.document_id,
            "source_id": record.source_id,
            "text": record.text,
            "token_count_estimate": record.token_count_estimate,
            "source_uri": record.source_uri,
            "title": record.title,
            "metadata": record.metadata,
        }
