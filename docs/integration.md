# Integration

## Role in Platform Flow

`llm-knowledge-ingestion` is the upstream producer of normalized knowledge artifacts.

Flow:

1. Raw source content enters ingestion.
2. Ingestion emits `documents.jsonl` and `chunks.jsonl` with stable IDs.
3. `llm-observability-analytics` references `document_id` / `chunk_id` during runtime trace logging.
4. `llm-dataset-foundry` combines ingestion artifacts with observability traces to build versioned datasets.

## Upstream and Downstream Boundaries

Upstream boundary:

- source connectors and local artifact inputs

Downstream boundaries:

- to `llm-observability-analytics`: chunk/document keys for grounding and retrieval attribution
- to `llm-dataset-foundry`: normalized content and lineage context

## Expected Handoff Artifacts

- `artifacts/documents/documents.jsonl`
- `artifacts/chunks/chunks.jsonl`
- `artifacts/lineage/lineage.jsonl`

Minimum required fields for cross-repo joinability:

- documents: `source_id`, `document_id`
- chunks: `chunk_id`, `document_id`
- lineage: `source_id`, `document_id`, `chunk_id`

## Example Integration Artifacts

See `examples/integration/`:

- `ingestion_documents_for_dataset_foundry.jsonl`
- `ingestion_chunks_for_observability.jsonl`
- `ingestion_lineage_for_dataset_foundry.jsonl`
