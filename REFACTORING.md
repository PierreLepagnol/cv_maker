# Refactoring Plan: Unified CV Architecture

## Current State Analysis

**What exists today:**
- **cv_unified/** — Two `.sty` styles (academic, industry) on top of `article.cls` + legacy `TLCresume.sty`. Python pipeline generates `.tex` sections from `data/*.json`.
- **cv_sciam/** — Standalone `sciamcv.cls` class with its own TikZ-based layout. Hand-written `.tex`, not connected to JSON pipeline.
- **scripts/** — Flat directory with 6 Python modules, some legacy (TLC generators), a mix of concerns.

**Problems:**
1. Two incompatible LaTeX architectures for the same person's CV
2. `TLCresume.sty` is a third-party dependency baked in with hacks
3. `section_generators.py` contains dead legacy TLC generators + one shared function
4. `cv_sciam/cv.tex` is hand-maintained, can't benefit from JSON data
5. No proper document class — academic/industry use bare `article.cls`
6. Duplicated code between `cv_style_academic.sty` and `cv_style_industry.sty` (education macros, spacing, etc.)

## Target Architecture

```
curriculum_vitae/
├── cv/                          # All LaTeX class + styles
│   ├── lepagnolcv.cls           # THE document class (core infrastructure)
│   ├── cv_style_academic.sty    # Academic style
│   ├── cv_style_industry.sty    # Industry style (Awesome-CV inspired)
│   ├── cv_style_sciam.sty       # SCIAM corporate style
│   └── fonts/                   # Vendored fonts
├── data/                        # JSON source data (unchanged)
├── config/                      # Variant configs (simplified)
│   ├── academic.json
│   ├── industry.json
│   └── sciam.json
├── src/
│   └── cv_generator/            # Python package
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       ├── config.py            # Config loading
│       ├── escape.py            # LaTeX escaping
│       ├── models.py            # Pydantic data models
│       ├── rendering.py         # LaTeX builder infrastructure
│       └── generators.py        # Section generators (unified only)
├── templates/                   # Main .tex templates per variant
│   ├── academic.tex
│   ├── industry.tex
│   └── sciam.tex
├── build/                       # Generated output (gitignored)
├── build.py                     # Simplified build script
├── Makefile                     # Build shortcuts (+ sciam target)
└── pyproject.toml               # Updated with package config
```

Usage: `\documentclass{lepagnolcv}` + `\usepackage{cv_style_academic}`

## Execution Plan (7 Phases)

### Phase 1: Create `lepagnolcv.cls` — The Document Class ✅
**Goal:** Single `.cls` that provides core infrastructure for all variants.

**Tasks:**
1. Create `cv/lepagnolcv.cls` that:
   - Loads `article` as base class (with `a4paper` option)
   - Handles PDF/XeLaTeX engine detection (`iftex`)
   - Loads shared packages (xcolor, hyperref, graphicx, enumitem, etoolbox, fontspec/fontenc, etc.)
   - Defines core semantic macros as **no-ops or minimal defaults** that styles override:
     - `\cvmakeheader`, `\cvsection`, `\cventry`, `\cvskill`, `\cvparagraph`, `\cveduentry`, etc.
   - Provides shared spacing knobs from current `cv_core.sty` (`\cventrysep`, `\cvitemssep`, etc.)
   - Provides metadata commands and contact value `\def`s
   - Provides shared helpers (`\cvHuggingFaceIcon`, `\cvtexorpdfline`, `\cvhrulefill`)
   - Exposes `\cvsetup{key=value}` via pgfkeys for style-agnostic configuration
2. Absorb `cv_core.sty` into the class (delete it after migration)
3. Absorb/replace `TLCresume.sty` (delete it after migration)

**Verification:** The class file compiles with a minimal test document.

### Phase 2: Migrate Styles to New Architecture
**Goal:** Three `.sty` files, each providing visual identity on top of `lepagnolcv.cls`.

**Tasks:**
1. **`cv/cv_style_academic.sty`** — Refactor from current `cv_style_academic.sty`:
   - Remove `TLCresume.sty` dependency (use class-provided infrastructure)
   - Override `\cvmakeheader` with the fancyhdr-based academic header
   - Override `\cvsection`, `\cventry`, `\cvskills`, `\cvitems`, education macros
2. **`cv/cv_style_industry.sty`** — Refactor from current `cv_style_industry.sty`:
   - Remove duplicate package loading (handled by class)
   - Override macros with Awesome-CV-inspired tabular layout
   - Keep Roboto font loading, color scheme
3. **`cv/cv_style_sciam.sty`** — Extract from `sciamcv.cls`:
   - Move all visual elements (TikZ banner, paracol layout, photo, colors) into a style package
   - Override `\cvmakeheader` → TikZ banner + logo
   - Override `\cvsection` → left/right column adaptive version
   - Provide `\makeprofil`, `\cvmission`, `cvcolumns`/`cvleft`/`cvright` environments
   - Provide SCIAM-specific pgfkeys (maincolor, accentcolor, photoradius, etc.)
4. Delete `sciamcv.cls` (now `cv_style_sciam.sty`)
5. Move `fonts/` to `cv/fonts/`

**Verification:** Each style compiles correctly when loaded after the class.

### Phase 3: Create Template `.tex` Files
**Goal:** One main `.tex` template per variant, all using the unified class.

**Tasks:**
1. **`templates/academic.tex`** — Refactor `resume_academic.tex`
2. **`templates/industry.tex`** — Refactor `resume_industry.tex`
3. **`templates/sciam.tex`** — Refactor `cv.tex` to use the class + style
4. Delete old directories: `cv_unified/`, `cv_sciam/`

**Verification:** Templates have valid structure and reference only the new class/styles.

### Phase 4: Restructure Python Code as `src/cv_generator/`
**Goal:** Clean, modular Python package. Remove all dead code.

**Tasks:**
1. Create `src/cv_generator/` package with `__init__.py`
2. **`src/cv_generator/escape.py`** — Move from `latex_escaper.py`
3. **`src/cv_generator/models.py`** — Move from `data_models.py`
4. **`src/cv_generator/rendering.py`** — Move from `latex_rendering.py`
5. **`src/cv_generator/config.py`** — Move from `config_loader.py`
6. **`src/cv_generator/generators.py`** — Move from `unified_generators.py`:
   - Rename functions: `generate_unified_X` → `generate_X`
   - Move `generate_contact_values_section` from `section_generators.py`
7. **`src/cv_generator/__main__.py`** — Refactor from `generate_cv.py`:
   - Simplify `copy_template_files()` — no more TLC/awesome-cv branching
   - Clean up `build_tokens()`
8. Delete `scripts/` directory entirely (including all legacy TLC generators)
9. Delete `main.py` (placeholder, unused)
10. Update `pyproject.toml` with package configuration

**Verification:** `uv run python -m cv_generator --config config/academic.json` works.

### Phase 5: Add Sciam Generators
**Goal:** Generate sciam CV sections from the same JSON data.

**Tasks:**
1. Add sciam-specific generators in `generators.py`:
   - `generate_sciam_experience` → `\cventry`/`\cvmission` macros
   - `generate_sciam_education` → `\cvskills{...}` for the left column
   - `generate_sciam_publications` → `\cvpublication{title}{venue}`
   - `generate_sciam_skills` → `\cvskills{...}` for left column
   - `generate_sciam_projects` → `\begin{cvitems}...\end{cvitems}`
2. Create `config/sciam.json`
3. Add `sciam` to `build.py` CONFIGS dict
4. Add `sciam` target to Makefile

**Verification:** `make sciam` builds a PDF matching the current sciam look.

### Phase 6: Update Build Pipeline
**Goal:** `build.py` and config files work with the new structure.

**Tasks:**
1. Simplify `build.py`: update paths, always use `latexmk -xelatex`, clean up error messages
2. Update `config/academic.json` and `config/industry.json`: change `template_source` to `"cv"`, update `main_template` to reference `templates/`
3. Update Makefile with `sciam` target
4. Update `.gitignore` if needed
5. Copy assets (profile.jpg, huggingface.svg) to appropriate locations

**Verification:** `make all` builds all 3 variants successfully.

### Phase 7: Final Cleanup & Documentation
**Goal:** Remove dead code, update docs, verify everything.

**Tasks:**
1. Remove empty/dead files: `main.py`, backup files (`*.bak0`), `indent.log`
2. Update `AGENTS.md` with new project structure
3. Update `README.md`
4. Run `make clean && make all` — verify all 3 PDFs generate correctly
5. Visually compare output PDFs with current versions to ensure no regressions

## Key Design Decisions

| Decision | Choice |
|-|--|
| Architecture | Single `.cls` + multiple `.sty` styles |
| Class name | `lepagnolcv.cls` |
| LaTeX home | `cv/` directory |
| Python home | `src/cv_generator/` package |
| Legacy code | Remove all (TLCresume.sty, old generators) |
| Sciam | Unified as `cv_style_sciam.sty` + JSON generation |
| Compiler | XeLaTeX only (drop pdflatex path) |
