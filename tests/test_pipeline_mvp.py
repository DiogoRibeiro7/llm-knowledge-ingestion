from __future__ import annotations

import json
from pathlib import Path

import pytest

from llm_knowledge_ingestion.pipeline.config import load_config
from llm_knowledge_ingestion.pipeline.orchestrator import IngestionPipeline


def _write_config(path: Path, input_path: Path, out_root: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "ingestion:",
                "  source_id: test-source",
                f"  input_path: {input_path.as_posix()}",
                "  max_documents: 10",
                "chunking:",
                "  strategy: fixed_tokens",
                "  target_tokens: 3",
                "  overlap_tokens: 1",
                "output:",
                f"  normalized_documents_path: {(out_root / 'documents').as_posix()}",
                f"  chunks_path: {(out_root / 'chunks').as_posix()}",
                f"  lineage_path: {(out_root / 'lineage').as_posix()}",
                f"  index_records_path: {(out_root / 'index').as_posix()}",
                f"  run_result_path: {(out_root / 'run' / 'ingestion_result.json').as_posix()}",
            ]
        ),
        encoding="utf-8",
    )


def test_pipeline_writes_expected_artifacts(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "a.txt").write_text("one two three four", encoding="utf-8")
    (input_dir / "b.md").write_text("# heading\nbody text", encoding="utf-8")
    (input_dir / "c.json").write_text('{"title":"JsonDoc","k":"v"}', encoding="utf-8")
    out_dir = tmp_path / "artifacts"
    cfg_path = tmp_path / "config.yaml"
    _write_config(cfg_path, input_dir, out_dir)

    config = load_config(cfg_path)
    result = IngestionPipeline(config=config).run()

    assert result.documents_processed == 3
    assert (out_dir / "documents" / "documents.jsonl").exists()
    assert (out_dir / "chunks" / "chunks.jsonl").exists()
    assert (out_dir / "lineage" / "lineage.jsonl").exists()
    assert (out_dir / "index" / "index_records.jsonl").exists()
    assert (out_dir / "run" / "ingestion_result.json").exists()

    docs = (out_dir / "documents" / "documents.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(docs) == 3
    first_doc = json.loads(docs[0])
    assert first_doc["source_id"] == "test-source"
    assert first_doc["content_hash"]


def test_pipeline_handles_missing_input_path(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.yaml"
    out_dir = tmp_path / "artifacts"
    _write_config(cfg_path, tmp_path / "missing", out_dir)
    config = load_config(cfg_path)

    with pytest.raises(ValueError, match="Input path does not exist"):
        IngestionPipeline(config=config).run()
