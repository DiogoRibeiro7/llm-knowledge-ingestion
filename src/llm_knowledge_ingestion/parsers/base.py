from __future__ import annotations

from abc import ABC, abstractmethod


class DocumentParser(ABC):
    """Base parser contract for source document extraction."""

    @abstractmethod
    def parse(self, raw_payload: bytes) -> str:
        """Return extracted textual content from raw payload."""


class PdfParser(DocumentParser):
    def parse(self, raw_payload: bytes) -> str:
        raise NotImplementedError("PDF parser not implemented yet")


class MarkdownParser(DocumentParser):
    def parse(self, raw_payload: bytes) -> str:
        raise NotImplementedError("Markdown parser not implemented yet")


class HtmlParser(DocumentParser):
    def parse(self, raw_payload: bytes) -> str:
        raise NotImplementedError("HTML parser not implemented yet")


class JsonParser(DocumentParser):
    def parse(self, raw_payload: bytes) -> str:
        raise NotImplementedError("JSON parser not implemented yet")


class TextParser(DocumentParser):
    def parse(self, raw_payload: bytes) -> str:
        return raw_payload.decode("utf-8", errors="replace")
