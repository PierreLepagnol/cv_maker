#!/usr/bin/env python3
"""
Main CV generation script.
Usage: python scripts/generate_cv.py --config config/academic.json
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from config_loader import load_config, load_data
from latex_escaper import escape_latex
from data_models import Contact
from pydantic import ValidationError
from section_generators import generate_contact_values_section

from unified_generators import (
    generate_unified_activities_section,
    generate_unified_education_section,
    generate_unified_experience_section,
    generate_unified_papers_section,
    generate_unified_skills_section,
    generate_unified_summary_section,
)

# Unified template: one semantic markup, multiple style packages
UNIFIED_SECTION_GENERATORS = {
    "contact_values": generate_contact_values_section,
    # Provide both names; templates typically use resume/summary.tex
    "summary": generate_unified_summary_section,
    "objective": generate_unified_summary_section,
    "skills": generate_unified_skills_section,
    "experience": generate_unified_experience_section,
    "education": generate_unified_education_section,
    "papers": generate_unified_papers_section,
    "activities": generate_unified_activities_section,
}

TOKEN_PATTERN = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")
INPUT_PATTERN = re.compile(r"\\input\s*{([^}]+)}")


def copy_template_files(config, output_dir):
    """
    Copy template files to output directory based on template type.

    Args:
        config: Configuration dict
        output_dir: Output directory path
    """
    template_type = config.get("template", "tlc")
    template_source = Path(config.get("template_source", "templates"))

    if template_type != "unified":
        raise ValueError(
            f"Unsupported template '{template_type}'. This project uses the unified engine only."
        )

    # Copy unified style packages
    for sty_name in ["cv_core.sty", "cv_style_academic.sty", "cv_style_industry.sty"]:
        src = template_source / sty_name
        if not src.exists():
            raise FileNotFoundError(f"Missing unified style file: {src}")
        shutil.copy(src, output_dir / sty_name)

    # Unified templates are self-contained.
    tlc_src = template_source / "TLCresume.sty"
    if not tlc_src.exists():
        raise FileNotFoundError(f"Missing unified dependency: {tlc_src}")
    shutil.copy(tlc_src, output_dir / "TLCresume.sty")

    fonts_src = template_source / "fonts"
    fonts_dst = output_dir / "fonts"
    if fonts_src.exists():
        shutil.copytree(fonts_src, fonts_dst, dirs_exist_ok=True)

    profile_src = template_source / "profile.png"
    if profile_src.exists():
        shutil.copy(profile_src, output_dir / "profile.png")

    # Optional social icons
    hf_svg_src = template_source / "huggingface.svg"
    if hf_svg_src.exists():
        hf_svg_dst = output_dir / "huggingface.svg"
        shutil.copy(hf_svg_src, hf_svg_dst)

        hf_pdf_dst = output_dir / "huggingface.pdf"
        # Regenerate if missing or source changed
        try:
            needs_convert = (
                (not hf_pdf_dst.exists())
                or hf_pdf_dst.stat().st_mtime < hf_svg_dst.stat().st_mtime
            )
        except OSError:
            needs_convert = True

        if needs_convert:
            converted = False
            # Prefer librsvg (fast) then fall back to inkscape
            for cmd in (
                [
                    "rsvg-convert",
                    "-f",
                    "pdf",
                    "-o",
                    str(hf_pdf_dst),
                    str(hf_svg_dst),
                ],
                [
                    "inkscape",
                    str(hf_svg_dst),
                    "--export-type=pdf",
                    f"--export-filename={hf_pdf_dst}",
                ],
            ):
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                except FileNotFoundError:
                    continue

                if result.returncode == 0 and hf_pdf_dst.exists():
                    converted = True
                    break

            if not converted:
                print(
                    "Warning: could not convert huggingface.svg to huggingface.pdf; "
                    "falling back to text icon."
                )


def build_tokens(config, contact_data):
    """Build token replacements for resume templates."""
    contact = Contact.model_validate(contact_data or {})

    full_name_raw = contact.name or "Your Name"
    full_name = escape_latex(full_name_raw)

    firstname_raw = ""
    lastname_raw = ""
    name_parts = str(full_name_raw).rsplit(" ", 1)
    if len(name_parts) == 2:
        firstname_raw, lastname_raw = name_parts
    else:
        firstname_raw, lastname_raw = str(full_name_raw), ""

    portfolio_url = ""
    portfolio_name = ""
    portfolio_homepage = ""
    if contact.portfolio:
        portfolio_url = str(contact.portfolio.url or "")
        portfolio_name = str(contact.portfolio.display_name or "")

    if portfolio_url and not portfolio_name:
        portfolio_name = portfolio_url.replace("https://", "").replace("http://", "")

    # Awesome-CV expects homepage without protocol; it prepends http://
    if portfolio_name:
        portfolio_homepage = portfolio_name
    elif portfolio_url:
        portfolio_homepage = portfolio_url.replace("https://", "").replace(
            "http://", ""
        )

    huggingface_url = ""
    huggingface_handle = ""
    huggingface_label = ""
    if contact.huggingface:
        hf = str(contact.huggingface).strip()
        if hf.startswith("http://") or hf.startswith("https://"):
            huggingface_url = hf
        else:
            huggingface_handle = hf
            huggingface_url = f"https://huggingface.co/{huggingface_handle}"

        # Display label (no protocol)
        if huggingface_url:
            huggingface_label = huggingface_url.replace("https://", "").replace(
                "http://", ""
            )

    tokens = {
        # Shared per-field contact tokens (used by contact_values generator)
        "CONTACT_FULL_NAME": full_name,
        "CONTACT_FIRSTNAME": escape_latex(firstname_raw),
        "CONTACT_LASTNAME": escape_latex(lastname_raw),
        "CONTACT_ROLE": escape_latex(contact.role),
        "CONTACT_QUOTE": escape_latex(contact.quote),
        "CONTACT_PHONE": escape_latex(contact.phone),
        "CONTACT_CITY": escape_latex(contact.city),
        "CONTACT_EMAIL": str(contact.email),
        "CONTACT_GITHUB": str(contact.github),
        "CONTACT_LINKEDIN": str(contact.linkedin),
        "CONTACT_HUGGINGFACE_URL": huggingface_url,
        "CONTACT_HUGGINGFACE_HANDLE": escape_latex(huggingface_handle),
        "CONTACT_HUGGINGFACE_LABEL": escape_latex(huggingface_label),
        "CONTACT_PORTFOLIO_URL": portfolio_url,
        "CONTACT_PORTFOLIO_NAME": escape_latex(portfolio_name),
        "CONTACT_PORTFOLIO_HOMEPAGE": escape_latex(portfolio_homepage),
        # Existing footer token
        "FOOTER_CENTER": f"{full_name}~~~·~~~Résumé",
    }

    # Optional per-section spacing controls (LaTeX lengths).
    # Consumed by unified resume templates via:
    #   \cvsection[{{SECTION_CVENTRYSEP_EXPERIENCE}}]{Professional Experience}
    section_entry_seps = config.get("section_entry_seps", {}) or {}
    if not isinstance(section_entry_seps, dict):
        raise ValueError("config.section_entry_seps must be an object/dict")

    # Optional per-section bullet spacing controls for \cvitems (LaTeX lengths).
    # Consumed by unified resume templates via:
    #   \cvsectionitemssep{ {{SECTION_CVITEMSSEP_EXPERIENCE}} }
    section_item_seps = config.get("section_item_seps", {}) or {}
    if not isinstance(section_item_seps, dict):
        raise ValueError("config.section_item_seps must be an object/dict")

    # Optional bullet spacing override for education *details* lists
    # (\begin{cvedudetailslist} ...). If unset/blank, details lists inherit the
    # current \cvitems spacing (i.e. section_item_seps.education).
    education_details_item_sep = config.get("education_details_item_sep", None)

    known_sections = [
        "summary",
        "objective",
        "skills",
        "experience",
        "education",
        "papers",
        "activities",
    ]
    for section_name in known_sections:
        token_key = f"SECTION_CVENTRYSEP_{section_name.upper()}"
        tokens[token_key] = ""

        token_key = f"SECTION_CVITEMSSEP_{section_name.upper()}"
        tokens[token_key] = ""

    # Education details list spacing token (used by unified templates)
    tokens["SECTION_CVEDUDETAILSSEP_EDUCATION"] = ""

    for section_name, length_value in section_entry_seps.items():
        if length_value is None:
            continue
        token_key = f"SECTION_CVENTRYSEP_{str(section_name).upper()}"
        tokens[token_key] = str(length_value)

    for section_name, length_value in section_item_seps.items():
        if length_value is None:
            continue
        token_key = f"SECTION_CVITEMSSEP_{str(section_name).upper()}"
        tokens[token_key] = str(length_value)

    if education_details_item_sep is not None:
        tokens["SECTION_CVEDUDETAILSSEP_EDUCATION"] = str(education_details_item_sep)

    extra_tokens = config.get("tokens", {})
    for key, value in extra_tokens.items():
        tokens[str(key)] = str(value)

    return tokens


def render_tokens(content, tokens, source_label):
    """Replace token placeholders in template content."""
    missing = set()

    def replace(match):
        key = match.group(1)
        if key not in tokens:
            missing.add(key)
            return match.group(0)
        return tokens[key]

    rendered = TOKEN_PATTERN.sub(replace, content)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Unknown template token(s) in {source_label}: {missing_list}")

    return rendered


def render_template_file(template_path, output_path, tokens):
    """Render a template file with token replacements."""
    content = template_path.read_text(encoding="utf-8")
    rendered = render_tokens(content, tokens, str(template_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")


def extract_input_paths(tex_content):
    """Extract LaTeX \\input paths from content."""
    return INPUT_PATTERN.findall(tex_content)


def normalize_input_path(input_value):
    """Normalize LaTeX \\input paths to .tex files."""
    input_path = Path(input_value)
    if input_path.suffix == "":
        input_path = input_path.with_suffix(".tex")
    return input_path


def get_section_generator(section_name, template_type):
    if template_type == "unified":
        return UNIFIED_SECTION_GENERATORS.get(section_name)
    return None


def process_inputs(
    tex_path, template_source, output_dir, template_type, data, tokens, processed
):
    """Generate or copy all files referenced by \\input statements."""
    content = tex_path.read_text(encoding="utf-8")
    for input_value in extract_input_paths(content):
        normalized = normalize_input_path(input_value)
        output_path = (output_dir / normalized).resolve()

        if output_path in processed:
            continue
        processed.add(output_path)

        generator = get_section_generator(normalized.stem, template_type)
        if generator:
            section_data = data.get(normalized.stem, {})
            generated = generator(section_data)
            rendered = render_tokens(generated, tokens, f"generated:{normalized}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")
        else:
            source_path = template_source / normalized
            if not source_path.exists():
                print(f"Warning: missing template file {source_path}")
                continue
            render_template_file(source_path, output_path, tokens)

        process_inputs(
            output_path,
            template_source,
            output_dir,
            template_type,
            data,
            tokens,
            processed,
        )


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX CV from JSON data")
    parser.add_argument("--config", required=True, help="Path to config JSON file")
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)

        # Load all data files
        data = load_data(base_dir="data")

        # Create output directory
        output_dir = Path(config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy template files to output directory
        copy_template_files(config, output_dir)

        # Render main resume.tex from template
        template_type = config.get("template", "tlc")
        template_source = Path(config.get("template_source", "templates"))
        main_template_name = config.get("main_template", "resume.tex")
        main_template_path = template_source / main_template_name

        if not main_template_path.exists():
            raise FileNotFoundError(f"Missing main template: {main_template_path}")

        tokens = build_tokens(config, data["contact"])
        output_resume = output_dir / "resume.tex"
        render_template_file(main_template_path, output_resume, tokens)

        processed = {output_resume.resolve()}
        process_inputs(
            output_resume,
            template_source,
            output_dir,
            template_type,
            data,
            tokens,
            processed,
        )

        print(f"✓ Generated CV files in {output_dir}")
        compile_cmd = "latexmk -xelatex"
        print(f"  To compile: cd {output_dir} && {compile_cmd} resume.tex")
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
