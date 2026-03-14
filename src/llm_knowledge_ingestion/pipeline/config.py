from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class IngestionSettings:
    source_id: str
    input_path: Path
    max_documents: int = 100

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("ingestion.source_id must not be empty")
        if self.max_documents <= 0:
            raise ValueError("ingestion.max_documents must be > 0")


@dataclass(frozen=True, slots=True)
class ChunkingSettings:
    strategy: str
    target_tokens: int
    overlap_tokens: int


@dataclass(frozen=True, slots=True)
class OutputSettings:
    normalized_documents_path: Path
    chunks_path: Path
    lineage_path: Path
    index_records_path: Path
    run_result_path: Path


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    ingestion: IngestionSettings
    chunking: ChunkingSettings
    output: OutputSettings


def _path(base_dir: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else (base_dir / candidate)


def load_config(config_path: Path) -> PipelineConfig:
    base_dir = config_path.resolve().parent
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Config payload must be a mapping")

    ingestion_data = _require_mapping(payload, "ingestion")
    chunking_data = _require_mapping(payload, "chunking")
    output_data = _require_mapping(payload, "output")

    ingestion = IngestionSettings(
        source_id=str(ingestion_data["source_id"]),
        input_path=_path(base_dir, str(ingestion_data["input_path"])),
        max_documents=int(ingestion_data.get("max_documents", 100)),
    )
    chunking = ChunkingSettings(
        strategy=str(chunking_data.get("strategy", "fixed_tokens")),
        target_tokens=int(chunking_data.get("target_tokens", 400)),
        overlap_tokens=int(chunking_data.get("overlap_tokens", 40)),
    )
    output = OutputSettings(
        normalized_documents_path=_path(base_dir, str(output_data["normalized_documents_path"])),
        chunks_path=_path(base_dir, str(output_data["chunks_path"])),
        lineage_path=_path(base_dir, str(output_data["lineage_path"])),
        index_records_path=_path(base_dir, str(output_data["index_records_path"])),
        run_result_path=_path(base_dir, str(output_data["run_result_path"])),
    )
    return PipelineConfig(ingestion=ingestion, chunking=chunking, output=output)


def _require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Config key '{key}' must be a mapping")
    return value
