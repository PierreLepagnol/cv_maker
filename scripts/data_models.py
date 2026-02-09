"""Pydantic data models for JSON inputs.

These models validate + normalize the JSON structures found in `data/*.json`.
They intentionally accept extra keys (ignored) so the schema can evolve.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _coerce_str(value):
    if value is None:
        return ""
    return str(value).strip()


def _coerce_str_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    item = str(value).strip()
    return [item] if item else []


class ContactPortfolio(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: str = ""
    display_name: str = ""

    @field_validator("url", "display_name", mode="before")
    @classmethod
    def _coerce_str(cls, value):
        return _coerce_str(value)


class Contact(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = ""
    role: str = ""
    quote: str = ""
    phone: str = ""
    city: str = ""
    email: str = ""
    linkedin: str = ""
    github: str = ""
    huggingface: str = ""
    portfolio: ContactPortfolio | None = None

    @field_validator(
        "name",
        "role",
        "quote",
        "phone",
        "city",
        "email",
        "linkedin",
        "github",
        "huggingface",
        mode="before",
    )
    @classmethod
    def _coerce_str(cls, value):
        return _coerce_str(value)


class TextSection(BaseModel):
    """Generic {"text": "..."} payload (summary/objective)."""

    model_config = ConfigDict(extra="ignore")

    text: str = ""

    @field_validator("text", mode="before")
    @classmethod
    def _coerce_text(cls, value):
        return _coerce_str(value)


class Skill(BaseModel):
    model_config = ConfigDict(extra="ignore")

    category: str = ""
    items: str = ""

    @field_validator("category", "items", mode="before")
    @classmethod
    def _coerce_skill_fields(cls, value):
        return _coerce_str(value)


class SkillsData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    skills: list[Skill] = Field(default_factory=list)


class Experience(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = Field(default_factory=list)

    @field_validator("title", "company", "location", "start_date", "end_date", mode="before")
    @classmethod
    def _coerce_experience_fields(cls, value):
        return _coerce_str(value)

    @field_validator("bullets", mode="before")
    @classmethod
    def _coerce_bullets(cls, value):
        return _coerce_str_list(value)


class ExperienceData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    experiences: list[Experience] = Field(default_factory=list)


class Degree(BaseModel):
    model_config = ConfigDict(extra="ignore")

    degree: str = ""
    institution: str = ""
    location: str = ""
    date: str = ""
    # Either a single string paragraph or a list of bullet-ish lines.
    details: str | list[str] = ""

    @field_validator("degree", "institution", "location", "date", mode="before")
    @classmethod
    def _coerce_degree_fields(cls, value):
        return _coerce_str(value)

    @field_validator("details", mode="before")
    @classmethod
    def _coerce_details(cls, value):
        if value is None or value == "":
            return ""
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        return _coerce_str(value)


class Award(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    organization: str = ""
    date: str = ""

    @field_validator("title", "organization", "date", mode="before")
    @classmethod
    def _coerce_award_fields(cls, value):
        return _coerce_str(value)


class EducationData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    degrees: list[Degree] = Field(default_factory=list)
    awards: list[Award] = Field(default_factory=list)


class Paper(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    authors: str = ""
    venue: str = ""
    year: str = ""
    status: str = "published"
    volume: str = ""
    url: str = ""
    bullets: list[str] = Field(default_factory=list)

    @field_validator(
        "title",
        "authors",
        "venue",
        "year",
        "status",
        "volume",
        "url",
        mode="before",
    )
    @classmethod
    def _coerce_paper_fields(cls, value):
        return _coerce_str(value)

    @field_validator("bullets", mode="before")
    @classmethod
    def _coerce_paper_bullets(cls, value):
        return _coerce_str_list(value)


class PapersData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    papers: list[Paper] = Field(default_factory=list)


class Activity(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    date: str = ""

    @field_validator("title", "date", mode="before")
    @classmethod
    def _coerce_activity_fields(cls, value):
        return _coerce_str(value)


class ActivitiesData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    activities: list[Activity] = Field(default_factory=list)
