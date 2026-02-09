"""
LaTeX character escaping utilities.
Automatically escapes special LaTeX characters so users can write plain text in JSON.
"""

LATEX_SPECIAL_CHARS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

# Backslash must be handled separately to avoid double-escaping
BACKSLASH_ESCAPE = r"\textbackslash{}"


def escape_latex(text):
    """
    Escape special LaTeX characters in text.

    Special handling:
    - URLs are NOT escaped (detected by http:// or https://)
    - Empty/None text returns empty string

    Args:
        text: String to escape

    Returns:
        Escaped string safe for LaTeX
    """
    if not text:
        return ""

    # Convert to string if not already
    text = str(text)

    # Don't escape URLs
    if text.startswith("http://") or text.startswith("https://"):
        return text

    # Don't escape email addresses (simple heuristic)
    if "@" in text and "." in text and " " not in text:
        return text

    # First escape backslashes to avoid double-escaping
    # But only if they're not already part of an escape sequence
    if "\\" in text and not text.startswith("\\"):
        result = text.replace("\\", BACKSLASH_ESCAPE)
    else:
        result = text

    # Escape other special characters
    for char, escaped in LATEX_SPECIAL_CHARS.items():
        result = result.replace(char, escaped)

    return result


def escape_dict(data):
    """
    Recursively escape all strings in a dictionary or list.

    Args:
        data: Dict, list, or primitive value

    Returns:
        Same structure with all strings escaped
    """
    if isinstance(data, str):
        return escape_latex(data)
    elif isinstance(data, dict):
        return {k: escape_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [escape_dict(item) for item in data]
    else:
        return data
