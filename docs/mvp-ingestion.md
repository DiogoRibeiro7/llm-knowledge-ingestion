# MVP Ingestion Pipeline

## Overview

The MVP pipeline ingests local files (`.txt`, `.md`, `.json`), normalizes them into shared contract models, computes deterministic content hashes, generates chunks, and writes index-ready artifacts.

## How To Run

Install dependencies:

```bash
pip install -e .[dev]
```

Dry run (configuration and input discovery only):

```bash
python -m llm_knowledge_ingestion.cli.main --dry-run --config configs/base.yaml
```

Execute ingestion:

```bash
python -m llm_knowledge_ingestion.cli.main --config configs/base.yaml
```

## Expected Input Structure

Input path is configured via `ingestion.input_path` in `configs/base.yaml`.

Supported files:

- `.txt`
- `.md`
- `.json`

The pipeline recursively scans the input directory and processes supported files in stable sorted order.

## Expected Output Artifacts

Output destinations are controlled by the `output` section in config.

- `normalized_documents_path/documents.jsonl`
  - One normalized document record per line.
- `chunks_path/chunks.jsonl`
  - One chunk record per line.
- `lineage_path/lineage.jsonl`
  - One lineage reference per chunk.
- `index_records_path/index_records.jsonl`
  - One index-ready record per chunk.
- `run_result_path`
  - JSON summary including counters and warnings.

All JSON output is deterministic at record field level (`sort_keys=True`) to support diffability and repeatability.
