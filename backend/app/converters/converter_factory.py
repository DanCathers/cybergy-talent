"""Converter factory — returns the right output converter by format name.

The *Factory pattern* centralizes object creation. Endpoints ask for a
converter by name ("json"/"xml") and get back a ready object implementing the
common :class:`BaseConverter` interface.
"""

from __future__ import annotations

from app.converters.base_converter import BaseConverter
from app.converters.json_converter import JsonConverter
from app.converters.xml_converter import XmlConverter


class ConverterFactory:
    """Creates output converters for supported formats."""

    # Registry of format name -> converter class.
    _registry: dict[str, type[BaseConverter]] = {
        JsonConverter.format_name: JsonConverter,
        XmlConverter.format_name: XmlConverter,
    }

    @classmethod
    def get_converter(cls, format_name: str) -> BaseConverter:
        """Return a converter instance for ``format_name`` ("json" or "xml").

        Raises:
            ValueError: If the format is not supported.
        """
        converter_class = cls._registry.get(format_name.lower())
        if converter_class is None:
            supported = ", ".join(sorted(cls._registry))
            raise ValueError(f"Unsupported output format '{format_name}'. Supported: {supported}.")
        return converter_class()

    @classmethod
    def supported_formats(cls) -> list[str]:
        """Return the list of supported output format names."""
        return sorted(cls._registry)
