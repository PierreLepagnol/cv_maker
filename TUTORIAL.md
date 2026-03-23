# CV Builder Tutorial

This tutorial covers the whole system with the simplified theme model:

- build a CV
- switch theme and layout
- tune colors, typography, spacing, and column widths
- add variants, styles, and layouts for `\cv*` macros
- keep layout logic in the template

## 1. Quick Start

Install dependencies and build one preset CV:

```bash
uv sync
uv run build.py industry
```

Or build with an explicit theme and layout:

```bash
uv run build.py --theme minimal --layout twocol
```

Write output somewhere else:

```bash
uv run build.py --theme bold --layout single --output-dir .tmp/bold-single
```

Preset aliases available in `build.py`:

- `academic`
- `industry`
- `industry-footer`
- `sciam`

Generated files go to `out/` by default:

- `out/resume.cls`
- `out/resume.tex`
- `out/resume.pdf`

## 2. Mental Model

Keep the responsibilities separate:

1. `data/resume.yaml` stores content
2. `themes/*.yaml` stores visual tokens plus macro styles and layouts
3. `templates/resume.tex.j2` decides section order and layout

The main simplification rule is:

- text variants describe rendering
- structured macros split style from layout
- theme rules store reusable spacing values
- the template decides where sections go

If you want to change wording, edit `data/resume.yaml`.

If you want to change look and feel, edit `themes/*.yaml`.

If you want to move sections around, edit `templates/resume.tex.j2`.

## 3. Build Flow

When you run:

```bash
uv run build.py --theme minimal --layout twocol
```

the builder:

1. loads `data/resume.yaml`
2. validates it with `schema.yaml`
3. loads `themes/_base.yaml` and the chosen theme override
4. validates the merged theme with `theme-schema.yaml`
5. normalizes text variants plus structured macro style/layout defaults
6. generates `resume.cls`
7. renders `templates/resume.tex.j2` into `resume.tex`
8. compiles with `latexmk -lualatex`

## 4. Project Structure

Core files:

- `build.py`: loads YAML, validates, generates LaTeX, compiles PDF
- `data/resume.yaml`: CV content
- `schema.yaml`: resume schema
- `theme-schema.yaml`: theme schema
- `themes/_base.yaml`: shared visual defaults
- `themes/minimal.yaml`: theme colors for the minimal preset
- `themes/academic.yaml`: theme colors for the academic preset
- `themes/bold.yaml`: theme colors for the sciam preset
- `templates/resume.tex.j2`: section layout and macro usage
- `cv/fonts/`: vendored fonts copied into the build output

## 5. Theme Anatomy

A theme file has five top-level blocks:

```yaml
colors:
fonts:
sizes:
rules:
macros:
```

### `colors`

Named color tokens:

```yaml
colors:
  primary: "#2d2d2d"
  accent: "#4a7c96"
  muted: "#777777"
  rule: "#cccccc"
```

### `fonts`

Logical font families used by macro variants:

```yaml
fonts:
  heading: "Roboto"
  body: "Roboto"
```

### `sizes`

Reusable typography and margin tokens:

```yaml
sizes:
  name: "24pt"
  name_line: "28pt"
  title: "12pt"
  title_line: "15pt"
  body: "10pt"
  body_line: "13pt"
  margin_top: "0.7cm"
  margin_bottom: "0.7cm"
  margin_side: "0.5cm"
```

Add extra tokens here when they are typography-related, such as `hero_name` or `sidebar_section_line`.

### `rules`

Reusable layout and spacing tokens:

```yaml
rules:
  section_rule_width: "0.4pt"
  section_rule_gap: "2pt"
  section_spacing: "10pt"
  column_gap: "30pt"
  column_ratios: [0.36, 0.64]
  tight_spacing: "0pt"
  project_spacing: "1pt"
  stack_gap: "1pt"
  entry_gap: "2pt"
  block_spacing: "5pt"
  sidebar_rule_gap: "4pt"
  sidebar_spacing: "6pt"
  header_gap: "4pt"
  header_bottom_gap: "12pt"
```

Use these canonical rule names in themes.

### `macros`

This block defines public `\cv*` command configuration.

- text macros use `variants`
- `cventry`, `cvskill`, and `cvsectiontitle` use `styles` and `layouts`

Example:

```yaml
macros:
  cvmeta:
    variants:
      links:
        size: meta_links
        line: meta_links_line
        color: accent
```

You only need to define the fields you want to change.

## 6. Defaults and Composition

Text variants inherit from a generated base variant named `standard`.

Structured macros compose two independent pieces:

- `styles` inherit from a generated base style named `base`
- `layouts` inherit from canonical mode defaults such as `standard`, `inline`, `stacked`, and `sidebar`

That means you usually only override the fields you actually want to change.

Canonical layout defaults are:

- `cventry[...][standard]` and `cventry[...][inline]` use `tight_spacing` and `entry_gap`
- `cventry[...][stacked]` uses `project_spacing` and `entry_gap`
- `cvskill[...][stacked]` uses `stack_gap`
- `cvsectiontitle[...][sidebar]` uses `sidebar_rule_gap` and `sidebar_spacing`

So in most themes, styles only need to express visual differences and layouts only need to express structural differences.

If a theme omits `macros`, `build.py` synthesizes the base text variants plus the base structured styles and canonical layouts automatically.

## 7. Public Macro API

These commands are available in the template:

- `\cvname[variant]{text}`
- `\cvtitle[variant]{text}`
- `\cvmeta[variant]{text}`
- `\cvbody[variant]{text}`
- `\cvsmall[variant]{text}`
- `\cventry[style][layout]{arg1}{arg2}{arg3}{arg4}`
- `\cvskill[style][layout]{label}{value}`
- `\cvsectiontitle[style][layout]{text}`

If you omit optional arguments, the macro defaults are used.

Example:

```tex
\cvname{Pierre Lepagnol}
\cvname[hero]{Pierre Lepagnol}

\cvskill{ML and NLP}{Transformers, RAG, Evaluation}
\cvskill[aside][stacked]{ML and NLP}{Transformers, RAG, Evaluation}
```

## 8. Canonical Layout Names

Use the canonical layout names in new templates and themes:

- `\cventry` layouts: `standard`, `inline`, `stacked`
- `\cvskill` layouts: `inline`, `stacked`
- `\cvsectiontitle` layouts: `standard`, `sidebar`

The base theme also defines these semantic style names:

- `\cventry` styles: `base`
- `\cvskill` styles: `base`, `aside`
- `\cvsectiontitle` styles: `base`, `aside`

## 9. Macro Field Reference

### Text macros

These share the same field shape:

- `cvname`
- `cvtitle`
- `cvmeta`
- `cvbody`
- `cvsmall`

Supported fields:

- `font`
- `size`
- `line`
- `color`
- `weight`: `normal` or `bold`
- `shape`: `normal`, `italic`, or `slanted`
- `case`: `normal`, `uppercase`, or `smallcaps`

Example:

```yaml
macros:
  cvtitle:
    variants:
      headline:
        size: headline_title
        line: headline_title_line
        color: primary
        weight: bold
```

### `cventry`

Used for jobs, education items, publications, and projects.

Supported style fields:

- `font`, `size`, `line`
- `meta_size`, `meta_line`
- `line1_left_weight`, `line1_left_shape`, `line1_left_color`
- `line1_right_weight`, `line1_right_shape`, `line1_right_color`
- `line2_left_weight`, `line2_left_shape`, `line2_left_color`
- `line2_right_weight`, `line2_right_shape`, `line2_right_color`
- `meta_color`

Supported layout fields:

- `mode`: `standard`, `inline`, `stacked`
- `line_gap`
- `bottom_gap`
- `bottom_mode`: `linebreak` or `paragraph`

Typical example:

```yaml
macros:
  cventry:
    default_style: base
    default_layout: standard
    styles:
      base:
        line2_left_shape: italic
        line2_left_color: muted
        line1_right_color: muted
    layouts:
      inline:
        mode: inline
      stacked:
        mode: stacked
```

Only override `line_gap` or `bottom_gap` when you want a special case beyond the canonical layout defaults.

### `cvskill`

Renders a label/value pair like `Frameworks: PyTorch, vLLM`.

Supported style fields:

- `font`, `size`, `line`
- `label_weight`
- `label_color`
- `value_color`
- `separator`

Supported layout fields:

- `mode`: `inline` or `stacked`
- `stack_gap`

Example:

```yaml
macros:
  cvskill:
    default_style: base
    default_layout: inline
    styles:
      base:
        separator: " "
        value_color: muted
      aside:
        label_color: accent
        value_color: muted
    layouts:
      stacked:
        mode: stacked
```

### `cvsectiontitle`

Renders headings like `Experience` or `Skills`.

Supported style fields:

- `font`, `size`, `line`
- `color`, `weight`, `shape`, `case`
- `rule_enabled`
- `rule_color`, `rule_width`, `rule_length`

Supported layout fields:

- `mode`: `standard` or `sidebar`
- `rule_gap_before`, `rule_gap_after`

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

## 10. Template Layouts

The template controls structure.

Supported layouts:

- `single`: one column
- `twocol`: two columns with sidebar on the left
- `twocol-footer`: same two-column header/body, then full-width footer sections

The current template uses one shared condition for two-column behavior:

```jinja
{% set is_two_column = layout in ['twocol', 'twocol-footer'] %}
```

That keeps sidebar-style section titles and stacked skill rows consistent across both two-column layouts.

Example template fragment:

```jinja
{% set is_two_column = layout in ['twocol', 'twocol-footer'] %}

\cvsectiontitle[{{ 'aside' if is_two_column else 'base' }}][{{ 'sidebar' if is_two_column else 'standard' }}]{Skills}
{% for group in skills %}
\cvskill[{{ 'aside' if is_two_column else 'base' }}][{{ 'stacked' if is_two_column else 'inline' }}]
  { {{ group.category | latex_escape }} }
  { {{ group['items'] | join(', ') | latex_escape }} }
{% endfor %}
```

If you want a section in a different place, edit the template, not the theme.

## 11. Customize an Existing Theme

The safest workflow is incremental.

### Step 1: copy an existing theme

```bash
cp themes/minimal.yaml themes/mytheme.yaml
```

### Step 2: tune the palette

```yaml
colors:
  primary: "#1c1f26"
  accent: "#0b7fab"
  muted: "#68707a"
  rule: "#d4d9de"
```

### Step 3: tune type and spacing tokens

```yaml
sizes:
  name: "25pt"
  name_line: "29pt"
  section: "11pt"
  section_line: "13pt"
  body: "9.8pt"
  body_line: "12.8pt"

rules:
  column_ratios: [0.34, 0.66]
  block_spacing: "6pt"
  header_bottom_gap: "14pt"
```

### Step 4: build and inspect

```bash
uv run build.py --theme mytheme --layout twocol
```

## 12. Add a New Style

Example: add a `caps` section-title style.

### Step 1: add any new tokens you need

```yaml
sizes:
  caps_section: "10.5pt"
  caps_section_line: "12.5pt"

rules:
  caps_spacing: "5pt"
```

### Step 2: add the variant

```yaml
macros:
  cvsectiontitle:
    styles:
      caps:
        size: caps_section
        line: caps_section_line
        color: primary
        case: uppercase
        rule_color: primary
```

### Step 3: optionally add a layout override

```yaml
macros:
  cvsectiontitle:
    layouts:
      roomy_sidebar:
        mode: sidebar
        rule_gap_after: caps_spacing
```

### Step 4: use it in the template

```tex
\cvsectiontitle[caps][standard]{Projects}
```

### Step 5: build

```bash
uv run build.py --theme mytheme --layout single
```

## 13. Example Theme Fragment

This is a compact theme fragment aligned with the simplified spacing model:

```yaml
colors:
  primary: "#20242b"
  accent: "#006d77"
  muted: "#68727d"
  rule: "#d7dcdf"

fonts:
  heading: "Roboto"
  body: "Roboto"

sizes:
  name: "24pt"
  name_line: "28pt"
  hero_name: "27pt"
  hero_name_line: "31pt"
  title: "12pt"
  title_line: "15pt"
  headline_title: "11pt"
  headline_title_line: "14pt"
  section: "12pt"
  section_line: "14pt"
  sidebar_section: "10pt"
  sidebar_section_line: "12pt"
  body: "10pt"
  body_line: "13pt"
  lead: "10.5pt"
  lead_line: "14pt"
  small: "9pt"
  small_line: "11pt"
  meta_links: "9.5pt"
  meta_links_line: "12pt"
  entry_meta: "8.5pt"
  entry_meta_line: "10pt"
  margin_top: "0.7cm"
  margin_bottom: "0.7cm"
  margin_side: "0.5cm"

rules:
  section_rule_width: "0.4pt"
  section_rule_gap: "2pt"
  section_spacing: "10pt"
  column_gap: "30pt"
  column_ratios: [0.36, 0.64]
  tight_spacing: "0pt"
  project_spacing: "1pt"
  stack_gap: "1pt"
  entry_gap: "2pt"
  block_spacing: "5pt"
  sidebar_rule_gap: "4pt"
  sidebar_spacing: "6pt"
  header_gap: "4pt"
  header_bottom_gap: "12pt"

macros:
  cvname:
    variants:
      hero:
        size: hero_name
        line: hero_name_line
        color: accent

  cvtitle:
    variants:
      headline:
        size: headline_title
        line: headline_title_line
        color: primary
        weight: bold

  cvmeta:
    variants:
      links:
        size: meta_links
        line: meta_links_line
        color: accent

  cvskill:
    default_style: base
    default_layout: inline
    styles:
      base:
        separator: " "
        value_color: muted
      aside:
        label_color: accent
        value_color: muted
    layouts:
      inline:
        mode: inline
      stacked:
        mode: stacked

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
      standard:
        mode: standard
      sidebar:
        mode: sidebar
```

## 14. Validation and Troubleshooting

The builder fails early on invalid themes.

Useful checks:

- `colors.*` must be hex colors like `#4a7c96`
- macro names must be known
- default variant/style/layout names must exist
- font references must exist in `fonts`
- color references must exist in `colors`
- layout modes must be supported for that macro
- `rules.column_ratios` must contain exactly two positive numbers

Common issues:

### Unknown style or layout

Example:

```tex
\cvsectiontitle[fancy][sidebar]{Projects}
```

If `fancy` is not defined in the active theme, the build fails.

Fix it by defining the style in `macros.cvsectiontitle.styles` or by using an existing name.

### Unknown token

If you reference a color, font, size, or rule token that does not exist, validation fails before LaTeX starts.

### Font issues

The current setup expects the configured font families to match the vendored files in `cv/fonts/`.

### LaTeX compile failure after validation passes

Then the issue is usually in:

- the template structure
- a raw literal LaTeX value such as `rule_length`
- an asset or font resolution problem

Inspect:

- `out/resume.cls`
- `out/resume.tex`
- `out/resume.log`

## 15. Suggested Workflow

For safe iteration:

1. start from `themes/minimal.yaml`
2. change colors first
3. rebuild
4. change sizes and rules
5. rebuild
6. add one variant if needed
7. change the template only after the theme feels right
8. rebuild again

Small steps make layout changes much easier to understand.

## 16. Summary

Use this checklist:

- edit `data/resume.yaml` for content
- edit `themes/*.yaml` for visual tokens, styles, and layouts
- edit `templates/resume.tex.j2` for layout and section order
- use canonical layout names in new code
- use canonical `rules` tokens in new themes
- build with `uv run build.py ...`
