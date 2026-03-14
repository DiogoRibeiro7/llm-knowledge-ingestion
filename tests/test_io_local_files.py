from __future__ import annotations

from pathlib import Path

import pytest

from llm_knowledge_ingestion.io.local_files import discover_input_files, load_local_document


def test_load_plain_text_document(tmp_path: Path) -> None:
    file_path = tmp_path / "note.txt"
    file_path.write_text("hello world", encoding="utf-8")

    doc = load_local_document(file_path)
    assert doc.source_type == "text"
    assert doc.content == "hello world"
    assert doc.title == "note"


def test_load_markdown_document(tmp_path: Path) -> None:
    file_path = tmp_path / "note.md"
    file_path.write_text("# Header", encoding="utf-8")

    doc = load_local_document(file_path)
    assert doc.source_type == "markdown"
    assert doc.content.startswith("#")


def test_load_json_document_is_canonicalized(tmp_path: Path) -> None:
    file_path = tmp_path / "doc.json"
    file_path.write_text('{"b":2,"a":1,"title":"JSON Title"}', encoding="utf-8")

    doc = load_local_document(file_path)
    assert doc.source_type == "json"
    assert doc.title == "JSON Title"
    assert doc.content == '{"a":1,"b":2,"title":"JSON Title"}'


def test_discover_supported_files_only(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "c.json").write_text("{}", encoding="utf-8")
    (tmp_path / "skip.csv").write_text("x", encoding="utf-8")

    files = discover_input_files(tmp_path)
    assert [path.name for path in files] == ["a.txt", "b.md", "c.json"]


def test_invalid_json_file_raises(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.json"
    file_path.write_text('{"a":', encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_local_document(file_path)


def test_unsupported_extension_raises(tmp_path: Path) -> None:
    file_path = tmp_path / "file.xml"
    file_path.write_text("<x/>", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_local_document(file_path)
