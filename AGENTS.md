# Agent Guidelines for Curriculum Vitae Project

This document provides essential information for AI coding agents working on this LaTeX CV generation system.

## Project Overview

A data-driven CV generator that separates content (JSON) from presentation (LaTeX), enabling multiple CV variants (academic, industry) from a single data source.

**Tech Stack**: Python 3.13+, LaTeX (latexmk/xelatex), JSON, uv package manager

---

## Build Commands

### Building CVs

```bash
# Build all CV variants
make all
# OR
uv run build.py all

# Build specific variant
make academic
make industry
# OR
uv run build.py academic
uv run build.py industry

# Clean all build artifacts
make clean
```

### Python Environment

```bash
# Install dependencies (if any added)
uv sync

# Run generation script directly
uv run scripts/generate_cv.py --config config/academic.json
```

### Manual LaTeX Compilation

```bash
# Unified template (academic)
cd build/academic && latexmk -xelatex resume.tex

# Unified template (industry)
cd build/industry && latexmk -xelatex resume.tex
```

---

## Testing

**⚠️ No test suite currently exists.**

When adding tests in the future:
- Use pytest as the testing framework
- Place test files in `tests/` directory
- Name test files as `test_*.py`
- Run tests with: `uv run pytest`
- Run single test file: `uv run pytest tests/test_specific.py`
- Run single test function: `uv run pytest tests/test_file.py::test_function_name`

---

## Code Style Guidelines

### General Principles

- **KISS**: Keep everything Simple and Stupid
- Write clear, readable code over clever code
- Prefer standard library over external dependencies
- Separate concerns into focused modules

### Python Style

**Naming Conventions:**
- `snake_case` for functions, variables, module names
- `UPPER_CASE` for constants and global dictionaries
- Descriptive names that reveal intent (e.g., `generate_contact_macros`, `escape_latex`)

**Imports:**
```python
# Standard library imports first (alphabetical)
import argparse
import json
import re
import sys
from pathlib import Path

# Local imports last
from config_loader import load_config, load_data
from latex_escaper import escape_latex
```

**String Formatting:**
- Use f-strings for string interpolation: `f"Error: {exc}"`
- Use raw strings for regex patterns: `r"\input\s*{([^}]+)}"`

**Path Handling:**
- Always use `pathlib.Path` for file operations
- Example: `output_dir = Path(config['output_dir'])`

**Error Handling:**
```python
# Catch specific exceptions
try:
    config = load_config(args.config)
except (FileNotFoundError, ValueError) as exc:
    print(f"Error: {exc}")
    sys.exit(1)
```

**Docstrings:**
```python
def function_name(arg1, arg2):
    """
    Brief description of function.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value
    """
```

**Type Hints:**
- Currently NOT used in the codebase
- If adding them, use standard typing module
- Example: `def load_config(config_path: str) -> dict:`

### File Organization

```
curriculum_vitae/
├── data/              # JSON source files (user-editable)
├── config/            # CV variant configurations
├── scripts/           # Core generation logic (modular)
│   ├── config_loader.py          # Configuration loading
│   ├── latex_escaper.py          # LaTeX character escaping
│   ├── section_generators.py     # Legacy TLC generators + shared token helpers
│   └── unified_generators.py     # Unified semantic section generators
├── cv_unified/         # Unified LaTeX engine + switchable styles
├── build/             # Generated output (gitignored)
├── build.py           # Main build script
└── Makefile           # Build shortcuts
```

### JSON Data Files

**Formatting:**
- Use 2-space indentation
- Use lowercase keys with underscores: `"start_date"`
- Keep structure flat when possible
- Required fields should come first

**Example:**
```json
{
  "name": "Full Name",
  "role": "Job Title",
  "email": "email@example.com",
  "optional_field": null
}
```

### LaTeX Escaping Rules

- **Always** use `escape_latex()` for user content
- **Never** escape URLs (auto-detected by `http://` or `https://`)
- **Never** escape email addresses (auto-detected)
- Special chars escaped: `& % $ # _ { } ~ ^`

---

## Module Responsibilities

### `scripts/generate_cv.py`
Main orchestrator: loads config, generates sections, renders templates with token replacement.

### `scripts/config_loader.py`
Loads JSON config and data files with sensible defaults for missing files.

### `scripts/latex_escaper.py`
Escapes special LaTeX characters while preserving URLs and emails.

### `scripts/section_generators.py`
Legacy TLC generators plus shared helpers (e.g. contact values token file).

### `scripts/unified_generators.py`
Generates semantic LaTeX sections (single markup) used by the unified templates.

### `build.py`
CLI entry point: coordinates generation + compilation for CV variants.

---

## Common Tasks

### Adding a New Section

1. Add JSON data file: `data/new_section.json`
2. Create generator function in `scripts/unified_generators.py`:
   ```python
   def generate_new_section(section_data):
       """Generate new section LaTeX."""
       # Implementation
       return latex_string
   ```
3. Register in `UNIFIED_SECTION_GENERATORS` in `scripts/generate_cv.py`
4. Add `\input{resume/new_section}` (or similar) to the unified template wrapper
5. Update config to enable section

### Adding a New CV Variant

1. Create config file: `config/new_variant.json`
2. Create template directory: `cv_new_variant/`
3. Add to `CONFIGS` dict in `build.py`:
   ```python
   CONFIGS = {
       'academic': 'config/academic.json',
       'industry': 'config/industry.json',
       'new_variant': 'config/new_variant.json'
   }
   ```
4. Build with: `uv run build.py new_variant`

### Debugging LaTeX Errors

```bash
# Check generation step
uv run scripts/generate_cv.py --config config/academic.json

# Check compilation step
cd build/academic
latexmk -xelatex resume.tex
# View logs
cat resume.log
```

---

## Git Commit Style

- Use conventional commits format
- Examples:
  - `feat: add skills section generator`
  - `fix: escape special characters in company names`
  - `docs: update README with new build commands`
  - `refactor: extract token rendering logic`

---

## Key Constraints

1. **No external Python dependencies** - Keep using stdlib only
2. **Preserve LaTeX template compatibility** - Don't break existing CV builds
3. **Keep JSON simple** - Avoid nested structures when possible
4. **Auto-escape by default** - All user content must go through `escape_latex()`
5. **Template-driven** - Section order comes from `\input{}` statements in templates

---

## Questions or Issues?

Refer to:
- `README.md` for user-facing documentation
- `scripts/` modules for implementation details
- `config/*.json` for variant examples
