# Dynamic LaTeX CV Generation System

A data-driven CV generation system that separates content (JSON) from presentation (LaTeX), enabling multiple CV variants from a single data source.

## Quick Start

### Build Your CV

```bash
# Build academic CV
python build.py academic
# or
make academic

# Build industry CV
python build.py industry
# or
make industry

# Build all variants
python build.py all
# or
make all
```

The generated PDFs will be in:
- `build/academic/resume.pdf`
- `build/industry/resume.pdf`

### Clean Build Artifacts

```bash
make clean
```

## Project Structure

```
curriculum_vitae/
├── data/                       # Your CV content (JSON files)
│   ├── contact.json           # Contact information
│   ├── skills.json            # Skills by category
│   ├── experience.json        # Work history
│   ├── education.json         # Degrees and awards
│   ├── papers.json            # Publications
│   ├── activities.json        # Activities
│   ├── objective.json         # Academic objective (optional)
│   └── summary.json           # Industry summary (optional; falls back to objective)
│
├── config/                     # CV variant configurations
│   ├── academic.json          # Academic CV (education first, includes papers)
│   └── industry.json          # Industry CV (skills first, no papers)
│
├── scripts/                    # Generation scripts (don't modify)
│   ├── generate_cv.py
│   ├── latex_escaper.py
│   ├── section_generators.py
│   ├── unified_generators.py
│   └── config_loader.py
│
├── cv_unified/                  # Unified LaTeX engine + switchable styles
│   ├── resume_academic.tex     # Academic wrapper (TLC-like look)
│   ├── resume_industry.tex     # Industry wrapper (Awesome-inspired look)
│   ├── cv_core.sty
│   ├── cv_style_academic.sty
│   ├── cv_style_industry.sty
│   ├── TLCresume.sty           # Vendored dependency (academic)
│   ├── fonts/                  # Vendored fonts (industry)
│   └── profile.png             # Optional photo (industry)
│
├── build/                      # Generated files (gitignored)
│   ├── academic/              # Academic variant output
│   └── industry/              # Industry variant output
│
├── build.py                    # Main build script
├── Makefile                    # Convenience commands
└── README.md                   # This file
```

## Editing Your CV

### Template-driven main files

The build copies a variant-specific LaTeX wrapper into `build/<variant>/resume.tex` and replaces tokens in the main file and any included files.

Default variants use the unified engine + unified markup:

- Academic: `cv_unified/resume_academic.tex`
- Industry: `cv_unified/resume_industry.tex`

- `{{FOOTER_CENTER}}`: footer text (uses your name)

Section order comes from the `\input{...}` lines in the template itself. Any `\input` file whose name matches a JSON-backed section is generated into that exact path; other `\input` files are copied as-is from the template directory.
`config/*.json` section lists are ignored in favor of the template order.

### 1. Update Contact Information

Edit `data/contact.json`:

```json
{
  "name": "Your Name",
  "role": "Your Title",
  "phone": "+1 234 567 8900",
  "city": "Your City, Country",
  "email": "your.email@example.com",
  "linkedin": "your-linkedin-username",
  "github": "your-github-username",
  "portfolio": {
    "url": "https://your-website.com",
    "display_name": "your-website.com"
  }
}
```

### 2. Update Skills

Edit `data/skills.json`:

```json
{
  "skills": [
    {
      "category": "Programming Languages",
      "items": "Python, JavaScript, Go, Rust"
    },
    {
      "category": "Frameworks",
      "items": "React, Django, FastAPI"
    }
  ]
}
```

### 3. Update Experience

Edit `data/experience.json`:

```json
{
  "experiences": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Company",
      "location": "San Francisco, CA",
      "start_date": "Jan 2020",
      "end_date": "Present",
      "bullets": [
        "Led development of microservices architecture",
        "Improved system performance by 50%",
        "Mentored 5 junior developers"
      ]
    }
  ]
}
```

### 4. Update Education

Edit `data/education.json`:

```json
{
  "degrees": [
    {
      "degree": "PhD in Computer Science",
      "institution": "University Name",
      "location": "City, Country",
      "date": "2018 --- 2022",
      "details": "Specialization in Machine Learning"
    }
  ],
  "awards": [
    {
      "title": "Best Paper Award",
      "organization": "Conference Name",
      "date": "2021"
    }
  ]
}
```

### 5. Update Publications

Edit `data/papers.json`:

```json
{
  "papers": [
    {
      "title": "Your Paper Title",
      "authors": "You, Co-Author 1, Co-Author 2",
      "venue": "Conference/Journal Name",
      "year": 2024,
      "status": "published",
      "url": "https://arxiv.org/abs/xxxx.xxxxx"
    }
  ]
}
```

## Creating Custom CV Variants

To create a new variant (e.g., `short.json`):

1. Copy an existing config file:
   ```bash
   cp config/academic.json config/short.json
   ```

2. Edit the new config:
   - Change `variant` name
   - Change `output_dir` to `build/short`
   - Enable/disable sections as needed
   - Reorder sections

3. Add to `build.py`:
   ```python
   CONFIGS = {
       'academic': 'config/academic.json',
       'industry': 'config/industry.json',
       'short': 'config/short.json'  # Add this line
   }
   ```

4. Build your new variant:
   ```bash
   python build.py short
   ```

## Features

### Automatic LaTeX Escaping

Special characters (`&`, `%`, `_`, `#`, etc.) are automatically escaped. You can write:
- "R&D Engineer" → renders correctly as "R\&D Engineer"
- "Improved performance by 50%" → renders correctly
- URLs and emails are NOT escaped

### Modular Sections

Each section is stored in a separate JSON file, allowing:
- Easy editing of specific sections
- Selective inclusion in different CV variants
- Clear separation of concerns

### Multiple Variants

- Academic CV: Education first, includes publications and activities
- Industry CV: Skills first, excludes academic sections

## Troubleshooting

### LaTeX Compilation Errors

If you see errors during PDF generation:

1. Check the log file:
   ```bash
   cat build/academic/resume.log
   ```

2. Manually compile to see full errors:
   ```bash
   cd build/academic
   latexmk -pdf resume.tex
   ```

3. Common issues:
   - Missing LaTeX packages: Install TexLive full distribution
   - Special characters: Should be auto-escaped, but check your JSON
   - Missing data: Ensure all required JSON files exist

### Python Errors

If the script fails:

1. Check Python version (requires Python 3.7+):
   ```bash
   python3 --version
   ```

2. Verify file structure:
   ```bash
   ls -la data/ config/ scripts/
   ```

## Requirements

- Python 3.7+
- LaTeX distribution (TexLive 2020+ recommended)
  - Ubuntu/Debian: `sudo apt-get install texlive-full`
  - macOS: `brew install --cask mactex`
- latexmk (usually included with LaTeX distribution)

## License

The LaTeX template (TLCresume) is from Overleaf and maintains its original license.
The Python generation system is provided as-is for your personal use.
