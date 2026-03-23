# Dynamic LaTeX CV Builder

This project builds a CV from three inputs:

- `data/resume.yaml` for content
- `themes/*.yaml` for visual tokens, styles, and layouts
- `templates/resume.tex.j2` for layout and section order

`build.py` validates the YAML, generates `out/resume.cls`, renders `out/resume.tex`, and compiles `out/resume.pdf`.

## Quick Start

```bash
uv sync
uv run build.py industry
```

You can also build with explicit theme and layout values:

```bash
uv run build.py --theme minimal --layout twocol
```

Python 3.14+ is required.

## Preset Variants

These aliases are built into `build.py`:

- `academic`
- `industry`
- `industry-footer`
- `sciam`

They map to a theme plus a layout, so they are just shortcuts for `--theme ... --layout ...`.

## Output

Generated files are written to `out/` by default:

- `out/resume.cls`
- `out/resume.tex`
- `out/resume.pdf`

You can override the destination with `--output-dir`.

## Project Structure

```
curriculum_vitae/
|- build.py
|- schema.yaml
|- theme-schema.yaml
|- data/
|  `- resume.yaml
|- themes/
|  |- _base.yaml
|  |- academic.yaml
|  |- bold.yaml
|  `- minimal.yaml
|- templates/
|  `- resume.tex.j2
`- out/
```

## Theme Model

Theme files are pure data. They use five top-level blocks:

- `colors` for named colors
- `fonts` for logical font families
- `sizes` for reusable type sizes and margins
- `rules` for reusable spacing and layout tokens
- `macros` for public `\cv*` command configuration

The layout model is intentionally simple:

- the template decides where sections go
- `rules` stores reusable spacing tokens
- text macros use named `variants`
- `cventry`, `cvskill`, and `cvsectiontitle` split `styles` from `layouts`

Canonical `rules` tokens in `themes/_base.yaml` are:

- `section_rule_width`
- `section_rule_gap`
- `section_spacing`
- `column_gap`
- `column_ratios`
- `tight_spacing`
- `project_spacing`
- `stack_gap`
- `entry_gap`
- `block_spacing`
- `sidebar_rule_gap`
- `sidebar_spacing`
- `header_gap`
- `header_bottom_gap`

## Layouts

Supported layouts are:

- `single`
- `twocol`
- `twocol-footer`

For two-column layouts, tune the split with `rules.column_ratios`, for example:

```yaml
rules:
  column_ratios: [0.36, 0.64]
```

## Public Macro API

Themes can style these public commands:

- `\cvname`
- `\cvtitle`
- `\cvmeta`
- `\cvbody`
- `\cvsmall`
- `\cventry`
- `\cvskill`
- `\cvsectiontitle`

Text macros accept one optional variant name:

```tex
\cvname{Pierre Lepagnol}
\cvname[hero]{Pierre Lepagnol}
```

Structured macros accept `[style][layout]`:

```tex
\cventry[base][inline]{Paper title}{2026}{Venue}{}
\cvskill[aside][stacked]{ML and NLP}{Transformers, RAG, Evaluation}
\cvsectiontitle[aside][sidebar]{Skills}
```

Canonical layouts are:

- `\cventry`: `standard`, `inline`, `stacked`
- `\cvskill`: `inline`, `stacked`
- `\cvsectiontitle`: `standard`, `sidebar`

The base theme also defines semantic styles:

- `\cventry`: `base`
- `\cvskill`: `base`, `aside`
- `\cvsectiontitle`: `base`, `aside`

## Style/Layout Split

Text macros still use inherited `variants`.

For `cventry`, `cvskill`, and `cvsectiontitle`:

- `styles` own typography, colors, weights, shapes, and rule appearance
- `layouts` own structure and spacing
- `default_style` and `default_layout` select the fallback pair

Example:

```yaml
macros:
  cvsectiontitle:
    default_style: base
    default_layout: standard
    styles:
      aside:
        size: sidebar_section
        line: sidebar_section_line
        color: accent
        case: uppercase
        rule_color: accent
        rule_length: "0.38\\linewidth"
    layouts:
      sidebar:
        mode: sidebar
```

## Validation

`build.py` validates:

- `data/resume.yaml` against `schema.yaml`
- `themes/*.yaml` against `theme-schema.yaml`

Theme validation also checks variant/style/layout names, field values, token references, and supported layout modes before LaTeX generation starts.

## Compile Engine

PDF compilation uses `latexmk -lualatex`.

## More Detail

For a complete walkthrough of theme tokens, macro fields, template customization, layout examples, and troubleshooting, see `TUTORIAL.md`.
