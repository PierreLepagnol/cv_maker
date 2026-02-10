"""Unified semantic LaTeX generators.

These generators output a single markup format (semantic macros)
which is later styled by a template-selected style package.

Implementation uses small renderer objects (Strategy) on top of a LaTeX builder
(Builder) plus shared list-section skeletons (Template Method).
"""

from __future__ import annotations

from latex_escaper import escape_latex

from latex_rendering import (
    CompositeRenderer,
    LatexBuilder,
    ListSectionRenderer,
    fmt_date_range,
    latex_href,
)
from data_models import (
    ActivitiesData,
    Activity,
    EducationData,
    Degree,
    ExperienceData,
    Experience,
    Paper,
    PapersData,
    Skill,
    SkillsData,
    TextSection,
)


class SummaryRenderer:
    def render(self, data: TextSection):
        text = escape_latex(data.text)
        if not text:
            return ""

        b = LatexBuilder()
        with b.env("cvparagraph", blank_after_begin=False):
            b.line(text)
        return b.render()


class SkillsRenderer(ListSectionRenderer):
    key = "skills"
    outer_env = "cvskills"
    item_blank_line = False

    def render_item(self, b: LatexBuilder, item: Skill):
        category = escape_latex(item.category)
        items = escape_latex(item.items)
        if not category and not items:
            return False
        b.command("cvskill", category, items)
        return True


class ExperienceRenderer(ListSectionRenderer):
    key = "experiences"
    outer_env = "cventries"

    def render_item(self, b: LatexBuilder, exp: Experience):
        title = escape_latex(exp.title)
        company = escape_latex(exp.company)
        location = escape_latex(exp.location)
        date_range = fmt_date_range(exp.start_date, exp.end_date)

        bullets = exp.bullets

        if not any([title, company, location, date_range, bullets]):
            return False

        with b.command_body("cventry", title, company, location, date_range):
            if bullets:
                with b.env(
                    "cvitems",
                    blank_after_begin=False,
                    blank_before_end=False,
                    blank_after_end=False,
                ):
                    for bullet in bullets:
                        bullet_tex = escape_latex(bullet)
                        if not bullet_tex:
                            continue
                        b.line(f"\\item {{{bullet_tex}}}")
        return True


class DegreesRenderer(ListSectionRenderer):
    key = "degrees"

    def render_item(self, b: LatexBuilder, degree: Degree):
        degree_name = escape_latex(degree.degree)
        institution = escape_latex(degree.institution)
        location = escape_latex(degree.location)
        date = str(degree.date or "").strip()

        details = degree.details

        if not any([degree_name, institution, location, date, details]):
            return False

        with b.command_body("cveduentry", degree_name, institution, location, date):
            if isinstance(details, list):
                items = [escape_latex(str(d)) for d in details if str(d).strip()]
                if items:
                    with b.env(
                        "cvedudetailslist",
                        blank_after_begin=False,
                        blank_before_end=False,
                        blank_after_end=False,
                    ):
                        for d in items:
                            b.command("cvedudetail", d)
            else:
                details_text = escape_latex(str(details))
                if details_text.strip():
                    b.command("cvedudetails", details_text)
        return True



class PapersRenderer(ListSectionRenderer):
    key = "papers"
    outer_env = "cventries"

    def render_item(self, b: LatexBuilder, paper: Paper):
        title_text = escape_latex(paper.title)
        authors = escape_latex(paper.authors)
        venue = escape_latex(paper.venue)
        year = str(paper.year or "").strip()
        status = str(paper.status or "published").strip()

        date = year
        if status and status != "published":
            status_label = escape_latex(status).capitalize()
            date = f"{date} ({status_label})" if date else status_label

        url = str(paper.url or "").strip()
        title = title_text
        if url and str(paper.title or "").strip():
            title = latex_href(url, paper.title)

        bullets = [escape_latex(bu) for bu in paper.bullets if str(bu).strip()]
        if url and not str(paper.title or "").strip():
            bullets.append(latex_href(url, "[Link]"))

        if not any([title, authors, venue, date, bullets]):
            return False

        with b.command_body("cventry", title, authors, venue, date):
            if bullets:
                with b.env(
                    "cvitems",
                    blank_after_begin=False,
                    blank_before_end=False,
                    blank_after_end=False,
                ):
                    for bullet in bullets:
                        if not bullet:
                            continue
                        b.line(f"\\item {{{bullet}}}")
        return True


class ActivitiesRenderer(ListSectionRenderer):
    key = "activities"
    outer_env = "cventries"
    item_blank_line = False

    def _split_title(self, raw_title: str):
        """Split a one-line project string into (title, details).

        Supports the existing data convention:
          "Project Name --- One-line details"
        """

        title = str(raw_title or "").strip()
        if not title:
            return "", ""

        if " --- " in title:
            left, right = title.split(" --- ", 1)
            return left.strip(), right.strip()

        return title, ""

    def render_item(self, b: LatexBuilder, activity: Activity):
        raw_title, raw_details = self._split_title(activity.title)
        title = escape_latex(raw_title)
        details = escape_latex(raw_details)
        date = str(activity.date or "").strip()

        if not title and not date and not details:
            return False

        if details:
            with b.command_body("cventry", title, "", "", date):
                with b.env(
                    "cvitems",
                    blank_after_begin=False,
                    blank_before_end=False,
                    blank_after_end=False,
                ):
                    b.line(f"\\item {{{details}}}")
        else:
            b.command("cventry", title, "", "", date, "")
        return True


EDUCATION_RENDERER = CompositeRenderer(DegreesRenderer())


def generate_unified_summary_section(summary_data):
    """Generate a summary/objective paragraph."""
    section = TextSection.model_validate(summary_data or {})
    return SummaryRenderer().render(section)


def generate_unified_skills_section(skills_data):
    """Generate skills as cvskills/cvskill rows."""
    section = SkillsData.model_validate(skills_data or {})
    return SkillsRenderer().render(section)


def generate_unified_experience_section(experience_data):
    """Generate experience as cventries/cventry blocks."""
    section = ExperienceData.model_validate(experience_data or {})
    return ExperienceRenderer().render(section)


def generate_unified_education_section(education_data):
    """Generate education entries using semantic education macros.

    We keep education as its own semantic construct so styles can render it
    differently from work experience while keeping a single markup format.
    """
    section = EducationData.model_validate(education_data or {})
    return EDUCATION_RENDERER.render(section)


def generate_unified_papers_section(papers_data):
    """Generate publications.

    Publications are rendered using the shared \\cventry macro so they match the
    rest of the unified semantic markup.

    Supported paper fields:
      - title, authors, venue, year, status, volume, url
      - bullets: optional list of extra bullet points
    """
    section = PapersData.model_validate(papers_data or {})
    return PapersRenderer().render(section)


def generate_unified_activities_section(activities_data):
    """Generate activities as one-line entries."""
    section = ActivitiesData.model_validate(activities_data or {})
    return ActivitiesRenderer().render(section)
