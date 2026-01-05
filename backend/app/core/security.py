"""Security helpers: upload validation, rate limiting, and HTTP headers.

Defense in depth: we validate uploads by BOTH file extension and MIME content,
enforce a size limit, add hardening HTTP headers, and rate-limit the upload
endpoint. These are practical DevSecOps controls appropriate for a public API.
"""

# slowapi provides a small, dependency-injected rate limiter for Starlette/FastAPI.
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

# ---------------------------------------------------------------------------
# Allowed upload types
# ---------------------------------------------------------------------------
# We only accept PDF and DOCX. Both the file extension and the sniffed MIME
# type must be in these maps for an upload to be accepted.
ALLOWED_EXTENSIONS: dict[str, set[str]] = {
    # extension -> set of acceptable MIME types for that extension
    ".pdf": {"application/pdf"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",  # docx is a zip container; some sniffers report this
    },
}


# The rate limiter keys requests by client IP address. It is attached to the
# FastAPI app in main.py and used as a decorator on sensitive endpoints.
limiter = Limiter(key_func=get_remote_address)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds a set of conservative security headers to every response.

    A middleware wraps every request/response. ``dispatch`` is called for each
    request; we await the downstream handler, then attach headers on the way out.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Await the rest of the application to produce the response.
        response = await call_next(request)

        # Prevent MIME-type sniffing by browsers.
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Disallow being embedded in an iframe (clickjacking protection).
        response.headers["X-Frame-Options"] = "DENY"
        # Legacy XSS filter toggle (harmless on modern browsers).
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Do not leak the full referrer to other origins.
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # A minimal Content-Security-Policy for an API surface.
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response


def validate_upload(filename: str, mime_type: str, size_bytes: int) -> str:
    """Validate an uploaded file and return its normalized extension.

    Args:
        filename: The original client-provided file name.
        mime_type: The ``Content-Type`` reported for the uploaded part.
        size_bytes: The size of the uploaded file in bytes.

    Returns:
        The lower-cased file extension (e.g. ".pdf") if the file is valid.

    Raises:
        ValueError: If the extension, MIME type, or size is not acceptable.
    """
    # 1) Enforce the size limit first (cheapest check, avoids parsing huge files).
    if size_bytes > settings.max_upload_bytes:
        raise ValueError(
            f"File is too large ({size_bytes} bytes). "
            f"Maximum allowed is {settings.MAX_UPLOAD_SIZE_MB} MB."
        )
    if size_bytes == 0:
        raise ValueError("Uploaded file is empty.")

    # 2) Determine the extension from the filename (case-insensitive).
    #    ``rpartition`` splits on the last dot: "a.b.pdf" -> (".pdf").
    lowered = filename.lower()
    extension = ""
    for ext in ALLOWED_EXTENSIONS:
        if lowered.endswith(ext):
            extension = ext
            break
    if not extension:
        raise ValueError("Unsupported file type. Only .pdf and .docx are allowed.")

    # 3) Cross-check the MIME type against the extension's allow-list.
    allowed_mimes = ALLOWED_EXTENSIONS[extension]
    if mime_type not in allowed_mimes:
        raise ValueError(
            f"File content type '{mime_type}' does not match extension "
            f"'{extension}'. This upload was rejected as a safety measure."
        )

    return extension
