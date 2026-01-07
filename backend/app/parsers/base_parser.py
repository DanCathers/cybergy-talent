"""Abstract base class for resume parsers (the Strategy pattern).

The *Strategy pattern* lets us define a family of interchangeable algorithms
(here: "how to extract text from a file") behind one common interface. The
rest of the app depends only on this interface, so adding a new file type
later (e.g. .rtf) means writing one new strategy class — nothing else changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Common interface every concrete parser must implement.

    ``ABC`` marks this as an Abstract Base Class: it cannot be instantiated
    directly, and any subclass MUST implement the ``@abstractmethod`` below.
    """

    #: The file extension this strategy handles, e.g. ".pdf". Subclasses set it.
    extension: str = ""

    @abstractmethod
    async def extract_text(self, file_bytes: bytes) -> str:
        """Extract plain text from the raw bytes of a resume file.

        Args:
            file_bytes: The full contents of the uploaded file.

        Returns:
            The extracted text as a single string.

        Raises:
            ValueError: If the file cannot be parsed.
        """
        # ``...`` (Ellipsis) is a placeholder body for abstract methods.
        ...

    @staticmethod
    def _normalize(text: str) -> str:
        """Tidy up extracted text: collapse excess blank lines and spaces.

        Static because it needs no instance state — it's a pure helper.
        """
        # Split into lines, strip trailing spaces, and drop runs of blank lines.
        lines = [line.rstrip() for line in text.splitlines()]
        cleaned: list[str] = []
        blank_run = 0
        for line in lines:
            if line.strip() == "":
                blank_run += 1
                # Keep at most one consecutive blank line for readability.
                if blank_run <= 1:
                    cleaned.append("")
            else:
                blank_run = 0
                cleaned.append(line)
        return "\n".join(cleaned).strip()
