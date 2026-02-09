"""Unified semantic LaTeX generators.

These generators output a single markup format (Awesome-inspired semantic macros)
which is later styled by a template-selected style package.
"""

from latex_escaper import escape_latex


def generate_unified_summary_section(summary_data):
    """Generate a summary/objective paragraph."""
    text = escape_latex(summary_data.get("text", ""))
    if not text:
        return ""

    lines = [
        "\\begin{cvparagraph}",
        text,
        "\\end{cvparagraph}",
        "",
    ]
    return "\n".join(lines)


def generate_unified_skills_section(skills_data):
    """Generate skills as cvskills/cvskill rows."""
    skills = skills_data.get("skills", [])
    if not skills:
        return ""

    lines = ["\\begin{cvskills}", ""]
    for skill in skills:
        category = escape_latex(skill.get("category", ""))
        items = escape_latex(skill.get("items", ""))
        if not category and not items:
            continue
        lines.append(f"  \\cvskill{{{category}}}{{{items}}}")
    lines.extend(["", "\\end{cvskills}", ""])
    return "\n".join(lines)


def generate_unified_experience_section(experience_data):
    """Generate experience as cventries/cventry blocks."""
    experiences = experience_data.get("experiences", [])
    if not experiences:
        return ""

    lines = ["\\begin{cventries}", ""]

    for exp in experiences:
        title = escape_latex(exp.get("title", ""))
        company = escape_latex(exp.get("company", ""))
        location = escape_latex(exp.get("location", ""))
        start_date = str(exp.get("start_date", "")).strip()
        end_date = str(exp.get("end_date", "")).strip()
        date_range = " - ".join([d for d in [start_date, end_date] if d])

        lines.append("  \\cventry")
        lines.append(f"    {{{title}}}{{{company}}}{{{location}}}{{{date_range}}}{{")

        bullets = exp.get("bullets", []) or []
        if bullets:
            lines.append("      \\begin{cvitems}")
            for bullet in bullets:
                lines.append(f"        \\item {{{escape_latex(bullet)}}}")
            lines.append("      \\end{cvitems}")

        lines.append("    }")
        lines.append("")

    lines.extend(["\\end{cventries}", ""])
    return "\n".join(lines)


def generate_unified_education_section(education_data):
    """Generate education entries using semantic education macros.

    We keep education as its own semantic construct so styles can render it
    differently from work experience while keeping a single markup format.
    """
    degrees = education_data.get("degrees", []) or []
    awards = education_data.get("awards", []) or []
    if not degrees and not awards:
        return ""

    lines = []

    for degree in degrees:
        degree_name = escape_latex(degree.get("degree", ""))
        institution = escape_latex(degree.get("institution", ""))
        location = escape_latex(degree.get("location", ""))
        date = str(degree.get("date", "")).strip()
        details = escape_latex(degree.get("details", ""))

        lines.append(
            f"\\cveduentry{{{degree_name}}}{{{institution}}}{{{location}}}{{{date}}}{{{details}}}"
        )
        lines.append("")

    for award in awards:
        title = escape_latex(award.get("title", ""))
        org = escape_latex(award.get("organization", ""))
        date = str(award.get("date", "")).strip()

        lines.append(f"\\cvaward{{{title}}}{{{org}}}{{{date}}}")
        lines.append("")

    return "\n".join(lines)


def generate_unified_papers_section(papers_data):
    """Generate publications as plain lines (academic-friendly)."""
    papers = papers_data.get("papers", []) or []
    if not papers:
        return ""

    lines = []
    for paper in papers:
        authors = escape_latex(paper.get("authors", ""))
        title = escape_latex(paper.get("title", ""))
        venue = escape_latex(paper.get("venue", ""))
        year = str(paper.get("year", "")).strip()
        status = str(paper.get("status", "published") or "published")

        line = f'{authors}. \\textit{{"{title}"}}. {venue} {year}.'
        if status and status != "published":
            line += f" ({escape_latex(status).capitalize()})"
        url = paper.get("url")
        if url:
            line += f" \\href{{{url}}}{{[Link]}}"

        lines.append(line)
        lines.append("")

    return "\n".join(lines)


def generate_unified_activities_section(activities_data):
    """Generate activities as one-line entries."""
    activities = activities_data.get("activities", []) or []
    if not activities:
        return ""

    lines = []
    for activity in activities:
        title = escape_latex(activity.get("title", ""))
        date = str(activity.get("date", "")).strip()
        if not title and not date:
            continue
        lines.append(f"{title} \\hfill {date}")
        lines.append("")
    return "\n".join(lines)
