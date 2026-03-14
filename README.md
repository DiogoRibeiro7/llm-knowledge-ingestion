# llm-knowledge-ingestion

Ingestion and indexing layer for the multi-repository LLM data engineering platform.

## Platform Position

`llm-knowledge-ingestion` is the upstream data preparation repository.
It remains an independent Git repository and publishes normalized knowledge artifacts consumed by:

- `llm-observability-analytics`
- `llm-dataset-foundry`

## Inputs and Outputs

Upstream inputs:

- local files or connector payloads (`.txt`, `.md`, `.json` in current MVP)
- source metadata and ingestion configuration

Downstream outputs:

- normalized documents (`documents.jsonl`)
- chunk records (`chunks.jsonl`)
- lineage records (`lineage.jsonl`)
- index-ready records (`index_records.jsonl`)

These outputs are the handoff contract to the other repositories.

## Shared Identifiers

Produced here:

- `source_id`
- `document_id`
- `chunk_id`

Produced for downstream traceability:

- `dataset_id` (used downstream)
- `dataset_version` (used downstream)
- `model_version` (used downstream)
- `query_id` (generated downstream)
- `trace_id` (generated downstream)

## Integration with Other Repositories

- `llm-observability-analytics` consumes `document_id` and `chunk_id` from ingestion outputs to attribute retrieval and grounding events.
- `llm-dataset-foundry` consumes normalized documents/chunks as source context during dataset curation.

See:

- `docs/data-contracts.md`
- `docs/integration.md`
- `examples/integration/`

## Local Development

Prerequisites:

- Python 3.12+
- GNU Make (or run equivalent commands directly)

Setup:

```bash
python -m venv .venv
. .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .[dev]
```

Common commands:

```bash
make format
make lint
make typecheck
make test
make ci
```

CLI:

```bash
python -m llm_knowledge_ingestion.cli.main --dry-run --config configs/base.yaml
python -m llm_knowledge_ingestion.cli.main --config configs/base.yaml
```

See detailed run and artifact documentation in `docs/mvp-ingestion.md`.


## Cross-Repo Consistency Checks

- Machine-readable summary: docs/shared-contract-summary.json`n- Manual validator: python scripts/validate_shared_contracts.py`n- Cross-repo check example:
  python scripts/validate_shared_contracts.py --peer ../llm-observability-analytics/docs/shared-contract-summary.json --peer ../llm-dataset-foundry/docs/shared-contract-summary.json

