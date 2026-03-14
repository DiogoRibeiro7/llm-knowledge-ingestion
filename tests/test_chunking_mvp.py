from llm_knowledge_ingestion.chunking.strategies import ChunkingConfig, chunk_document


def test_chunking_is_deterministic() -> None:
    cfg = ChunkingConfig(strategy="fixed_tokens", target_tokens=3, overlap_tokens=1)
    content = "one two three four five six"
    chunks_a = chunk_document(content, "doc-1", cfg)
    chunks_b = chunk_document(content, "doc-1", cfg)
    assert [c.chunk_id for c in chunks_a] == [c.chunk_id for c in chunks_b]
    assert [c.text for c in chunks_a] == [c.text for c in chunks_b]


def test_chunk_offsets_are_monotonic() -> None:
    cfg = ChunkingConfig(strategy="fixed_tokens", target_tokens=2, overlap_tokens=1)
    chunks = chunk_document("one two three four", "doc-1", cfg)
    assert chunks[0].start_offset == 0
    assert chunks[0].end_offset > chunks[0].start_offset
    assert chunks[1].start_offset >= chunks[0].start_offset
