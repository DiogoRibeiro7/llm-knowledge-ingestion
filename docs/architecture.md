# Architecture

## Scope

`llm-knowledge-ingestion` is responsible for transforming raw source content into normalized, deduplicated, chunked, and index-ready assets with durable lineage.

## High-Level Components

- `io/`: source descriptors, reader abstractions, and ingestion adapters.
- `parsers/`: format-specific parsers (PDF, Markdown, HTML, JSON, text).
- `normalize/`: schema normalization and metadata harmonization.
- `chunking/`: chunk generation strategies and chunk metadata.
- `dedup/`: content hashing and deduplication decisioning.
- `pipeline/`: orchestration for end-to-end ingestion jobs.
- `contracts/`: shared entity models and platform IDs.
- `cli/`: operational interface for running and validating jobs.

## Data Flow

1. Source is discovered and represented as a source descriptor (`source_id`).
2. Parser extracts raw document payload.
3. Normalizer emits canonical document (`document_id`).
4. Dedup stage computes content hash and dedup decision.
5. Chunking stage produces deterministic chunks (`chunk_id`).
6. Pipeline emits index-ready assets and lineage records.

## Integration Boundaries

- Upstream systems: source connectors and metadata providers.
- Downstream `llm-observability-analytics`: consumes stable `document_id` and `chunk_id` for runtime attribution.
- Downstream `llm-dataset-foundry`: consumes normalized/chunk artifacts plus lineage for reproducible dataset assembly.

## Non-Functional Priorities

- Idempotent ingestion runs.
- Deterministic identifiers and chunking under fixed policy.
- Explicit schema versioning and compatibility checks.
- Operational observability (metrics, trace hooks, structured errors).
- Security and compliance hooks (PII handling, retention policy integration).
