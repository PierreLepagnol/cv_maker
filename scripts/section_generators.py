"""
Section-specific LaTeX generation functions.
Each function takes JSON data and returns LaTeX string.
"""

from latex_escaper import escape_latex

def generate_contact_macros(contact_data):
    """
    Generate \\def macros for contact information.

    Args:
        contact_data: Dict with contact info

    Returns:
        String with LaTeX \\def commands
    """
    lines = [
        f"\\def\\name{{{escape_latex(contact_data.get('name', 'Your Name'))}}}",
        f"\\def\\phone{{{escape_latex(contact_data.get('phone', ''))}}}",
        f"\\def\\city{{{escape_latex(contact_data.get('city', ''))}}}",
        f"\\def\\email{{{contact_data.get('email', '')}}}",  # Don't escape email (escaper handles this)
        f"\\def\\LinkedIn{{{contact_data.get('linkedin', '')}}}",
        f"\\def\\github{{{contact_data.get('github', '')}}}",
        f"\\def\\role{{{escape_latex(contact_data.get('role', ''))}}}",
    ]

    # Handle optional portfolio
    if contact_data.get('portfolio'):
        lines.append(f"\\def\\portfoliourl{{{contact_data['portfolio']['url']}}}")
        lines.append(f"\\def\\portfolioname{{{escape_latex(contact_data['portfolio']['display_name'])}}}")
    else:
        lines.append("\\def\\portfoliourl{}")
        lines.append("\\def\\portfolioname{}")

    return '\n'.join(lines)

def generate_skills_section(skills_data):
    """
    Generate tabular skills section.

    Args:
        skills_data: Dict with 'skills' list

    Returns:
        String with LaTeX tabular
    """
    lines = ["\\begin{tabular}{p{11em} p{1em} p{43em}}"]

    for skill in skills_data.get('skills', []):
        category = escape_latex(skill['category'])
        items = escape_latex(skill['items'])
        lines.append(f"\\skills{{{category}}} & & {items} \\\\")

    lines.append("\\end{tabular}")
    return '\n'.join(lines)

def generate_experience_section(experience_data):
    """
    Generate experience entries with subsections.

    Args:
        experience_data: Dict with 'experiences' list

    Returns:
        String with LaTeX experience entries
    """
    lines = []

    for exp in experience_data.get('experiences', []):
        title = escape_latex(exp['title'])
        company = escape_latex(exp['company'])
        location = escape_latex(exp['location'])
        date_range = f"{exp['start_date']} --- {exp['end_date']}"

        lines.append(f"\\subsection{{{{{title} \\hfill {date_range}}}}}")
        lines.append(f"\\subtext{{{company} \\hfill {location}}}")
        lines.append("\\begin{zitemize}")

        for bullet in exp['bullets']:
            lines.append(f"    \\item {escape_latex(bullet)}")

        lines.append("\\end{zitemize}")
        lines.append("")  # Blank line between experiences

    return '\n'.join(lines)

def generate_education_section(education_data):
    """
    Generate education section with degrees and awards.

    Args:
        education_data: Dict with 'degrees' and 'awards' lists

    Returns:
        String with LaTeX education entries
    """
    lines = []

    # Degrees
    for degree in education_data.get('degrees', []):
        degree_name = escape_latex(degree['degree'])
        institution = escape_latex(degree['institution'])
        date = degree['date']

        lines.append(f"\\skills{{{degree_name}}}, \\textit{{{institution}}} \\hfill {date}")

        if degree.get('details'):
            lines.append(f"\\textit{{{escape_latex(degree['details'])}}}")

        lines.append("")

    # Awards
    for award in education_data.get('awards', []):
        title = escape_latex(award['title'])
        org = escape_latex(award['organization'])
        date = award['date']
        lines.append(f"\\textit{{{title}, {org}}} \\hfill {date}")
        lines.append("")

    return '\n'.join(lines)

def generate_papers_section(papers_data):
    """
    Generate publications section.

    Args:
        papers_data: Dict with 'papers' list

    Returns:
        String with LaTeX paper citations
    """
    lines = []

    for paper in papers_data.get('papers', []):
        authors = escape_latex(paper['authors'])
        title = escape_latex(paper['title'])
        venue = escape_latex(paper['venue'])
        year = paper['year']
        status = paper.get('status', 'published')

        # Format: Authors. "Title". Venue Year. (Status if not published)
        line = f"{authors}. \\textit{{\"{title}\"}}. {venue} {year}."

        if status != 'published':
            line += f" ({status.capitalize()})"

        if paper.get('url'):
            line += f" \\href{{{paper['url']}}}{{[Link]}}"

        lines.append(line)
        lines.append("")

    return '\n'.join(lines)

def generate_activities_section(activities_data):
    """
    Generate activities section.

    Args:
        activities_data: Dict with 'activities' list

    Returns:
        String with LaTeX activity entries
    """
    lines = []

    for activity in activities_data.get('activities', []):
        title = escape_latex(activity['title'])
        date = activity['date']
        lines.append(f"{title} \\hfill {date}")
        lines.append("")

    return '\n'.join(lines)

def generate_objective_section(objective_data):
    """
    Generate objective statement.

    Args:
        objective_data: Dict with 'text' key

    Returns:
        String with escaped objective text
    """
    text = escape_latex(objective_data.get('text', ''))
    return text
