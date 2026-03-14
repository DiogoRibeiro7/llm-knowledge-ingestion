from llm_knowledge_ingestion.chunking.strategies import ChunkingConfig, chunk_document
from llm_knowledge_ingestion.dedup.hashing import sha256_text


def test_chunk_document_scaffold_behavior() -> None:
    chunks = chunk_document("a b c d", "doc-1", ChunkingConfig(target_tokens=2, overlap_tokens=1))
    assert len(chunks) == 3
    assert chunks[0].text == "a b"
    assert chunks[1].text == "b c"


def test_sha256_text_is_deterministic() -> None:
    assert sha256_text("hello") == sha256_text("hello")
