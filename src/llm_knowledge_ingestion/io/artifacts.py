from __future__ import annotations

import json
from pathlib import Path

from llm_knowledge_ingestion.contracts.models import (
    Chunk,
    IngestionResult,
    LineageReference,
    NormalizedDocument,
)


def _write_jsonl(path: Path, lines: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(json.dumps(line, sort_keys=True))
            handle.write("\n")


def write_documents(path: Path, documents: list[NormalizedDocument]) -> None:
    _write_jsonl(path, [doc.to_dict() for doc in documents])


def write_chunks(path: Path, chunks: list[Chunk]) -> None:
    _write_jsonl(path, [chunk.to_dict() for chunk in chunks])


def write_lineage(path: Path, lineage: list[LineageReference]) -> None:
    _write_jsonl(path, [item.to_dict() for item in lineage])


def write_index_records(path: Path, records: list[dict[str, object]]) -> None:
    _write_jsonl(path, records)


def write_result(path: Path, result: IngestionResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.to_json(), encoding="utf-8")
