# Agent Guidelines for Curriculum Vitae Project

This document provides essential information for AI coding agents working on this LaTeX CV generation system.

## Project Overview

A data-driven CV generator that separates content (JSON) from presentation (LaTeX), enabling multiple CV variants (academic, industry, sciam) from a single data source.

**Tech Stack**: Python 3.14+, LaTeX (latexmk/xelatex), JSON, uv package manager

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
# Sync dependencies and install the cv_generator package
uv sync

# Run generator directly (useful for debugging)
uv run python -m cv_generator --config config/academic.json

# Manual LaTeX compilation
cd build/academic && latexmk -xelatex resume.tex
```

## Testing

**No test suite currently exists.**

When adding tests in the future:
- Use pytest as the testing framework
- Place test files in `tests/` directory
- Name test files as `test_*.py`
- Run with: `uv run pytest`

## Code Style Guidelines

### General Principles

- **KISS**: Keep everything Simple and Stupid
- Write clear, readable code over clever code
- Prefer standard library over external dependencies
- Separate concerns into focused modules

### Python Style

**Imports (within the package):** Use relative imports.
```python
from .escape import escape_latex
from .models import Contact
from .rendering import LatexBuilder
```

**Path Handling:** Always use `pathlib.Path`.

**Docstrings:**
```python
def generate_skills(skills_data):
    """Generate skills as cvskills/cvskill rows."""
```

### File Organization

```
curriculum_vitae/
├── cv/                      # LaTeX class + styles + assets
│   ├── lepagnolcv.cls       # Core document class
│   ├── cv_style_academic.sty
│   ├── cv_style_industry.sty
│   ├── cv_style_sciam.sty
│   ├── fonts/               # Vendored fonts (Roboto, FontAwesome)
│   ├── profile.png          # Optional profile photo
│   └── huggingface.svg      # Optional HF icon
├── data/                    # JSON source files (user-editable)
├── config/                  # CV variant configurations
│   ├── academic.json
│   └── industry.json
├── src/
│   └── cv_generator/        # Python package
│       ├── __init__.py
│       ├── __main__.py      # CLI (python -m cv_generator)
│       ├── config.py        # Config + data loading
│       ├── escape.py        # LaTeX character escaping
│       ├── models.py        # Pydantic data models
│       ├── rendering.py     # LaTeX builder infrastructure
│       └── generators.py    # Section generators + registry
├── templates/               # Main .tex templates per variant
│   ├── academic.tex
│   ├── industry.tex
│   └── sciam.tex
├── build/                   # Generated output (gitignored)
├── build.py                 # Main build script
├── Makefile                 # Build shortcuts
└── pyproject.toml           # Package config (hatchling)
```

### JSON Data Files

- 2-space indentation, lowercase keys with underscores
- Keep structure flat when possible

### LaTeX Escaping Rules

- **Always** use `escape_latex()` for user content
- **Never** escape URLs or email addresses
- Special chars escaped: `& % $ # _ { } ~ ^`

## Module Responsibilities

| Module | Responsibility |
|||
| `__main__.py` | CLI: loads config, copies style files, renders templates, processes `\input{}` |
| `config.py` | Loads JSON config and data files with sensible defaults |
| `escape.py` | Escapes LaTeX special characters while preserving URLs/emails |
| `models.py` | Pydantic models for all JSON sections |
| `rendering.py` | `LatexBuilder`, `ListSectionRenderer`, `CompositeRenderer` |
| `generators.py` | `generate_*` functions + `SECTION_GENERATORS` registry |

## Common Tasks

### Adding a New Section

1. Add `data/new_section.json`
2. Add a Pydantic model in `models.py`
3. Write `generate_new_section()` in `generators.py`
4. Register it in `SECTION_GENERATORS`
5. Add `\input{resume/new_section}` to the relevant template(s)

### Adding a New CV Variant

1. Create `config/new_variant.json`
2. Create `templates/new_variant.tex`
3. Add to `CONFIGS` in `build.py`
4. Add `make new_variant` to `Makefile`
5. `uv run build.py new_variant`

### Debugging LaTeX Errors

```bash
uv run python -m cv_generator --config config/academic.json
cd build/academic && latexmk -xelatex resume.tex
```

## Git Commit Style

Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`

## Key Constraints

1. **No external Python dependencies** beyond pydantic
2. **Keep JSON simple** — avoid nested structures when possible
3. **Auto-escape by default** — all user content goes through `escape_latex()`
4. **XeLaTeX only** — pdflatex support is dropped
5. **Template-driven section order** — comes from `\input{}` in `.tex` templates
