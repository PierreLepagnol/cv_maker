# Full Tutorial: Use and Customize the CV Builder

This tutorial explains how to:

- build the CV
- switch theme and layout
- customize colors, sizes, spacing, and fonts
- add named variants for `\cv*` macros
- use those variants from the Jinja/LaTeX template
- create a brand new theme safely

The system is built around three layers:

1. `data/resume.yaml`: your content
2. `themes/*.yaml`: visual tokens and macro variants
3. `templates/resume.tex.j2`: layout and macro usage

`build.py` validates the data and theme, generates `resume.cls`, renders `resume.tex`, and compiles `resume.pdf`.

## 1. Quick Start

Install dependencies and build one CV:

```bash
uv sync
uv run build.py --theme minimal --layout twocol
```

The output goes to `out/` by default:

- `out/resume.cls`
- `out/resume.tex`
- `out/resume.pdf`

You can also use preset aliases:

```bash
uv run build.py academic
uv run build.py industry
uv run build.py sciam
```

You can write the result to another directory:

```bash
uv run build.py --theme bold --layout single --output-dir .tmp/bold-single
```

## 2. Project Structure

The main files are:

- `build.py`: loads YAML, validates it, generates LaTeX, compiles PDF
- `data/resume.yaml`: resume content
- `schema.yaml`: schema for the resume data
- `theme-schema.yaml`: schema for theme files
- `themes/minimal.yaml`: example theme with named variants
- `themes/bold.yaml`: alternative theme
- `themes/academic.yaml`: alternative theme
- `templates/resume.tex.j2`: template that calls `\cv*` macros
- `cv/fonts/`: vendored fonts copied into the output directory

## 3. The Mental Model

The important idea is this:

- content is data
- appearance is theme data
- structure is controlled by the template
- macro names stay stable
- variants let one macro render in different styles without changing its semantic meaning

Example:

```tex
\cvskill{Frameworks}{PyTorch, Hugging Face, vLLM}
\cvskill[compact]{Frameworks}{PyTorch, Hugging Face, vLLM}
```

Both lines mean "render a skill row". The only difference is which named visual variant gets used.

## 4. How Building Works

When you run:

```bash
uv run build.py --theme minimal --layout twocol
```

the builder does this:

1. loads `data/resume.yaml`
2. validates it with `schema.yaml`
3. loads `themes/minimal.yaml`
4. validates it with `theme-schema.yaml`
5. normalizes missing macro configs into default `standard` variants
6. generates `resume.cls` with all variant-aware `\cv*` commands
7. renders `templates/resume.tex.j2` into `resume.tex`
8. compiles with `latexmk -lualatex`

## 5. Resume Content Basics

Your resume content lives in `data/resume.yaml`.

Typical sections include:

- `meta`
- `summary`
- `experience`
- `education`
- `publications`
- `projects`
- `skills`
- `languages`

This file contains only content. Do not put style variants in it.

Good rule:

- if you want to change wording, edit `data/resume.yaml`
- if you want to change look and feel, edit `themes/*.yaml`
- if you want to change ordering/layout, edit `templates/resume.tex.j2`

## 6. Theme Basics

A theme file has five top-level sections:

```yaml
colors:
fonts:
sizes:
rules:
macros:
```

### `colors`

These are named color tokens.

```yaml
colors:
  primary: "#2d2d2d"
  accent: "#4a7c96"
  muted: "#777777"
  rule: "#cccccc"
```

These names are reused by macro variants.

### `fonts`

These are logical font tokens:

```yaml
fonts:
  heading: "Roboto"
  body: "Roboto"
  mono: "Roboto"
```

Macro variants refer to the token names like `heading` or `body`, not directly to fontspec commands.

### `sizes`

These contain reusable typography and spacing tokens:

```yaml
sizes:
  name: "24pt"
  name_line: "28pt"
  title: "12pt"
  title_line: "15pt"
  body: "10pt"
  body_line: "13pt"
```

You can add your own custom size tokens such as `hero_name`, `sidebar_section`, or `meta_links_line`.

### `rules`

These contain line and spacing tokens:

```yaml
rules:
  section_rule_width: "0.4pt"
  section_spacing: "8pt"
  column_gap: "18pt"
  column_ratios: [0.36, 0.64]
```

You can add custom tokens here too, such as `entry_stack_gap` or `section_sidebar_gap_after`.

### `macros`

This is where named variants live.

Each macro has:

- a `default` variant name
- a `variants` map

Example:

```yaml
macros:
  cvmeta:
    default: standard
    variants:
      standard: {}
      links:
        size: meta_links
        line: meta_links_line
        color: accent
```

Here, `links` inherits from `standard` and overrides only three fields.

## 7. Public Macro API

These are the public macros available in the template:

- `\cvname[variant]{text}`
- `\cvtitle[variant]{text}`
- `\cvmeta[variant]{text}`
- `\cvbody[variant]{text}`
- `\cvsmall[variant]{text}`
- `\cventry[variant]{arg1}{arg2}{arg3}{arg4}`
- `\cvskill[variant]{label}{value}`
- `\cvsectiontitle[variant]{text}`

The optional `[variant]` part can be omitted:

```tex
\cvname{Pierre Lepagnol}
\cvname[hero]{Pierre Lepagnol}
```

If you omit the optional argument, the theme default is used.

## 8. Supported Variant Fields

This is the part you will customize most often.

### Text-style macros

These macros share the same field shape:

- `cvname`
- `cvtitle`
- `cvmeta`
- `cvbody`
- `cvsmall`

Supported fields:

- `font`: font token name from `fonts`
- `size`: size token name from `sizes`
- `line`: line-height token name from `sizes`
- `color`: color token name from `colors`, or omit it
- `weight`: `normal` or `bold`
- `shape`: `normal`, `italic`, or `slanted`
- `case`: `normal`, `uppercase`, or `smallcaps`

Example:

```yaml
macros:
  cvtitle:
    default: standard
    variants:
      standard: {}
      headline:
        size: headline_title
        line: headline_title_line
        color: primary
        weight: bold
```

### `cventry`

This macro is for two-line entries such as jobs, education items, publications, and projects.

Supported fields:

- `layout`: `standard` or `stacked`
- `font`
- `size`
- `line`
- `meta_size`
- `meta_line`
- `line1_left_weight`
- `line1_left_shape`
- `line1_left_color`
- `line1_right_weight`
- `line1_right_shape`
- `line1_right_color`
- `line2_left_weight`
- `line2_left_shape`
- `line2_left_color`
- `line2_right_weight`
- `line2_right_shape`
- `line2_right_color`
- `meta_color`
- `line_gap`
- `bottom_gap`

Example:

```yaml
macros:
  cventry:
    default: standard
    variants:
      standard: {}
      stacked:
        layout: stacked
        meta_size: entry_meta
        meta_line: entry_meta_line
        line_gap: entry_stack_gap
        bottom_gap: entry_stack_bottom_gap
```

Use `stacked` when a narrow column needs a more vertical layout.

### `cvskill`

This macro renders a label/value pair like `Frameworks: PyTorch, vLLM`.

Supported fields:

- `layout`: `inline` or `stacked`
- `font`
- `size`
- `line`
- `label_weight`: `normal` or `bold`
- `label_color`
- `value_color`
- `separator`
- `stack_gap`

Example:

```yaml
macros:
  cvskill:
    default: standard
    variants:
      standard: {}
      compact:
        layout: stacked
        label_color: accent
        value_color: muted
        stack_gap: skill_stack_gap
```

### `cvsectiontitle`

This macro renders section headings such as `Experience` or `Skills`.

Supported fields:

- `layout`: `standard` or `sidebar`
- `font`
- `size`
- `line`
- `color`
- `weight`
- `shape`
- `case`
- `rule_enabled`: `true` or `false`
- `rule_color`
- `rule_width`
- `rule_length`
- `rule_gap_before`
- `rule_gap_after`

Example:

```yaml
macros:
  cvsectiontitle:
    default: standard
    variants:
      standard: {}
      sidebar:
        layout: sidebar
        size: sidebar_section
        line: sidebar_section_line
        color: accent
        case: uppercase
        rule_color: accent
        rule_length: "0.38\\linewidth"
        rule_gap_before: section_sidebar_gap_before
        rule_gap_after: section_sidebar_gap_after
```

## 9. Inheritance Rules

Macro variants inherit from `standard` automatically.

This means:

- keep `standard: {}` when defaults are already good
- override only the fields you want to change
- add reusable tokens to `sizes` or `rules` instead of repeating literal values everywhere

Example:

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
```

This does not replace the whole `cvname` definition. It only changes those three fields.

## 10. Customize an Existing Theme

The easiest workflow is to start from an existing theme.

### Step 1: duplicate a theme

```bash
cp themes/minimal.yaml themes/mytheme.yaml
```

### Step 2: change the basic palette

```yaml
colors:
  primary: "#1c1f26"
  accent: "#0b7fab"
  muted: "#68707a"
  rule: "#d4d9de"
```

### Step 3: adjust typography tokens

```yaml
sizes:
  name: "25pt"
  name_line: "29pt"
  section: "11pt"
  section_line: "13pt"
  body: "9.8pt"
  body_line: "12.8pt"
```

### Step 4: build it

```bash
uv run build.py --theme mytheme --layout twocol
```

## 11. Add a New Variant to an Existing Macro

Here is a full example that adds a new `caps` section-title style.

### Step 1: add tokens

```yaml
sizes:
  caps_section: "10.5pt"
  caps_section_line: "12.5pt"

rules:
  caps_gap_before: "3pt"
  caps_gap_after: "5pt"
```

### Step 2: add the variant

```yaml
macros:
  cvsectiontitle:
    default: standard
    variants:
      standard: {}
      caps:
        size: caps_section
        line: caps_section_line
        color: primary
        case: uppercase
        rule_color: primary
        rule_gap_before: caps_gap_before
        rule_gap_after: caps_gap_after
```

### Step 3: use it in the template

```tex
\cvsectiontitle[caps]{Projects}
```

### Step 4: build

```bash
uv run build.py --theme mytheme --layout single
```

## 12. Change the Template Layout

The template is in `templates/resume.tex.j2`.

It does two things:

- defines Jinja macros like `render_experience(items)`
- decides where each section goes depending on `layout`

Example from the current template:

```jinja
{% if layout == 'single' %}
{{ render_summary(summary) }}
{{ render_experience(experience) }}
{{ render_education(education) }}
{% elif layout == 'twocol' %}
\begin{paracol}{2}
{{ render_summary(summary) }}
{{ render_experience(experience) }}
\switchcolumn
{{ render_skills(skills) }}
{{ render_languages(languages | default([])) }}
\end{paracol}
{% endif %}
```

If you want a section in a different place, edit the template, not the theme.

Examples:

- move `Projects` earlier in the single-column layout
- use `\cventry[stacked]` for all publications
- use `\cvsectiontitle[sidebar]` only on the right column

## 13. Real Examples from the Current Template

The current `templates/resume.tex.j2` already demonstrates good variant usage.

### Header variants

```tex
\cvname[hero]{ ... }
\cvtitle[headline]{ ... }
\cvmeta{ ... }
\cvmeta[links]{ ... }
```

### Summary variant

```tex
\cvbody[lead]{ ... }
```

### Detail text variant

```tex
\cvsmall[detail]{ ... }
```

### Narrow-column skill variant

```tex
\cvskill[compact]{ ... }{ ... }
```

### Narrow-column section-title variant

```tex
\cvsectiontitle[sidebar]{Skills}
```

### Stacked entry variant

```tex
\cventry[stacked]{ ... }{ ... }{ ... }{ ... }
```

## 14. Create a Brand New Theme

Use this workflow.

### Step 1: copy an existing theme

```bash
cp themes/minimal.yaml themes/editorial.yaml
```

### Step 2: rename and tune tokens

You can keep the same structure and change values gradually:

- palette in `colors`
- typography in `sizes`
- spacing in `rules`
- visual styles in `macros`

### Step 3: keep macro signatures stable

Do not invent a new public macro name like `\cvbadge` unless you also change the template and generator architecture.

The intended customization path is:

- keep `\cvname`, `\cventry`, `\cvskill`, etc.
- add new named variants inside `macros`
- call them from the template when needed

### Step 4: build and iterate

```bash
uv run build.py --theme editorial --layout twocol
```

## 15. Use Tokens vs Literal Values

In general:

- use token names for reusable things
- use raw literal values only for one-off lengths or separators

Good examples:

```yaml
size: hero_name
line: hero_name_line
color: accent
rule_gap_after: section_sidebar_gap_after
```

Also valid when needed:

```yaml
rule_length: "0.42\\linewidth"
separator: " - "
bottom_gap: "3pt"
```

## 16. Validation Rules You Should Know

The builder fails early on invalid themes.

Common checks:

- `colors.*` must be hex colors like `#4a7c96`
- `macros` can only define known macro names
- each macro must have `default` and `variants`
- the default variant name must exist
- font references must exist in `fonts`
- color references must exist in `colors`
- layouts must be supported for that macro
- `rules.column_ratios` must contain exactly two positive numbers

This is helpful because most theme mistakes fail before LaTeX compilation starts.

## 17. Troubleshooting

### Unknown variant error

Example:

```tex
\cvsectiontitle[fancy]{Projects}
```

If `fancy` is not defined in the active theme, the build fails.

Fix:

- define `fancy` in `macros.cvsectiontitle.variants`
- or use an existing variant name

### Unknown color token

If you write:

```yaml
color: brand_blue
```

then `brand_blue` must exist in `colors`.

### Unsupported layout

These are the supported layout values:

- `cventry`: `standard`, `stacked`
- `cvskill`: `inline`, `stacked`
- `cvsectiontitle`: `standard`, `sidebar`

### Font issues

The current setup expects vendored fonts in `cv/fonts/` matching the configured families.

If you change font names, make sure the output build can actually resolve the font family and style files.

### LaTeX compile fails after theme validation passed

Then the issue is usually in:

- the template structure
- a raw literal LaTeX value such as `rule_length`
- a font resolution problem

Inspect:

- `out/resume.cls`
- `out/resume.tex`
- `out/resume.log`

## 18. Backward Compatibility

Themes do not strictly need a `macros` block.

If `macros` is missing, `build.py` generates `standard` variants automatically from the older top-level tokens.

That means you can migrate gradually:

1. keep only `colors`, `fonts`, `sizes`, `rules`
2. confirm the build still works
3. add `macros` later when you want named variants

## 19. Suggested Customization Workflow

This is the safest workflow for iterative design:

1. start from `themes/minimal.yaml`
2. change only `colors`
3. rebuild
4. change `sizes` and `rules`
5. rebuild
6. add one new macro variant, such as `cvsectiontitle.sidebar_alt`
7. use it in one place in `templates/resume.tex.j2`
8. rebuild
9. repeat

Do not change everything at once. Small steps make it much easier to understand what each tweak changes.

## 20. A Complete Example Theme Fragment

This is a compact but realistic example:

```yaml
colors:
  primary: "#20242b"
  accent: "#006d77"
  muted: "#68727d"
  rule: "#d7dcdf"

fonts:
  heading: "Roboto"
  body: "Roboto"
  mono: "Roboto"

sizes:
  name: "24pt"
  name_line: "28pt"
  hero_name: "27pt"
  hero_name_line: "31pt"
  title: "12pt"
  title_line: "15pt"
  section: "12pt"
  section_line: "14pt"
  sidebar_section: "10pt"
  sidebar_section_line: "12pt"
  body: "10pt"
  body_line: "13pt"
  small: "9pt"
  small_line: "11pt"
  margin_top: "1.5cm"
  margin_bottom: "1.5cm"
  margin_side: "1.8cm"

rules:
  section_rule_width: "0.4pt"
  section_spacing: "8pt"
  column_gap: "18pt"
  column_ratios: [0.36, 0.64]
  section_sidebar_gap_before: "4pt"
  section_sidebar_gap_after: "6pt"

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
        size: sidebar_section
        line: sidebar_section_line
        color: accent
        case: uppercase
        rule_color: accent
        rule_length: "0.38\\linewidth"
        rule_gap_before: section_sidebar_gap_before
        rule_gap_after: section_sidebar_gap_after
```

## 21. A Complete Example Template Fragment

```jinja
\cvname[hero]{ {{ meta.name | latex_escape }} }\\[4pt]
\cvtitle{ {{ meta.title | latex_escape }} }\\[4pt]
\cvmeta{ {{ meta.email }} ~|~ {{ meta.phone | latex_escape }} }\\

\cvsectiontitle[sidebar]{Skills}
{% for group in skills %}
\cvskill[compact]{ {{ group.category | latex_escape }} }{ {{ group['items'] | join(', ') | latex_escape }} }
{% endfor %}
```

## 22. Summary

Use this checklist:

- edit `data/resume.yaml` for content
- edit `themes/*.yaml` for visual tokens and variants
- edit `templates/resume.tex.j2` for layout and section ordering
- call `\cv*` macros with or without named variants
- build with `uv run build.py ...`

If you want a good starting point, copy `themes/minimal.yaml`, keep the same `macros` structure, and change one token group at a time.
