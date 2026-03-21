# CV Builder Redesign

## The roast: why the current system is broken

### The "independent variation" claim is false

The pitch is: swap a `.sty` for a different look, swap a `.tex` for a
different layout, swap JSON for different content. Three independent axes.
In practice, they are deeply coupled.

```
         ┌─────────────┐
         │    .cls      │
         │ geometry,    │
         │ fonts, base  │
         └──────┬───────┘
        assumes │ assumes
        geometry│ fonts
           ┌────┴─────┐
           ▼          ▼
    ┌────────────┐  ┌────────────┐
    │  .sty      │  │  .tex      │
    │ commands,  │──│ templates, │
    │ packages   │  │ structure  │
    └────────────┘  └────────────┘
          │               │
          └───────────────┘
          calls commands by name,
          assumes argument order,
          loads conflicting packages
```

Changing a `.sty` that renames `\cventry` or reorders its arguments breaks
every `.tex` template. Changing `.cls` page margins can blow up a two-column
`.sty` layout. You don't have independent axes — you have a fragile triangle
where touching one vertex cracks the other two.

### JSON data is a LaTeX minefield

You need a build step (Python? Node? Makefile?) that reads JSON and injects
it into LaTeX. That build step is an **unlisted fourth component** doing
heavy lifting while pretending not to exist.

```
   ┌──────────┐       ┌──────────────┐       ┌──────────┐
   │  JSON    │──???──│  ??? build   │──???──│   .tex   │
   │  data    │       │  ??? step    │       │ template │
   └──────────┘       └──────────────┘       └──────────┘

   Every &, %, #, $ in your JSON is a LaTeX bomb.
   Every conditional ("show this section only if data exists")
   means your build step reimplements half a programming language.
```

### Multiple `.sty` files misunderstand what a `.sty` is

A `.sty` file is not CSS. It defines commands, loads packages, sets lengths,
configures headers. Two different `.sty` files will inevitably:

- Define the same command differently
- Load conflicting packages (fontspec options, hyperref clashes)
- Assume different `.cls` internals

You're not "swapping themes." You're swapping entire rendering engines and
praying they're API-compatible.

### Two `.tex` templates is the start of a combinatorial explosion

Today: single-column and two-column. Tomorrow: two-column with sidebar,
single-column academic, single-column with photo. Each template duplicates
the logic for iterating over experiences, rendering education, showing
skills. You end up copy-pasting across templates and diverging silently.

```
   templates/
   ├── single-column.tex     ─┐
   ├── two-column.tex         │  same iteration logic
   ├── sidebar.tex            │  copy-pasted 4 times,
   └── academic.tex          ─┘  diverging silently
```

### The real question

What is the **actual variation** you need? Right now you've built a system
optimized for a flexibility you probably don't use, at the cost of
reliability you definitely need.


---


## The redesign

### Guiding principle

> One source of truth per concern. Zero hidden coupling.
> Data is data. Theme is data. Layout is a flag. LaTeX is generated.

### Architecture overview

```
                    ┌─────────────────────────────────────────────┐
  INPUT             │                 build.py                    │  OUTPUT
                    │           (~100 lines, no framework)        │
                    │                                             │
 ┌──────────┐      │  1. Validate    2. Render       3. Compile  │    ┌──────────┐
 │resume.   │─────▶│  data against   Jinja2 template  lualatex   │───▶│resume.pdf│
 │yaml      │      │  schema         with data+theme              │    └──────────┘
 └──────────┘      │                                             │
                   │       ▲               ▲                     │
 ┌──────────┐      │       │               │                     │
 │schema.   │──────│───────┘               │                     │
 │yaml      │      │                       │                     │
 └──────────┘      │                       │                     │
                   │                       │                     │
 ┌──────────┐      │                       │                     │
 │theme/    │──────│───────────────────────┘                     │
 │minimal.  │      │  colors, fonts, sizes                       │
 │yaml      │      │  injected as \newcommand                    │
 └──────────┘      │                                             │
                   │                                             │
 ┌──────────┐      │                                             │
 │--layout  │──────│──▶ selects Jinja2 block                     │
 │flag      │      │   (single | twocol)                         │
 └──────────┘      │                                             │
                    └─────────────────────────────────────────────┘
```

**One command. No ambiguity.**

```
python build.py --theme minimal --layout two-column
```


### File structure

```
cv-builder/
│
├── data/
│   └── resume.yaml            # all your content, one file
│
├── themes/
│   ├── minimal.yaml           # primary: "#333", font: "Helvetica" ...
│   ├── academic.yaml          # primary: "#1a1a1a", font: "EB Garamond" ...
│   └── bold.yaml              # primary: "#0066cc", font: "Montserrat" ...
│
├── templates/
│   └── resume.tex.j2          # single Jinja2 template, all layouts
│
├── schema.yaml                # validates resume.yaml
├── build.py                   # ~100 lines, the only executable
│
└── out/                       # everything here is generated
    ├── resume.cls             # generated from theme, never hand-edited
    ├── resume.tex             # generated from data + template
    └── resume.pdf             # final output
```

**Nine files total.** You can hold the entire system in your head.


---


## Detailed design of each component


### 1. `resume.yaml` — the single source of content

YAML over JSON because: comments, multiline strings, anchors for repeated
structures. No LaTeX in here. Ever. Raw text only.

```yaml
meta:
  name: "Jane Doe"
  title: "Senior Software Engineer"
  email: "jane@example.com"
  phone: "+33 6 12 34 56 78"
  location: "Paris, France"
  linkedin: "janedoe"
  github: "janedoe"

summary: >
  Backend engineer with 8 years building distributed systems.
  Focused on reliability, observability, and developer tooling.

experience:
  - company: "Acme Corp"
    role: "Senior Engineer"
    start: "2021-03"
    end: "present"
    highlights:
      - "Designed event-driven architecture handling 50k msg/sec"
      - "Reduced deployment time from 45min to 8min"

  - company: "Widgets Inc"
    role: "Software Engineer"
    start: "2018-06"
    end: "2021-02"
    highlights:
      - "Built real-time analytics pipeline on Kafka + Flink"

education:
  - institution: "École Polytechnique"
    degree: "MSc Computer Science"
    year: 2018

skills:
  - category: "Languages"
    items: ["Python", "Go", "Rust", "TypeScript"]
  - category: "Infrastructure"
    items: ["Kubernetes", "Terraform", "AWS", "GCP"]

languages:
  - name: "French"
    level: "Native"
  - name: "English"
    level: "Fluent"
```

**What this buys you:** no escaping disasters (`&` → `\&`), no bracket
hell, no "is this a LaTeX command or data" confusion. The build step
handles all escaping.


### 2. `schema.yaml` — catch typos before they reach LaTeX

A JSON Schema (in YAML format) that validates `resume.yaml`. Catches
missing fields, wrong types, bad date formats before lualatex ever runs.

```yaml
type: object
required: [meta, experience, education]
properties:
  meta:
    type: object
    required: [name, email]
    properties:
      name: { type: string, minLength: 1 }
      email: { type: string, format: email }
      phone: { type: string }
      location: { type: string }
  experience:
    type: array
    items:
      type: object
      required: [company, role, start]
      properties:
        company: { type: string }
        role: { type: string }
        start: { type: string, pattern: "^\\d{4}-\\d{2}$" }
        end: { type: string }
        highlights: { type: array, items: { type: string } }
```

Validated with one line in `build.py`:

```python
jsonschema.validate(data, schema)
```

**What this buys you:** a `"start": "March 2021"` blows up immediately
with a clear error instead of silently producing garbled LaTeX.


### 3. `themes/*.yaml` — styling as pure data

A theme is a bag of design tokens. Not a LaTeX package. Not code.
Just values.

```yaml
# themes/minimal.yaml
colors:
  primary: "#2d2d2d"
  accent: "#4a7c96"
  muted: "#777777"
  rule: "#cccccc"

fonts:
  heading: "Helvetica Neue"
  body: "Helvetica Neue"
  mono: "Fira Code"

sizes:
  name: "24pt"
  section: "12pt"
  body: "10pt"
  margin_top: "1.5cm"
  margin_side: "1.8cm"

rules:
  section_rule_width: "0.4pt"
  section_spacing: "8pt"
```

**Why this kills `.sty` files:**

```
  BEFORE (.sty)                        AFTER (theme.yaml)
  ┌──────────────────────┐             ┌──────────────────────┐
  │ \RequirePackage{...} │             │ primary: "#2d2d2d"   │
  │ \definecolor{...}    │             │ accent: "#4a7c96"    │
  │ \newcommand{\cv...}  │             │ heading: "Helvetica" │
  │ \renewcommand{...}   │             │ body_size: "10pt"    │
  │ \setlength{...}      │             └──────────────────────┘
  │ \pagestyle{...}      │                   │
  └──────────────────────┘                   │ no code
         │                                   │ no conflicts
         │ is CODE                           │ no package loads
         │ can conflict                      │ just values
         │ can break
         ▼
    fragile, opaque                     inert, obvious
```

No package conflicts. No command-name collisions. No "which `.sty` loads
`fontspec` with what options" nightmare. Two themes can never conflict
because they're just key-value pairs read by the same build step.


### 4. `templates/resume.tex.j2` — one template, all layouts

The single Jinja2 template owns all LaTeX. Layout is a block-level switch,
not a separate file.

```
  ┌──────────────────────────────────────────┐
  │  resume.tex.j2                           │
  │                                          │
  │  ┌─── preamble (shared) ───────────────┐ │
  │  │ \documentclass, \usepackage,        │ │
  │  │ \definecolor from theme,            │ │
  │  │ \newcommand from theme              │ │
  │  └────────────────────────────────────-┘ │
  │                                          │
  │  ┌─── macros (shared) ────────────────-┐ │
  │  │ \cventry, \skill, \sectionrule      │ │
  │  │ defined ONCE, used by all layouts   │ │
  │  └─────────────────────────────────────┘ │
  │                                          │
  │  ┌─── layout switch ──────────────────-┐ │
  │  │ {% if layout == "single" %}         │ │
  │  │   ... single column body ...        │ │
  │  │ {% elif layout == "twocol" %}       │ │
  │  │   \begin{minipage}...               │ │
  │  │   ... two column body ...           │ │
  │  │ {% endif %}                         │ │
  │  └─────────────────────────────────────┘ │
  │                                          │
  │  ┌─── sections (shared) ──────────────-┐ │
  │  │ {% macro render_experience(exp) %}  │ │
  │  │   \cventry{...}{...}               │ │
  │  │ {% endmacro %}                      │ │
  │  │                                     │ │
  │  │ {% macro render_skills(skills) %}   │ │
  │  │   ...                               │ │
  │  │ {% endmacro %}                      │ │
  │  └─────────────────────────────────────┘ │
  │                                          │
  └──────────────────────────────────────────┘
```

**Key insight:** the iteration logic (`for exp in experience`, `for skill
in skills`) is defined once as Jinja2 macros. The layout blocks call those
macros in different arrangements. Adding a new layout means adding one
`{% elif %}` block, not duplicating the entire template.

Skeleton of the actual template:

```jinja
\documentclass[{{ theme.sizes.body }}]{article}

% --- Theme-driven preamble ---
\usepackage[
  top={{ theme.sizes.margin_top }},
  left={{ theme.sizes.margin_side }},
  right={{ theme.sizes.margin_side }}
]{geometry}
\usepackage{fontspec}
\setmainfont{ {{- theme.fonts.body -}} }

\definecolor{primary}{HTML}{ {{- theme.colors.primary | replace("#","") -}} }
\definecolor{accent}{HTML}{ {{- theme.colors.accent | replace("#","") -}} }

% --- Shared macros (defined once) ---
\newcommand{\cventry}[4]{%
  {\bfseries #1} \hfill {\color{muted}#2}\\
  {\itshape #3} \hfill {\color{muted}#4}\\[2pt]
}
\newcommand{\sectionrule}{\color{rule}\rule{\linewidth}{ {{- theme.rules.section_rule_width -}} }}

% --- Jinja2 macros for section rendering ---
{% macro render_experience(items) %}
\section{Experience}
\sectionrule
{% for exp in items %}
\cventry
  { {{- exp.role | latex_escape -}} }
  { {{- exp.start -}} -- {{ exp.end | default("present") -}} }
  { {{- exp.company | latex_escape -}} }
  {}
{% for h in exp.highlights %}
  \textbullet~{{ h | latex_escape }}\\
{% endfor %}
\vspace{4pt}
{% endfor %}
{% endmacro %}

{% macro render_skills(items) %}
\section{Skills}
\sectionrule
{% for group in items %}
  {\bfseries {{ group.category | latex_escape }}:}
  {{ group.items | join(", ") | latex_escape }}\\
{% endfor %}
{% endmacro %}

\begin{document}

% --- Header ---
{\Huge\bfseries\color{primary} {{ meta.name | latex_escape }} }\\[4pt]
{{ meta.title | latex_escape }}\\
{{ meta.email }} | {{ meta.phone }}

\vspace{12pt}

% --- Layout switch ---
{% if layout == "single" %}
  {{ render_experience(experience) }}
  {{ render_skills(skills) }}
{% elif layout == "twocol" %}
  \begin{minipage}[t]{0.62\textwidth}
    {{ render_experience(experience) }}
  \end{minipage}\hfill
  \begin{minipage}[t]{0.33\textwidth}
    {{ render_skills(skills) }}
  \end{minipage}
{% endif %}

\end{document}
```


### 5. `build.py` — the only executable, ~100 lines

Does exactly three things. No magic. No framework.

```
  resume.yaml ──┐
                 │      ┌───────────────────────────────────┐
  schema.yaml ──┤      │  build.py                         │
                 ├─────▶│                                   │
  theme.yaml ───┤      │  Step 1: Validate                 │
                 │      │    jsonschema.validate(data)       │
  --layout ─────┘      │                                   │
                       │  Step 2: Render                   │
                       │    jinja2.render(template,        │──▶ out/resume.tex
                       │      data, theme, layout)         │
                       │                                   │
                       │  Step 3: Compile                  │
                       │    subprocess: lualatex            │──▶ out/resume.pdf
                       │                                   │
                       └───────────────────────────────────┘
```

The critical piece: a `latex_escape` Jinja2 filter.

```python
def latex_escape(text: str) -> str:
    """Escape all LaTeX special characters in user data."""
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text
```

This filter is registered once in Jinja2 and applied to every piece of
user data in the template. No more LaTeX bombs from JSON.


---


## Variation axes: how they actually stay independent

```
  ┌──────────────────────────────────────────────────────────┐
  │                   VARIATION MATRIX                       │
  │                                                          │
  │   Axis        │  What changes       │  What doesn't      │
  │  ─────────────┼─────────────────────┼──────────────────  │
  │  Content      │  resume.yaml        │  everything else   │
  │  Theme        │  themes/X.yaml      │  everything else   │
  │  Layout       │  --layout flag      │  everything else   │
  │                                                          │
  │   Each axis is a single file or flag.                    │
  │   No axis knows the other exists.                        │
  │   The template consumes all three through Jinja2.        │
  └──────────────────────────────────────────────────────────┘
```

Test it yourself:

```
  python build.py --theme minimal  --layout single     # combo 1
  python build.py --theme bold     --layout single     # combo 2
  python build.py --theme minimal  --layout twocol     # combo 3
  python build.py --theme academic --layout twocol     # combo 4
```

Four PDFs. Zero file edits between runs. That's real independence.


---


## Adding a new variation

### New theme

Create `themes/modern.yaml`. Done.

```
  themes/
  ├── minimal.yaml
  ├── academic.yaml
  ├── bold.yaml
  └── modern.yaml    ← add 15 lines of YAML
```

No `.sty` to write. No packages to debug. No commands to define.


### New layout

Add one `{% elif %}` block in `resume.tex.j2`.

```
  BEFORE                              AFTER
  ┌──────────────────────┐            ┌──────────────────────┐
  │ {% if single %}      │            │ {% if single %}      │
  │   ...                │            │   ...                │
  │ {% elif twocol %}    │            │ {% elif twocol %}    │
  │   ...                │            │   ...                │
  │ {% endif %}          │            │ {% elif sidebar %}   │
  └──────────────────────┘            │   ... ← new block   │
                                      │ {% endif %}          │
                                      └──────────────────────┘
```

The Jinja2 macros (`render_experience`, `render_skills`) don't change.
The new block just calls them in a different arrangement.


### New section

1. Add data to `resume.yaml` (e.g., `publications:`)
2. Add validation to `schema.yaml`
3. Add one Jinja2 macro in the template
4. Call the macro from each layout block

```
  resume.yaml          schema.yaml          resume.tex.j2
  ┌─────────────┐      ┌──────────────┐     ┌─────────────────────┐
  │publications:│      │publications: │     │{% macro render_     │
  │  - title:   │      │  type: array │     │   publications() %} │
  │    ...      │      │  items: ...  │     │  \section{...}      │
  └─────────────┘      └──────────────┘     │  {% for p in ... %} │
                                            │    ...               │
                                            │  {% endfor %}        │
                                            │{% endmacro %}        │
                                            └─────────────────────┘
```


---


## What got killed and why

```
  KILLED                       WHY                          REPLACED BY
  ──────────────────────────────────────────────────────────────────────
  .sty files (all of them)     Code disguised as config.    theme.yaml
                               Source of every conflict.    (pure data)

  .cls (hand-maintained)       Coupled to .sty and .tex.    Generated by
                               Changes break everything.   build.py from
                                                            theme tokens.

  Multiple .tex templates      Duplicated logic.            One .tex.j2
                               Diverge silently.            with layout
                               Copy-paste breeding ground.  blocks.

  JSON data files              No comments, no multiline,   resume.yaml
                               special chars are bombs.

  Hidden build step            Undocumented, fragile.       build.py
                               Nobody knows it exists.      explicit, ~100
                                                            lines, the only
                                                            executable.
```


---


## Migration path

You don't have to rewrite everything at once. Here's the order:

```
  Step 1                Step 2                Step 3
  ──────────────        ──────────────        ──────────────
  JSON → YAML           .sty → theme.yaml     Multiple .tex
  + add schema          + generate .cls        → single .tex.j2
  + add build.py        from tokens
  (keep .sty/.tex       (keep .tex files       (final state,
   as-is for now)        as-is for now)         everything clean)

  Effort: 1 hour        Effort: 2-3 hours     Effort: 2-3 hours
  Risk: zero             Risk: low             Risk: medium
```

Each step produces a working system. You can stop at any step and still
be better off than where you started.
