#!/usr/bin/env python3
"""
Main CV generation script.
Usage: python scripts/generate_cv.py --config config/academic.json
"""

import argparse
import re
import shutil
import sys
from pathlib import Path
from config_loader import load_config, load_data
from latex_escaper import escape_latex
from section_generators import (
    generate_contact_macros,
    generate_skills_section,
    generate_experience_section,
    generate_education_section,
    generate_papers_section,
    generate_activities_section,
    generate_objective_section
)
from awesome_cv_generators import (
    generate_awesome_contact_macros,
    generate_awesome_skills_section,
    generate_awesome_experience_section,
    generate_awesome_education_section,
    generate_awesome_papers_section,
    generate_awesome_activities_section,
    generate_awesome_objective_section
)

# Map section names to generator functions for TLC template
TLC_SECTION_GENERATORS = {
    'objective': generate_objective_section,
    'skills': generate_skills_section,
    'experience': generate_experience_section,
    'education': generate_education_section,
    'papers': generate_papers_section,
    'activities': generate_activities_section
}

# Map section names to generator functions for Awesome-CV template
AWESOME_SECTION_GENERATORS = {
    'objective': generate_awesome_objective_section,
    'skills': generate_awesome_skills_section,
    'experience': generate_awesome_experience_section,
    'education': generate_awesome_education_section,
    'papers': generate_awesome_papers_section,
    'activities': generate_awesome_activities_section
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
    template_type = config.get('template', 'tlc')
    template_source = Path(config.get('template_source', 'templates'))

    if template_type == 'tlc':
        # Copy TLC template files
        shutil.copy(template_source / 'TLCresume.sty', output_dir / 'TLCresume.sty')
        shutil.copy(template_source / '_header.tex', output_dir / '_header.tex')
    elif template_type == 'awesome-cv':
        # Copy Awesome-CV class and fonts
        shutil.copy(template_source / 'awesome-cv.cls', output_dir / 'awesome-cv.cls')
        # Copy fonts directory
        fonts_src = template_source / 'fonts'
        fonts_dst = output_dir / 'fonts'
        if fonts_src.exists():
            shutil.copytree(fonts_src, fonts_dst, dirs_exist_ok=True)

def build_tokens(config, contact_data, template_type):
    """Build token replacements for resume templates."""
    if template_type == 'awesome-cv':
        contact_macros = generate_awesome_contact_macros(contact_data)
    else:
        contact_macros = generate_contact_macros(contact_data)

    name = escape_latex(contact_data.get('name', 'Your Name'))
    tokens = {
        'CONTACT_MACROS': contact_macros,
        'FOOTER_CENTER': f"{name}~~~·~~~Résumé"
    }

    extra_tokens = config.get('tokens', {})
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
    content = template_path.read_text(encoding='utf-8')
    rendered = render_tokens(content, tokens, str(template_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding='utf-8')

def extract_input_paths(tex_content):
    """Extract LaTeX \\input paths from content."""
    return INPUT_PATTERN.findall(tex_content)

def normalize_input_path(input_value):
    """Normalize LaTeX \\input paths to .tex files."""
    input_path = Path(input_value)
    if input_path.suffix == '':
        input_path = input_path.with_suffix('.tex')
    return input_path

def get_section_generator(section_name, template_type):
    if template_type == 'awesome-cv':
        return AWESOME_SECTION_GENERATORS.get(section_name)
    return TLC_SECTION_GENERATORS.get(section_name)

def process_inputs(tex_path, template_source, output_dir, template_type, data, tokens, processed):
    """Generate or copy all files referenced by \\input statements."""
    content = tex_path.read_text(encoding='utf-8')
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
            output_path.write_text(rendered, encoding='utf-8')
        else:
            source_path = template_source / normalized
            if not source_path.exists():
                print(f"Warning: missing template file {source_path}")
                continue
            render_template_file(source_path, output_path, tokens)

        process_inputs(output_path, template_source, output_dir, template_type, data, tokens, processed)

def main():
    parser = argparse.ArgumentParser(description='Generate LaTeX CV from JSON data')
    parser.add_argument('--config', required=True, help='Path to config JSON file')
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)

        # Load all data files
        data = load_data(base_dir='data')

        # Create output directory
        output_dir = Path(config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy template files to output directory
        copy_template_files(config, output_dir)

        # Render main resume.tex from template
        template_type = config.get('template', 'tlc')
        template_source = Path(config.get('template_source', 'templates'))
        main_template_name = config.get('main_template', 'resume.tex')
        main_template_path = template_source / main_template_name

        if not main_template_path.exists():
            raise FileNotFoundError(f"Missing main template: {main_template_path}")

        tokens = build_tokens(config, data['contact'], template_type)
        output_resume = output_dir / 'resume.tex'
        render_template_file(main_template_path, output_resume, tokens)

        processed = {output_resume.resolve()}
        process_inputs(
            output_resume,
            template_source,
            output_dir,
            template_type,
            data,
            tokens,
            processed
        )

        print(f"✓ Generated CV files in {output_dir}")
        compile_cmd = "xelatex" if template_type == 'awesome-cv' else "latexmk -pdf"
        print(f"  To compile: cd {output_dir} && {compile_cmd} resume.tex")
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

if __name__ == '__main__':
    main()
