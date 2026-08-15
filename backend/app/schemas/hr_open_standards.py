"""HR Open Standards v4.2.0 — Pydantic models.

These models are a Python/Pydantic mapping of the HR Open Standards
``PersonProfileType`` and its nested types. They intentionally mirror the
field names used in the official JSON schemas (camelCase) so that the JSON we
emit is standards-compliant.

Learning notes for Python beginners
------------------------------------
* Every model subclasses ``BaseModel`` from Pydantic. Pydantic validates and
  coerces data against the type hints automatically.
* ``Optional[X]`` (written ``X | None``) means the field may be missing/null.
* ``list[X]`` declares a list whose items are of type ``X``.
* ``Field(default=..., description=...)`` documents a field and sets defaults.
* We keep almost everything optional because real resumes are messy and the
  AI extractor may only be able to fill in some fields.

Attribution (required by the HR Open Standards license) is embedded in every
serialized output via the constants defined at the bottom of this module.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Required HR Open Standards attribution / compliance strings.
# These are injected into every generated JSON and XML document.
# ---------------------------------------------------------------------------
HR_OPEN_ATTRIBUTION = (
    "Copyright © The HR Open Standards Consortium. All Rights Reserved. "
    "http://www.hropenstandards.org"
)
HR_OPEN_COMPLIANCE = (
    "This product implements and complies with the Version 4.2.0 Specifications "
    "as published by the HR Open Standards Consortium at "
    "http://www.hropenstandards.org"
)
HR_OPEN_VERSION = "4.2.0"


class HROpenBase(BaseModel):
    """Shared base configuration for all HR Open Standards models.

    ``ConfigDict`` options:
      * ``populate_by_name`` lets us populate fields by their Python name.
      * ``extra="ignore"`` drops unexpected keys the LLM might invent instead
        of raising an error (graceful handling of imperfect AI output).
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# ---------------------------------------------------------------------------
# Small reusable value types
# ---------------------------------------------------------------------------
class CodeType(HROpenBase):
    """A coded value with an optional human label (HR Open ``CodeType``)."""

    name: str | None = Field(default=None, description="Human-readable label.")
    value: str | None = Field(default=None, description="The code value.")


class EffectiveTimePeriod(HROpenBase):
    """A validity window with optional start/end dates (ISO-8601 strings)."""

    validFrom: str | None = Field(default=None, description="Start date.")
    validTo: str | None = Field(default=None, description="End date.")


class Identifier(HROpenBase):
    """HR Open ``IdentifierType`` — a coded identifier object.

    The HR Open schema requires identifiers to be OBJECTS with a required
    ``value`` (not a bare string). Example: ``{"value": "0687-abc"}``.

    The ``coerce_from_string`` validator lets us accept a plain string (which
    the AI or older code may produce) and wrap it into the correct object shape
    automatically, so the emitted JSON is always standards-compliant.
    """

    value: str | None = Field(default=None, description="The identifier value.")
    schemeId: str | None = Field(default=None, description="Identifier scheme id.")
    schemeVersionId: str | None = Field(default=None, description="Scheme version.")
    schemeAgencyId: str | None = Field(default=None, description="Managing agency.")
    description: str | None = None


class ScoreText(HROpenBase):
    """HR Open ``ScoreTextType`` — a textual score with a required ``value``."""

    value: str | None = Field(default=None, description="The score text, e.g. 'expert'.")
    scoreTextCode: str | None = None
    minimum: str | None = None
    maximum: str | None = None


class BaseScore(HROpenBase):
    """HR Open ``BaseScoreType`` — numeric and/or textual scores.

    A proficiency level is expressed as a ``BaseScore`` object (NOT a bare
    string). Example: ``{"scoresText": [{"value": "expert"}]}``.
    """

    scoresText: list[ScoreText] = Field(default_factory=list)

    @field_validator("scoresText", mode="before")
    @classmethod
    def _coerce_scores(cls, v):
        # Accept a plain string or list of strings and wrap into ScoreText objs.
        if v is None:
            return []
        if isinstance(v, str):
            return [{"value": v}]
        if isinstance(v, list):
            return [{"value": item} if isinstance(item, str) else item for item in v]
        return v


# ---------------------------------------------------------------------------
# Person name
# ---------------------------------------------------------------------------
class PersonName(HROpenBase):
    """HR Open ``PersonNameType`` — a person's name broken into parts."""

    formattedName: str | None = Field(default=None, description="Full name as written out.")
    given: str | None = Field(default=None, description="Given / first name.")
    middle: str | None = Field(default=None, description="Middle name(s) or initials.")
    family: str | None = Field(default=None, description="Family / last name.")
    preferred: str | None = Field(default=None, description="Preferred name if different.")
    preferredSalutationCode: CodeType | None = Field(default=None, description="Mr., Dr., etc.")
    generationAffixCode: CodeType | None = Field(default=None, description="Jr., Sr., III, etc.")
    qualificationAffixCode: CodeType | None = Field(default=None, description="Ph.D, M.Sc, etc.")


# ---------------------------------------------------------------------------
# Communication (contact) details
# ---------------------------------------------------------------------------
class Address(HROpenBase):
    """A postal address (subset of HR Open ``AddressType``)."""

    line: str | None = Field(default=None, description="Street address line.")
    city: str | None = None
    countrySubdivision: str | None = Field(default=None, description="State / province.")
    postalCode: str | None = None
    countryCode: str | None = None


class Phone(HROpenBase):
    """A telephone number with an optional usage label (home/work/mobile)."""

    formattedNumber: str | None = None
    useCode: str | None = Field(default=None, description="e.g. mobile, work, home.")


class Email(HROpenBase):
    """An email address with an optional usage label."""

    address: str | None = None
    useCode: str | None = None


class Web(HROpenBase):
    """A website / social profile URL (LinkedIn, GitHub, portfolio, ...)."""

    url: str | None = None
    useCode: str | None = Field(default=None, description="e.g. linkedin, github, portfolio.")


class Communication(HROpenBase):
    """HR Open ``CommunicationType`` — all contact channels grouped together."""

    address: list[Address] = Field(default_factory=list)
    phone: list[Phone] = Field(default_factory=list)
    email: list[Email] = Field(default_factory=list)
    web: list[Web] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Organization (used by employment, education, certifications, ...)
# ---------------------------------------------------------------------------
class Organization(HROpenBase):
    """A simplified HR Open ``OrganizationType`` (name + optional location)."""

    name: str | None = None
    location: Address | None = None


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------
class EducationSpecialization(HROpenBase):
    """A major/minor focus of study within a degree."""

    name: str | None = None
    type: str | None = Field(default=None, description="'major' or 'minor'.")


class EducationDegree(HROpenBase):
    """A degree/diploma awarded (or in progress)."""

    name: str | None = Field(default=None, description="e.g. 'B.Sc. Computer Science'.")
    date: str | None = Field(default=None, description="Date awarded (ISO-8601).")
    specializations: list[EducationSpecialization] = Field(default_factory=list)


class EducationAttendance(HROpenBase):
    """HR Open ``EducationAttendanceType`` — one school/college attendance."""

    institution: Organization | None = None
    department: Organization | None = None
    programs: list[str] = Field(default_factory=list)
    educationDegrees: list[EducationDegree] = Field(default_factory=list)
    currentlyAttendingIndicator: bool | None = None
    start: str | None = Field(default=None, description="Start date (ISO-8601).")
    end: str | None = Field(default=None, description="End date (ISO-8601).")
    descriptions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Employment
# ---------------------------------------------------------------------------
class PositionHistory(HROpenBase):
    """A single job/role held at an organization."""

    title: str | None = None
    resourceRelationshipCode: str | None = Field(
        default=None,
        description=(
            "Must be one of the HR Open ResourceRelationshipCodeList values: "
            "'Employee' or 'VendorEmployee' (capitalized)."
        ),
    )
    organization: Organization | None = Field(
        default=None, description="Department / sub-org, if relevant."
    )
    location: Address | None = None
    start: str | None = None
    end: str | None = None
    current: bool | None = Field(default=None, description="Still in this role?")
    descriptions: list[str] = Field(
        default_factory=list, description="Responsibilities / achievements."
    )

    @field_validator("resourceRelationshipCode", mode="before")
    @classmethod
    def _normalize_relationship_code(cls, v):
        """Coerce free-form/lowercase values into the valid enum.

        The HR Open ``ResourceRelationshipCodeList`` only allows exactly
        ``"Employee"`` or ``"VendorEmployee"``. The AI (or older code) may emit
        lowercase or synonyms like ``"employee"`` or ``"contractor"``; we map
        those to the closest valid, capitalized code so the JSON validates.
        """
        if v is None or not isinstance(v, str):
            return v
        key = v.strip().lower()
        if not key:
            return None
        # Synonyms that map to the "outside vendor / contractor" code.
        vendor_terms = {
            "vendoremployee",
            "vendor",
            "contractor",
            "contract",
            "temporary",
            "temp",
            "consultant",
            "freelance",
            "freelancer",
        }
        if key in vendor_terms:
            return "VendorEmployee"
        # Everything else (employee, permanent, full-time, part-time, ...) maps
        # to the standard "Employee" code.
        return "Employee"


class EmployerHistory(HROpenBase):
    """HR Open ``EmployerHistoryType`` — tenure at one employer."""

    organization: Organization | None = None
    positionHistories: list[PositionHistory] = Field(default_factory=list)
    start: str | None = None
    end: str | None = None
    current: bool | None = None


# ---------------------------------------------------------------------------
# Certifications & Licenses
# ---------------------------------------------------------------------------
class Certification(HROpenBase):
    """HR Open ``CertificationType`` — a professional certification."""

    name: str | None = None
    type: CodeType | None = None
    status: str | None = Field(default=None, description="active, expired, pending, ...")
    issuingAuthority: Organization | None = None
    effectiveTimePeriod: EffectiveTimePeriod | None = None
    issued: str | None = Field(default=None, description="Issue date (ISO-8601).")
    descriptions: list[str] = Field(default_factory=list)


class License(Certification):
    """HR Open ``LicenseType`` — extends CertificationType with restrictions.

    Inheriting from ``Certification`` mirrors the HR Open schema, which defines
    LicenseType via ``allOf CertificationType`` plus a few extra arrays.
    """

    endorsements: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Competencies (this is where SKILLS live)
# ---------------------------------------------------------------------------
class ExperienceMeasure(HROpenBase):
    """A measured amount of experience (e.g. 5 years)."""

    value: float | None = None
    unitCode: str | None = Field(
        default=None,
        description=(
            "HR Open UnitCodeList code for the time unit. Use 'ANN' for years, "
            "'MON' for months, 'WEE' for weeks, 'DAY' for days, 'HUR' for hours."
        ),
    )

    @field_validator("unitCode", mode="before")
    @classmethod
    def _normalize_unit_code(cls, v):
        """Coerce human words like 'year'/'years' into UnitCodeList codes.

        The HR Open ``UnitCodeList`` uses UN/ECE codes such as ``ANN`` (years)
        rather than the English word 'year'. We translate the common words the
        AI may emit into the correct code so the JSON validates.
        """
        if v is None or not isinstance(v, str):
            return v
        key = v.strip().lower()
        if not key:
            return None
        mapping = {
            "year": "ANN",
            "years": "ANN",
            "yr": "ANN",
            "yrs": "ANN",
            "annual": "ANN",
            "annually": "ANN",
            "month": "MON",
            "months": "MON",
            "mo": "MON",
            "week": "WEE",
            "weeks": "WEE",
            "wk": "WEE",
            "day": "DAY",
            "days": "DAY",
            "hour": "HUR",
            "hours": "HUR",
            "hr": "HUR",
            "hrs": "HUR",
        }
        # If the AI already gave a valid uppercase code, keep it as-is.
        if v.strip().upper() in {"ANN", "MON", "WEE", "DAY", "HUR"}:
            return v.strip().upper()
        return mapping.get(key, v)


class PersonCompetency(HROpenBase):
    """HR Open ``PersonCompetencyType`` — a skill/competency assertion."""

    competencyName: str | None = Field(default=None, description="The skill name.")
    description: str | None = None
    proficiencyLevel: BaseScore | None = Field(
        default=None,
        description=(
            "A BaseScore object, e.g. {'scoresText': [{'value': 'expert'}]}. "
            "A bare string like 'expert' is auto-wrapped into this shape."
        ),
    )
    lastUsedDate: str | None = None
    experienceMeasure: ExperienceMeasure | None = None

    @field_validator("proficiencyLevel", mode="before")
    @classmethod
    def _coerce_proficiency(cls, v):
        """Wrap a bare string proficiency into a BaseScore object.

        HR Open expects ``proficiencyLevel`` to be a ``BaseScoreType`` object,
        not a bare string. If the AI emits ``"expert"`` we convert it into
        ``{"scoresText": [{"value": "expert"}]}`` so the JSON is compliant.
        """
        if v is None:
            return v
        if isinstance(v, str):
            text = v.strip()
            if not text:
                return None
            return {"scoresText": [{"value": text}]}
        return v


# ---------------------------------------------------------------------------
# Affiliations, publications, patents, military, references
# ---------------------------------------------------------------------------
class OrganizationAffiliation(HROpenBase):
    """HR Open ``OrganizationAffiliationType`` — membership in a group."""

    organization: Organization | None = None
    role: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    descriptions: list[str] = Field(default_factory=list)


class PublicationContributor(HROpenBase):
    """A contributor (author/editor) to a publication."""

    name: str | None = None
    role: str | None = None


class Publication(HROpenBase):
    """HR Open ``PublicationType`` — a book, article, or paper."""

    title: str | None = None
    type: str | None = Field(default=None, description="book, article, paper, ...")
    date: str | None = None
    abstract: str | None = None
    contributors: list[PublicationContributor] = Field(default_factory=list)
    journal: str | None = None
    publisher: str | None = None


class Patent(HROpenBase):
    """HR Open ``PatentType`` — a registered patent."""

    title: str | None = None
    inventorNames: list[str] = Field(default_factory=list)
    assigneeNames: list[str] = Field(default_factory=list)
    issuingAuthority: Organization | None = None
    status: str | None = Field(default=None, description="filed, pending, issued.")
    descriptions: list[str] = Field(default_factory=list)


class MilitaryService(HROpenBase):
    """HR Open ``MilitaryServiceType`` — a period of military service."""

    countryCode: str | None = None
    branch: str | None = None
    division: str | None = None
    startingRank: str | None = None
    endingRank: str | None = None
    dischargeStatus: str | None = None
    start: str | None = None
    end: str | None = None
    honors: list[str] = Field(default_factory=list)
    descriptions: list[str] = Field(default_factory=list)


class Referee(HROpenBase):
    """HR Open ``RefereeType`` — a professional reference."""

    personName: PersonName | None = None
    positionTitle: str | None = None
    organizationName: str | None = None
    communication: Communication | None = None


class Attachment(HROpenBase):
    """HR Open ``AttachmentType`` — a link/reference to a related document."""

    id: Identifier | None = Field(
        default=None,
        description="Identifier object, e.g. {'value': '...'}. Bare strings are auto-wrapped.",
    )
    url: str | None = None
    descriptions: list[str] = Field(default_factory=list)

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_id(cls, v):
        """Wrap a bare string id into an IdentifierType object."""
        if isinstance(v, str):
            text = v.strip()
            return {"value": text} if text else None
        return v


# ---------------------------------------------------------------------------
# Top-level PersonProfileType — the full resume object
# ---------------------------------------------------------------------------
class PersonProfile(HROpenBase):
    """HR Open ``PersonProfileType`` — the complete structured resume.

    This is what the AI mapping service produces and what we store, serve, and
    export as JSON/XML. Every section is optional so partial resumes validate.
    """

    id: Identifier | None = Field(
        default=None,
        description=(
            "Stable identifier for this profile as an IdentifierType object, "
            "e.g. {'value': '0687-...'}. A bare string is auto-wrapped."
        ),
    )
    name: PersonName | None = None
    communication: Communication | None = None
    profileName: str | None = Field(default=None, description="A label for this profile.")
    languageCode: str | None = Field(default="en", description="Primary language.")

    education: list[EducationAttendance] = Field(default_factory=list)
    employment: list[EmployerHistory] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    licenses: list[License] = Field(default_factory=list)
    # NOTE: in HR Open Standards, skills are modeled as "qualifications"
    # (PersonCompetencyType). We keep that name for standards compliance.
    qualifications: list[PersonCompetency] = Field(default_factory=list)
    affiliations: list[OrganizationAffiliation] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    patents: list[Patent] = Field(default_factory=list)
    militaryService: list[MilitaryService] = Field(default_factory=list)
    references: list[Referee] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_id(cls, v):
        """Wrap a bare string id into an IdentifierType object.

        HR Open expects ``id`` to be an object with a ``value`` key, e.g.
        ``{"value": "0687-..."}``. If a plain string is supplied we convert it
        so the emitted JSON validates against the schema.
        """
        if isinstance(v, str):
            text = v.strip()
            return {"value": text} if text else None
        return v

    def with_attribution(self) -> dict:
        """Return a dict of this profile with the required HR Open notices.

        The two ``_attribution`` / ``_compliance`` keys satisfy the HR Open
        Standards license requirement that every derivative work carry the
        copyright and compliance notice.
        """
        # ``model_dump`` serializes the Pydantic model to a plain dict.
        # ``exclude_none=True`` keeps the output tidy by dropping empty fields.
        data = self.model_dump(exclude_none=True)
        # Build a NEW dict so the notices appear first, then the profile data.
        return {
            "_attribution": HR_OPEN_ATTRIBUTION,
            "_compliance": HR_OPEN_COMPLIANCE,
            "_specificationVersion": HR_OPEN_VERSION,
            **data,
        }
