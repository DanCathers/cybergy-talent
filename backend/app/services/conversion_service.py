"""AI mapping / conversion service.

This is the "intelligence" of Cybergy Talent. It takes the raw text extracted
from a resume and asks a Large Language Model (LLM) to map it into the HR Open
Standards :class:`PersonProfile` structure, returning strict JSON that we then
validate with Pydantic.

We use the Abacus AI OpenAI-compatible endpoint via the official ``openai``
Python client, pointed at Abacus AI's base URL.
"""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.hr_open_standards import PersonProfile

# Module logger so AI failures are visible in the container logs instead of
# being silently swallowed (they still won't crash the upload flow).
logger = logging.getLogger("cybergy.ai_mapping")

# ---------------------------------------------------------------------------
# The system prompt describes the target schema to the model in plain language
# and demands strict JSON output. Keeping it as a module constant makes it easy
# to review and version-control.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are an expert resume parser that maps unstructured resume text onto the
HR Open Standards v4.2.0 PersonProfileType data model.

Return ONLY a single valid JSON object (no markdown, no commentary) with this
structure. Populate every field you can confidently infer from the resume and
OMIT fields you cannot determine (do not invent data). Use ISO-8601 date
strings (YYYY-MM or YYYY-MM-DD) where possible.

{
  "name": {
    "formattedName": "full name",
    "given": "first name",
    "middle": "middle name/initial",
    "family": "last name",
    "qualificationAffixCode": {"value": "Ph.D"}
  },
  "communication": {
    "address": [{"line": "", "city": "", "countrySubdivision": "",
                 "postalCode": "", "countryCode": ""}],
    "phone": [{"formattedNumber": "", "useCode": "mobile"}],
    "email": [{"address": "", "useCode": "personal"}],
    "web": [{"url": "", "useCode": "linkedin"}]
  },
  "profileName": "a short label, e.g. 'Senior Software Engineer'",
  "languageCode": "en",
  "education": [{
    "institution": {"name": "university name", "location": {"city": "", "countryCode": ""}},
    "department": {"name": ""},
    "programs": ["program name"],
    "educationDegrees": [{"name": "B.Sc. Computer Science", "date": "2015-06",
      "specializations": [{"name": "Artificial Intelligence", "type": "major"}]}],
    "currentlyAttendingIndicator": false,
    "start": "2011-09", "end": "2015-06",
    "descriptions": ["honors, GPA, relevant coursework"]
  }],
  "employment": [{
    "organization": {"name": "company", "location": {"city": "", "countryCode": ""}},
    "positionHistories": [{
      "title": "job title",
      "resourceRelationshipCode": "Employee",
      "start": "2018-01", "end": "2022-03", "current": false,
      "descriptions": ["achievement or responsibility", "another bullet point"]
    }],
    "start": "2018-01", "end": "2022-03", "current": false
  }],
  "certifications": [{"name": "AWS Certified Solutions Architect",
    "issuingAuthority": {"name": "Amazon Web Services"},
    "status": "active", "issued": "2021-05",
    "effectiveTimePeriod": {"validFrom": "2021-05", "validTo": "2024-05"}}],
  "licenses": [{"name": "", "issuingAuthority": {"name": ""}, "status": "active"}],
  "qualifications": [{
    "competencyName": "Python",
    "description": "skill context",
    "proficiencyLevel": {"scoresText": [{"value": "expert"}]},
    "experienceMeasure": {"value": 5, "unitCode": "ANN"}
  }],
  "affiliations": [{"organization": {"name": ""}, "role": "", "startDate": "", "endDate": ""}],
  "publications": [{"title": "", "type": "article", "date": "", "journal": "", "publisher": ""}],
  "patents": [{"title": "", "status": "issued", "inventorNames": [""]}],
  "militaryService": [{"branch": "", "startingRank": "", "endingRank": "",
    "start": "", "end": "", "dischargeStatus": ""}],
  "references": [{"personName": {"formattedName": ""}, "positionTitle": "",
    "organizationName": ""}]
}

IMPORTANT:
- SKILLS go into "qualifications" as PersonCompetency objects (competencyName).
- Include ALL identifiable skills as separate qualification entries.
- Return an empty array for any section not present in the resume.
- Output must be strictly valid JSON parseable by json.loads().

HR OPEN STANDARDS CODED-VALUE RULES (use these EXACT forms):
- "resourceRelationshipCode" MUST be exactly "Employee" (a direct employee) or
  "VendorEmployee" (a contractor/consultant/temp). Always capitalized.
- "unitCode" in experienceMeasure MUST be a UN/ECE code, NOT an English word:
  use "ANN" for years, "MON" for months, "WEE" for weeks, "DAY" for days,
  "HUR" for hours.
- "proficiencyLevel" MUST be an object shaped like
  {"scoresText": [{"value": "expert"}]} — never a bare string.
- Any "id" field MUST be an object like {"value": "the-identifier"}, never a
  bare string.
"""


class ConversionService:
    """Maps raw resume text to a validated HR Open Standards profile."""

    def __init__(self) -> None:
        """Create the async OpenAI-compatible client pointed at Abacus AI."""
        # The AsyncOpenAI client lets us ``await`` API calls without blocking.
        self._client = AsyncOpenAI(
            api_key=settings.ABACUS_API_KEY or "not-set",
            base_url=settings.ABACUS_BASE_URL,
        )
        self._model = settings.AI_MODEL

    async def map_resume_text(self, raw_text: str) -> PersonProfile:
        """Convert raw resume text into a validated :class:`PersonProfile`.

        Steps:
          1. Call the LLM with the schema-describing system prompt.
          2. Parse the returned JSON.
          3. Validate it against the Pydantic model (graceful on failure).

        Returns:
            A :class:`PersonProfile`. On any failure it returns a minimal,
            valid profile rather than raising, so an upload never hard-fails.
        """
        # Guard: if there's basically no text, skip the API call entirely.
        if not raw_text or len(raw_text.strip()) < 20:
            return PersonProfile()

        try:
            content = await self._call_llm(raw_text)
        except Exception as exc:  # noqa: BLE001 - we deliberately degrade gracefully
            # Network/auth/quota problems shouldn't crash the upload flow, but
            # we DO log the real error so it's diagnosable (wrong base URL,
            # bad API key, quota, etc.) instead of a silent "AI unavailable".
            logger.error(
                "AI mapping failed (base_url=%s model=%s): %r",
                settings.ABACUS_BASE_URL,
                self._model,
                exc,
            )
            return PersonProfile(profileName="Unmapped resume (AI unavailable)")

        # Extract the JSON object from the model's text response.
        data = self._safe_json_loads(content)
        if data is None:
            return PersonProfile(profileName="Unmapped resume (invalid AI JSON)")

        # Validate against the HR Open Standards model. ``extra="ignore"`` in
        # the schema means unexpected keys are dropped instead of erroring.
        try:
            return PersonProfile.model_validate(data)
        except ValidationError:
            # As a last resort, try to keep whatever validated cleanly by
            # constructing an empty profile (never return malformed data).
            return PersonProfile(profileName="Partially mapped resume")

    async def _call_llm(self, raw_text: str) -> str:
        """Send the resume text to the LLM and return the raw response text.

        We cap the input length to keep requests within model limits and set a
        low temperature for deterministic, faithful extraction.
        """
        # Truncate extremely long resumes to a safe character budget.
        trimmed = raw_text[:24000]

        # ``response_format`` asks the API to return a JSON object directly.
        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Resume text:\n\n{trimmed}"},
            ],
        )
        # The message content holds the model's JSON string.
        return response.choices[0].message.content or ""

    @staticmethod
    def _safe_json_loads(content: str) -> dict | None:
        """Parse JSON from an LLM response, tolerating minor formatting noise.

        Some models wrap JSON in ```json fences``` despite instructions, so we
        strip those before parsing. Returns ``None`` if parsing fails.
        """
        text = content.strip()
        # Remove surrounding markdown code fences if present.
        if text.startswith("```"):
            # Drop the first line (``` or ```json) and any trailing fence.
            text = text.split("\n", 1)[-1]
            if text.rstrip().endswith("```"):
                text = text.rstrip()[:-3]
        try:
            parsed = json.loads(text)
            # Only accept a top-level object (dict); anything else is invalid.
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None


# A module-level singleton so callers can simply import and use it.
conversion_service = ConversionService()
