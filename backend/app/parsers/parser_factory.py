"""Parser factory — selects the right parsing strategy for a file type.

This is the *Factory* half of the Strategy pattern: callers ask the factory
for a parser by file extension and receive a ready-to-use strategy object,
without needing to know which concrete class implements it.
"""

from __future__ import annotations

from app.parsers.base_parser import BaseParser
from app.parsers.docx_parser import DocxParser
from app.parsers.pdf_parser import PdfParser


class ParserFactory:
    """Creates the appropriate ``BaseParser`` for a given file extension."""

    # A registry mapping file extension -> the strategy class that handles it.
    # To support a new format, add one entry here and write its parser class.
    _registry: dict[str, type[BaseParser]] = {
        PdfParser.extension: PdfParser,
        DocxParser.extension: DocxParser,
    }

    @classmethod
    def get_parser(cls, extension: str) -> BaseParser:
        """Return a parser instance for ``extension`` (e.g. ".pdf").

        Args:
            extension: The lower-cased file extension, including the leading dot.

        Returns:
            An instance of the matching parser strategy.

        Raises:
            ValueError: If no parser is registered for the extension.
        """
        parser_class = cls._registry.get(extension.lower())
        if parser_class is None:
            supported = ", ".join(sorted(cls._registry))
            raise ValueError(f"No parser available for '{extension}'. Supported: {supported}.")
        # Instantiate and return the chosen strategy.
        return parser_class()

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """Return the list of extensions the factory can handle."""
        return sorted(cls._registry)
