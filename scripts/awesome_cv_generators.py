"""
Awesome-CV specific LaTeX generation functions.
Each function takes JSON data and returns LaTeX string for Awesome-CV template.
"""

from latex_escaper import escape_latex

def generate_awesome_contact_macros(contact_data):
    """
    Generate contact information commands for Awesome-CV.

    Args:
        contact_data: Dict with contact info

    Returns:
        String with LaTeX contact commands
    """
    # Split name into first and last
    full_name = contact_data.get('name', 'Your Name')
    name_parts = full_name.rsplit(' ', 1)
    if len(name_parts) == 2:
        firstname, lastname = name_parts
    else:
        firstname, lastname = full_name, ''

    lines = []

    # Name (required)
    lines.append(f"\\name{{{escape_latex(firstname)}}}{{{escape_latex(lastname)}}}")

    # Position/role
    if contact_data.get('role'):
        lines.append(f"\\position{{{escape_latex(contact_data['role'])}}}")

    # Address/city
    if contact_data.get('city'):
        lines.append(f"\\address{{{escape_latex(contact_data['city'])}}}")

    # Contact info
    if contact_data.get('phone'):
        lines.append(f"\\mobile{{{contact_data['phone']}}}")

    if contact_data.get('email'):
        lines.append(f"\\email{{{contact_data['email']}}}")

    if contact_data.get('github'):
        lines.append(f"\\github{{{contact_data['github']}}}")

    if contact_data.get('linkedin'):
        lines.append(f"\\linkedin{{{contact_data['linkedin']}}}")

    # Portfolio/homepage
    if contact_data.get('portfolio') and contact_data['portfolio'].get('url'):
        # Extract domain from URL for display
        url = contact_data['portfolio']['url']
        display_name = contact_data['portfolio'].get('display_name', url.replace('https://', '').replace('http://', ''))
        lines.append(f"\\homepage{{{display_name}}}")

    return '\n'.join(lines)

def generate_awesome_skills_section(skills_data):
    """
    Generate skills section for Awesome-CV.

    Uses cvskills environment with skill type and items.

    Args:
        skills_data: Dict with 'skills' list

    Returns:
        String with LaTeX skills section
    """
    lines = [
        "%-------------------------------------------------------------------------------",
        "%\tSECTION TITLE",
        "%-------------------------------------------------------------------------------",
        "\\cvsection{Technical Skills}",
        "",
        "",
        "%-------------------------------------------------------------------------------",
        "%\tCONTENT",
        "%-------------------------------------------------------------------------------",
        "\\begin{cvskills}",
        "",
        "%---------------------------------------------------------"
    ]

    for skill in skills_data.get('skills', []):
        category = escape_latex(skill['category'])
        items = escape_latex(skill['items'])
        lines.append(f"  \\cvskill")
        lines.append(f"    {{{category}}} % Category")
        lines.append(f"    {{{items}}} % Skills")
        lines.append("")

    lines.append("%---------------------------------------------------------")
    lines.append("\\end{cvskills}")

    return '\n'.join(lines)

def generate_awesome_experience_section(experience_data):
    """
    Generate experience entries for Awesome-CV.

    Uses cventries environment with cventry commands.

    Args:
        experience_data: Dict with 'experiences' list

    Returns:
        String with LaTeX experience entries
    """
    lines = [
        "%-------------------------------------------------------------------------------",
        "%\tSECTION TITLE",
        "%-------------------------------------------------------------------------------",
        "\\cvsection{Professional Experience}",
        "",
        "",
        "%-------------------------------------------------------------------------------",
        "%\tCONTENT",
        "%-------------------------------------------------------------------------------",
        "\\begin{cventries}",
        ""
    ]

    for exp in experience_data.get('experiences', []):
        title = escape_latex(exp['title'])
        company = escape_latex(exp['company'])
        location = escape_latex(exp['location'])
        date_range = f"{exp['start_date']} - {exp['end_date']}"

        lines.append("%---------------------------------------------------------")
        lines.append("  \\cventry")
        lines.append(f"    {{{title}}} % Job title")
        lines.append(f"    {{{company}}} % Organization")
        lines.append(f"    {{{location}}} % Location")
        lines.append(f"    {{{date_range}}} % Date(s)")
        lines.append("    {")
        lines.append("      \\begin{cvitems} % Description(s) of tasks/responsibilities")

        for bullet in exp['bullets']:
            lines.append(f"        \\item {{{escape_latex(bullet)}}}")

        lines.append("      \\end{cvitems}")
        lines.append("    }")
        lines.append("")

    lines.append("%---------------------------------------------------------")
    lines.append("\\end{cventries}")

    return '\n'.join(lines)

def generate_awesome_education_section(education_data):
    """
    Generate education section for Awesome-CV.

    Args:
        education_data: Dict with 'degrees' and 'awards' lists

    Returns:
        String with LaTeX education entries
    """
    lines = [
        "%-------------------------------------------------------------------------------",
        "%\tSECTION TITLE",
        "%-------------------------------------------------------------------------------",
        "\\cvsection{Education}",
        "",
        "",
        "%-------------------------------------------------------------------------------",
        "%\tCONTENT",
        "%-------------------------------------------------------------------------------",
        "\\begin{cventries}",
        ""
    ]

    # Degrees
    for degree in education_data.get('degrees', []):
        degree_name = escape_latex(degree['degree'])
        institution = escape_latex(degree['institution'])
        location = escape_latex(degree.get('location', ''))
        date = degree['date']

        lines.append("%---------------------------------------------------------")
        lines.append("  \\cventry")
        lines.append(f"    {{{degree_name}}} % Degree")
        lines.append(f"    {{{institution}}} % Institution")
        lines.append(f"    {{{location}}} % Location")
        lines.append(f"    {{{date}}} % Date(s)")
        lines.append("    {")

        # Include details or awards as bullet points
        items = []
        if degree.get('details'):
            items.append(escape_latex(degree['details']))

        if items:
            lines.append("      \\begin{cvitems} % Description(s) bullet points")
            for item in items:
                lines.append(f"        \\item {{{item}}}")
            lines.append("      \\end{cvitems}")

        lines.append("    }")
        lines.append("")

    # Awards as additional entries
    for award in education_data.get('awards', []):
        title = escape_latex(award['title'])
        org = escape_latex(award['organization'])
        date = award['date']

        lines.append("%---------------------------------------------------------")
        lines.append("  \\cventry")
        lines.append(f"    {{{title}}} % Award")
        lines.append(f"    {{{org}}} % Organization")
        lines.append("    {} % Location")
        lines.append(f"    {{{date}}} % Date(s)")
        lines.append("    {}")
        lines.append("")

    lines.append("%---------------------------------------------------------")
    lines.append("\\end{cventries}")

    return '\n'.join(lines)

def generate_awesome_papers_section(papers_data):
    """
    Generate publications section for Awesome-CV.

    Uses cvhonors environment for publication list.

    Args:
        papers_data: Dict with 'papers' list

    Returns:
        String with LaTeX paper citations
    """
    lines = [
        "%-------------------------------------------------------------------------------",
        "%\tSECTION TITLE",
        "%-------------------------------------------------------------------------------",
        "\\cvsection{Publications}",
        "",
        "",
        "%-------------------------------------------------------------------------------",
        "%\tCONTENT",
        "%-------------------------------------------------------------------------------",
        "\\begin{cvhonors}",
        ""
    ]

    for paper in papers_data.get('papers', []):
        title = escape_latex(paper['title'])
        venue = escape_latex(paper['venue'])
        year = str(paper['year'])
        status = paper.get('status', 'published').capitalize()

        # Format: title, venue, status, year
        lines.append("%---------------------------------------------------------")
        lines.append(f"  \\cvhonor")
        lines.append(f"    {{{title}}} % Title")
        lines.append(f"    {{{venue}}} % Event/Venue")
        lines.append(f"    {{}} % Location (empty for papers)")
        lines.append(f"    {{{year} ({status})}} % Date(s)")
        lines.append("")

    lines.append("%---------------------------------------------------------")
    lines.append("\\end{cvhonors}")

    return '\n'.join(lines)

def generate_awesome_activities_section(activities_data):
    """
    Generate activities section for Awesome-CV.

    Uses cvhonors environment.

    Args:
        activities_data: Dict with 'activities' list

    Returns:
        String with LaTeX activity entries
    """
    lines = [
        "%-------------------------------------------------------------------------------",
        "%\tSECTION TITLE",
        "%-------------------------------------------------------------------------------",
        "\\cvsection{Activities}",
        "",
        "",
        "%-------------------------------------------------------------------------------",
        "%\tCONTENT",
        "%-------------------------------------------------------------------------------",
        "\\begin{cvhonors}",
        ""
    ]

    for activity in activities_data.get('activities', []):
        title = escape_latex(activity['title'])
        org = escape_latex(activity.get('organization', ''))
        date = activity['date']

        lines.append("%---------------------------------------------------------")
        lines.append(f"  \\cvhonor")
        lines.append(f"    {{{title}}} % Title")
        lines.append(f"    {{{org}}} % Organization")
        lines.append("    {} % Location")
        lines.append(f"    {{{date}}} % Date")
        lines.append("")

    lines.append("%---------------------------------------------------------")
    lines.append("\\end{cvhonors}")

    return '\n'.join(lines)

def generate_awesome_objective_section(objective_data):
    """
    Generate summary/objective for Awesome-CV.

    Uses cvparagraph environment.

    Args:
        objective_data: Dict with 'text' key

    Returns:
        String with LaTeX objective
    """
    text = escape_latex(objective_data.get('text', ''))

    if not text:
        return ""

    lines = [
        "%-------------------------------------------------------------------------------",
        "%\tSECTION TITLE",
        "%-------------------------------------------------------------------------------",
        "\\cvsection{Summary}",
        "",
        "",
        "%-------------------------------------------------------------------------------",
        "%\tCONTENT",
        "%-------------------------------------------------------------------------------",
        "\\begin{cvparagraph}",
        "",
        "%---------------------------------------------------------",
        text,
        "\\end{cvparagraph}",
        ""
    ]

    return '\n'.join(lines)
