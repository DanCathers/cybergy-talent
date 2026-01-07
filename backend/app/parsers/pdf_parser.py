"""PDF parsing strategy.

We try two libraries for robustness:
  1. PyMuPDF (imported as ``fitz``) — very fast and accurate for most PDFs.
  2. pdfplumber — a layout-aware fallback that sometimes does better on
     multi-column resumes.

If PyMuPDF yields little or no text (e.g. an unusual layout), we fall back to
pdfplumber before giving up.
"""

from __future__ import annotations

import asyncio
import io

import fitz  # PyMuPDF
import pdfplumber

from app.parsers.base_parser import BaseParser


class PdfParser(BaseParser):
    """Extracts text from PDF resumes."""

    extension = ".pdf"

    async def extract_text(self, file_bytes: bytes) -> str:
        """Extract text from PDF bytes, trying PyMuPDF then pdfplumber.

        PDF libraries are synchronous and CPU-bound. To avoid blocking the
        async event loop, we run the heavy work in a thread via
        ``asyncio.to_thread`` and ``await`` the result.
        """
        # Run the blocking extraction in a worker thread and await it.
        text = await asyncio.to_thread(self._extract_with_pymupdf, file_bytes)

        # If PyMuPDF produced very little text, try the pdfplumber fallback.
        if len(text.strip()) < 30:
            fallback = await asyncio.to_thread(self._extract_with_pdfplumber, file_bytes)
            if len(fallback.strip()) > len(text.strip()):
                text = fallback

        if not text.strip():
            raise ValueError("Could not extract any text from the PDF file.")

        return self._normalize(text)

    @staticmethod
    def _extract_with_pymupdf(file_bytes: bytes) -> str:
        """Extract text using PyMuPDF (fitz). Synchronous/blocking."""
        parts: list[str] = []
        # ``fitz.open`` can read straight from an in-memory bytes stream.
        # The ``with`` block guarantees the document is closed afterwards.
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:  # iterate over each page
                parts.append(page.get_text("text"))
        return "\n".join(parts)

    @staticmethod
    def _extract_with_pdfplumber(file_bytes: bytes) -> str:
        """Extract text using pdfplumber. Synchronous/blocking."""
        parts: list[str] = []
        # Wrap the bytes in a BytesIO so pdfplumber can treat it like a file.
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                # ``extract_text`` may return None for image-only pages.
                parts.append(page.extract_text() or "")
        return "\n".join(parts)
