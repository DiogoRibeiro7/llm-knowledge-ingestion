from __future__ import annotations

import re
from dataclasses import dataclass

from llm_knowledge_ingestion.contracts.models import Chunk
from llm_knowledge_ingestion.dedup.hashing import sha256_text


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    strategy: str = "fixed_tokens"
    target_tokens: int = 400
    overlap_tokens: int = 40

    def __post_init__(self) -> None:
        if self.strategy != "fixed_tokens":
            raise ValueError("Only fixed_tokens strategy is supported in MVP")
        if self.target_tokens <= 0:
            raise ValueError("target_tokens must be > 0")
        if self.overlap_tokens < 0:
            raise ValueError("overlap_tokens must be >= 0")
        if self.overlap_tokens >= self.target_tokens:
            raise ValueError("overlap_tokens must be < target_tokens")


TOKEN_RE = re.compile(r"\S+")


def _chunk_id(document_id: str, chunk_index: int, text: str, start: int, end: int) -> str:
    digest = sha256_text(f"{document_id}|{chunk_index}|{start}|{end}|{text}")
    return f"chk_{digest[:28]}"


def chunk_document(content: str, document_id: str, config: ChunkingConfig) -> list[Chunk]:
    """Split content into deterministic token-window chunks."""
    tokens = list(TOKEN_RE.finditer(content))
    if not tokens:
        return []

    step = config.target_tokens - config.overlap_tokens
    chunks: list[Chunk] = []
    chunk_index = 0

    for token_start in range(0, len(tokens), step):
        token_end = min(len(tokens), token_start + config.target_tokens)
        start_offset = tokens[token_start].start()
        end_offset = tokens[token_end - 1].end()
        text = content[start_offset:end_offset]
        chunks.append(
            Chunk(
                chunk_id=_chunk_id(document_id, chunk_index, text, start_offset, end_offset),
                document_id=document_id,
                chunk_index=chunk_index,
                text=text,
                token_count_estimate=token_end - token_start,
                start_offset=start_offset,
                end_offset=end_offset,
                section=None,
                metadata={},
            )
        )
        chunk_index += 1
        if token_end == len(tokens):
            break

    return chunks
