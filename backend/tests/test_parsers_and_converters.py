"""Unit tests for parsers, converters, and the parser/converter factories.

These tests run WITHOUT a database or network, so they're fast and safe for CI.
"""

from __future__ import annotations

import json

import pytest

from app.converters.converter_factory import ConverterFactory
from app.parsers.parser_factory import ParserFactory
from app.schemas.hr_open_standards import (
    HR_OPEN_ATTRIBUTION,
    PersonName,
    PersonProfile,
)


def _sample_profile() -> PersonProfile:
    """Build a small profile used across several tests."""
    return PersonProfile(
        name=PersonName(formattedName="Ada Lovelace", given="Ada", family="Lovelace"),
        profileName="Mathematician",
    )


def test_parser_factory_supports_pdf_and_docx() -> None:
    """The factory should know about both supported extensions."""
    assert set(ParserFactory.supported_extensions()) == {".pdf", ".docx"}


def test_parser_factory_rejects_unknown_extension() -> None:
    """Requesting an unsupported extension should raise ValueError."""
    with pytest.raises(ValueError):
        ParserFactory.get_parser(".txt")


def test_json_converter_includes_attribution() -> None:
    """Generated JSON must carry the HR Open Standards attribution notice."""
    converter = ConverterFactory.get_converter("json")
    output = converter.convert(_sample_profile())
    data = json.loads(output)  # ensures the output is valid JSON
    assert data["_attribution"] == HR_OPEN_ATTRIBUTION
    assert data["name"]["formattedName"] == "Ada Lovelace"


def test_xml_converter_includes_attribution_comment() -> None:
    """Generated XML must contain the attribution as a comment node."""
    converter = ConverterFactory.get_converter("xml")
    output = converter.convert(_sample_profile())
    assert HR_OPEN_ATTRIBUTION in output
    assert "<PersonProfile" in output
    assert "Ada Lovelace" in output


def test_converter_factory_rejects_unknown_format() -> None:
    """Unknown output formats should raise ValueError."""
    with pytest.raises(ValueError):
        ConverterFactory.get_converter("yaml")


def test_profile_with_attribution_orders_notice_first() -> None:
    """with_attribution() should place notice keys before profile data."""
    keys = list(_sample_profile().with_attribution().keys())
    assert keys[0] == "_attribution"
    assert "name" in keys
