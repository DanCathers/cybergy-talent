"""JSON output converter (HR Open Standards compliant)."""

from __future__ import annotations

import json

from app.converters.base_converter import BaseConverter
from app.schemas.hr_open_standards import PersonProfile


class JsonConverter(BaseConverter):
    """Serializes a :class:`PersonProfile` to HR Open Standards JSON."""

    format_name = "json"
    media_type = "application/json"
    file_extension = ".json"

    def convert(self, profile: PersonProfile) -> str:
        """Return the profile as a pretty-printed JSON string.

        ``profile.with_attribution()`` returns a dict that already contains the
        required ``_attribution`` and ``_compliance`` notices at the top.
        """
        payload = profile.with_attribution()
        # ``indent=2`` makes the output human-readable. ``ensure_ascii=False``
        # preserves accented characters (e.g. names) instead of escaping them.
        return json.dumps(payload, indent=2, ensure_ascii=False)
