from __future__ import annotations

import argparse
from pathlib import Path

from llm_knowledge_ingestion.io.local_files import discover_input_files
from llm_knowledge_ingestion.pipeline.config import load_config
from llm_knowledge_ingestion.pipeline.orchestrator import IngestionPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-knowledge-ingest")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to configuration file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and planned stages without executing ingestion",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(Path(args.config))

    if args.dry_run:
        files = discover_input_files(config.ingestion.input_path)
        print(
            "Dry run successful: "
            f"{min(len(files), config.ingestion.max_documents)} document(s) selected "
            f"from {config.ingestion.input_path}"
        )
        return 0

    pipeline = IngestionPipeline(config=config)
    result = pipeline.run()
    print(
        "Ingestion completed: "
        f"documents={result.documents_processed} "
        f"chunks={result.chunks_generated} "
        f"result={config.output.run_result_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
