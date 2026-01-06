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

from pydantic import BaseModel, ConfigDict, Field

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
        default=None, description="employee, contractor, temporary, etc."
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
    unitCode: str | None = Field(default=None, description="e.g. 'year', 'month'.")


class PersonCompetency(HROpenBase):
    """HR Open ``PersonCompetencyType`` — a skill/competency assertion."""

    competencyName: str | None = Field(default=None, description="The skill name.")
    description: str | None = None
    proficiencyLevel: str | None = Field(default=None, description="e.g. beginner, expert.")
    lastUsedDate: str | None = None
    experienceMeasure: ExperienceMeasure | None = None


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

    id: str | None = None
    url: str | None = None
    descriptions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level PersonProfileType — the full resume object
# ---------------------------------------------------------------------------
class PersonProfile(HROpenBase):
    """HR Open ``PersonProfileType`` — the complete structured resume.

    This is what the AI mapping service produces and what we store, serve, and
    export as JSON/XML. Every section is optional so partial resumes validate.
    """

    id: str | None = Field(default=None, description="Stable identifier for this profile.")
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
