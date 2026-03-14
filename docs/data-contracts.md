# Data Contracts

This repository publishes the canonical ingestion-side knowledge contracts.

## Shared Platform Identifiers

- `source_id`
- `document_id`
- `chunk_id`
- `query_id` (downstream)
- `trace_id` (downstream)
- `dataset_id` (downstream)
- `dataset_version` (downstream)
- `model_version` (downstream)

Contract constant:

- `INGESTION_CONTRACT_VERSION = "1.0"`

## Produced Schemas

### NormalizedDocument

Required fields:

- `document_id`
- `source_id`
- `source_type`
- `source_uri`
- `title`
- `language`
- `created_at`
- `updated_at`
- `content`
- `content_hash`
- `metadata`
- `ingestion_timestamp`
- `contract_version`

### Chunk

Required fields:

- `chunk_id`
- `document_id`
- `chunk_index`
- `text`
- `token_count_estimate`
- `start_offset`
- `end_offset`
- `section`
- `metadata`
- `contract_version`

### LineageReference

Required fields:

- `source_id`
- `document_id`

Optional fields:

- `chunk_id`
- `pipeline_run_id`
- `parent_document_id`
- `contract_version`

## Handoff Formats

- `documents.jsonl`: handoff to `llm-dataset-foundry`
- `chunks.jsonl`: handoff to `llm-observability-analytics` and `llm-dataset-foundry`
- `lineage.jsonl`: provenance handoff to `llm-dataset-foundry`

Each file is JSONL (one JSON object per line), UTF-8, with snake_case field names.
