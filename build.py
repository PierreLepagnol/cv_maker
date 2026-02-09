#!/usr/bin/env python3
"""
Single-command build script for CV generation.
Usage:
    python build.py academic    # Build academic CV
    python build.py industry    # Build industry CV
    python build.py all         # Build all variants
"""

import json
import subprocess
import sys
from pathlib import Path

CONFIGS = {
    "academic": "config/academic.json",
    "industry": "config/industry.json",
}


def build_variant(variant_name):
    """
    Build a specific CV variant.

    Args:
        variant_name: Name of variant to build

    Returns:
        bool: True if successful, False otherwise
    """
    if variant_name not in CONFIGS:
        print(f"Error: Unknown variant '{variant_name}'")
        print(f"Available variants: {', '.join(CONFIGS.keys())}")
        return False

    config_path = CONFIGS[variant_name]
    print(f"\n=== Building {variant_name} CV ===")

    # Step 1: Generate .tex files from JSON
    print("Step 1: Generating LaTeX files from JSON...")
    result = subprocess.run(
        ["python3", "scripts/generate_cv.py", "--config", config_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error generating files:\n{result.stderr}")
        return False

    print(result.stdout)

    # Step 2: Compile PDF
    with open(config_path) as f:
        config = json.load(f)
    output_dir = Path(config["output_dir"])
    template_type = config.get("template", "tlc")

    # Choose compiler based on template
    if template_type in ("awesome-cv", "unified"):
        print("Step 2: Compiling PDF with latexmk (xelatex)...")
        result = subprocess.run(
            [
                "latexmk",
                "-xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "resume.tex",
            ],
            cwd=output_dir,
            capture_output=True,
            text=True,
        )
    else:
        print("Step 2: Compiling PDF with latexmk (pdflatex)...")
        result = subprocess.run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "resume.tex",
            ],
            cwd=output_dir,
            capture_output=True,
            text=True,
        )

    if result.returncode != 0:
        print("Warning: LaTeX compilation had warnings/errors")
        # Print last 1000 chars of output for debugging
        if result.stdout:
            print(result.stdout[-1000:])

    pdf_path = output_dir / "resume.pdf"
    if pdf_path.exists():
        print(f"✓ Successfully built {variant_name} CV: {pdf_path}")
        return True
    else:
        print("✗ Failed to generate PDF")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py <variant>")
        print(f"Variants: {', '.join(CONFIGS.keys())}, all")
        sys.exit(1)

    variant = sys.argv[1]

    if variant == "all":
        success = all(build_variant(v) for v in CONFIGS.keys())
    else:
        success = build_variant(variant)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
