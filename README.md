# Dynamic LaTeX CV Builder

This project now follows the redesign in `cv-builder-redesign.md`: one content file, one schema, pure-data themes, one Jinja2 template, one executable, and generated LaTeX output.

## Quick Start

```bash
uv self update
uv python install 3.14.3
uv sync
uv run build.py --theme minimal --layout twocol
```

Python 3.14+ is required.

For a complete walkthrough of themes, named macro variants, template customization,
and troubleshooting, see `TUTORIAL.md`.

Generated files are written to `out/` by default:
- `out/resume.cls`
- `out/resume.tex`
- `out/resume.pdf`

## Structure

```
curriculum_vitae/
├── build.py
├── schema.yaml
├── theme-schema.yaml
├── data/
│   └── resume.yaml
├── themes/
│   ├── minimal.yaml
│   ├── academic.yaml
│   └── bold.yaml
├── templates/
│   └── resume.tex.j2
└── out/
```

## Variation Axes

- Content: `data/resume.yaml`
- Theme: `themes/*.yaml`
- Layout: `--layout single` or `--layout twocol`

Example combinations:

```bash
uv run build.py --theme minimal --layout single
uv run build.py --theme bold --layout single
uv run build.py --theme minimal --layout twocol
uv run build.py --theme academic --layout twocol
```

For `twocol`, you can tune each theme's column widths with `rules.column_ratios`
in `themes/*.yaml`, for example `column_ratios: [0.36, 0.64]`.

## Validation

`build.py` validates:

- `data/resume.yaml` against `schema.yaml`
- `themes/*.yaml` against `theme-schema.yaml`

Theme validation also performs semantic checks for named macro variants, token references,
and supported layouts before LaTeX generation starts.

## Macro Variants

Themes can now customize the public `\cv*` commands with named variants while keeping
their semantic API stable:

- `\cvname`
- `\cvtitle`
- `\cvmeta`
- `\cvbody`
- `\cvsmall`
- `\cventry`
- `\cvskill`
- `\cvsectiontitle`

Each macro keeps the same base signature as before, and now also accepts an optional
variant name:

```tex
\cvname{Pierre Lepagnol}
\cvname[hero]{Pierre Lepagnol}

\cvskill{ML and NLP}{Transformers, RAG, Evaluation}
\cvskill[compact]{ML and NLP}{Transformers, RAG, Evaluation}
```

Theme files use a `macros` block to define defaults and named variants:

```yaml
macros:
  cvname:
    default: standard
    variants:
      standard: {}
      hero:
        size: hero_name
        line: hero_name_line
        color: accent

  cvsectiontitle:
    default: standard
    variants:
      standard: {}
      sidebar:
        layout: sidebar
        color: accent
        case: uppercase
        rule_color: accent
        rule_length: "0.38\\linewidth"
```

Variant values inherit from the generated `standard` variant, so most custom variants
only need to override the fields they want to change.

If a theme omits `macros`, `build.py` synthesizes `standard` variants from the legacy
top-level theme tokens for backward compatibility.

## Compile Engine

PDF compilation uses `latexmk -lualatex`.
