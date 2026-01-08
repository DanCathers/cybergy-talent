"""Abstract base class for output converters (the Factory pattern).

A converter turns a validated :class:`PersonProfile` into a serialized output
format (JSON or XML). Every converter must embed the required HR Open
Standards attribution/compliance notices in its output.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.hr_open_standards import PersonProfile


class BaseConverter(ABC):
    """Common interface for all output converters."""

    #: The output format name, e.g. "json" or "xml".
    format_name: str = ""
    #: The MIME type used when serving the output as a download.
    media_type: str = "application/octet-stream"
    #: The file extension used for downloads, e.g. ".json".
    file_extension: str = ""

    @abstractmethod
    def convert(self, profile: PersonProfile) -> str:
        """Serialize ``profile`` to a string in this converter's format.

        Implementations MUST include the HR Open Standards attribution and
        compliance notices in the produced document.
        """
        ...
