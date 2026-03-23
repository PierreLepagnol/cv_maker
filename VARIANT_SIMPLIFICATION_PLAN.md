# Variant Simplification Checklist

## Goal

Simplify the macro variant system so it is easier to understand, more consistent, and safer to evolve, while keeping old variant names working for one transition cycle.

The main rule going forward is:

- variants describe visual rendering only
- section semantics stay in the template
- spacing stays in theme tokens and layout rules

## Target Design

Use a small canonical variant set for each macro:

- `cventry`: `standard`, `inline`, `stacked`
- `cvskill`: `inline`, `stacked`
- `cvsectiontitle`: `standard`, `sidebar`

Deprecated names remain temporarily as compatibility aliases:

- `experience` -> `standard`
- `education` -> `standard`
- `project` -> `stacked`
- `publication` -> `inline`
- `compact` -> canonical equivalent depending on macro
- `inline_compact` -> `inline`

## Definition of Done

- `templates/resume.tex.j2` uses only canonical variant names
- `themes/_base.yaml` defines only canonical variants as real implementations
- deprecated names still compile through an explicit alias layer in `build.py`
- `README.md` and `TUTORIAL.md` teach only canonical names
- `twocol` and `twocol-footer` use the same sidebar-related variant logic where intended
- generated PDFs remain visually stable, or changes are explicitly accepted

## Current Problems

The current system mixes several concepts inside the same "variant" namespace:

- semantic names like `publication`, `project`, `experience`
- visual layout names like `inline`, `stacked`, `sidebar`
- density or spacing names like `compact`, `inline_compact`

This creates several issues:

- the same concept is expressed in different ways
- some names hide behavior instead of describing it
- template code depends on theme-internal naming choices
- some variants duplicate each other with little or no real difference
- layout-specific logic is inconsistent between `twocol` and `twocol-footer`

## Rules to Keep

1. Keep variants visual, not semantic.
2. Keep section meaning in `templates/resume.tex.j2`.
3. Keep spacing in theme `rules` and reusable tokens.
4. Preserve backward compatibility for one transition cycle.
5. Make canonical names the only names shown in docs and examples.

## Concrete Implementation Checklist

### 1. Add canonical and alias maps in `build.py`

- [x] Add one explicit alias map near the macro-variant normalization code in `build.py`
- [x] Keep alias mapping per macro, not global, so names stay unambiguous
- [x] Use this initial mapping:
  - [x] `cventry.experience` -> `standard`
  - [x] `cventry.education` -> `standard`
  - [x] `cventry.project` -> `stacked`
  - [x] `cventry.publication` -> `inline`
  - [x] `cventry.inline_compact` -> `inline`
  - [x] `cvskill.compact` -> `stacked`
- [x] Keep canonical variants as the source of truth
- [x] Synthesize deprecated aliases from canonical variants during normalization
- [x] Do not add warnings yet; keep compatibility silent for this migration

### 2. Keep validation strict and predictable in `build.py`

- [x] Validate only supported layouts for the canonical behavior:
  - [x] `cventry`: `standard`, `inline`, `stacked`
  - [x] `cvskill`: `inline`, `stacked`
  - [x] `cvsectiontitle`: `standard`, `sidebar`
- [x] Ensure alias-expanded variants still pass existing field validation
- [ ] Confirm unknown variant names still fail with a clear error
- [x] Keep the dispatcher architecture unchanged

### 3. Simplify real variant definitions in `themes/_base.yaml`

- [x] Reduce `cventry` real definitions to `standard`, `inline`, `stacked`
- [x] Remove semantic first-class definitions like `experience`, `education`, `project`, `publication`
- [x] Remove density-style first-class definitions like `compact`, `inline_compact`
- [x] Reduce `cvskill` real definitions to `inline`, `stacked`
- [x] Keep `cvsectiontitle` real definitions as `standard`, `sidebar`
- [x] Preserve current appearance by moving any needed spacing differences into `rules` or reusable tokens
- [ ] If necessary, add or rename spacing tokens so layout choices remain readable

### 4. Normalize default choices in `themes/_base.yaml`

- [x] Decide whether `cvskill.default` should become `inline` instead of `standard`
- [x] Decide whether any macro should keep `default: standard` for readability
- [x] Prefer defaults that match actual layout names when possible
- [x] Keep defaults stable unless the template change makes the intent clearer

### 5. Update template calls in `templates/resume.tex.j2`

- [x] Replace semantic `cventry` calls with canonical visual names:
  - [x] `\cventry[experience]` -> `\cventry[standard]`
  - [x] `\cventry[education]` -> `\cventry[standard]`
  - [x] `\cventry[publication]` -> `\cventry[inline]`
  - [x] `\cventry[project]` -> `\cventry[stacked]`
- [x] Replace `\cvskill[compact]` with `\cvskill[stacked]`
- [x] Keep `\cvsectiontitle[standard]` and `\cvsectiontitle[sidebar]` as the only section-title choices in the template
- [x] Keep header and text variants like `hero`, `headline`, `links`, `lead`, `detail` unchanged unless a separate cleanup is planned later

### 6. Fix layout condition handling in `templates/resume.tex.j2`

- [x] Introduce one shared condition for two-column layouts, for example: `layout in ['twocol', 'twocol-footer']`
- [x] Use that condition everywhere section-title and skill variants depend on sidebar/two-column behavior
- [x] Verify `twocol-footer` now uses the same sidebar variant selection as `twocol` where appropriate

### 7. Update `README.md`

- [x] Replace examples that teach deprecated names with canonical names
- [x] Keep the explanation that optional macro variants exist
- [x] Add a short migration note with alias replacements
- [x] Make sure `README.md` no longer presents `compact`, `publication`, or `inline_compact` as first-class choices

### 8. Update `TUTORIAL.md`

- [x] Rewrite examples so `cventry` uses `standard`, `inline`, `stacked`
- [x] Rewrite examples so `cvskill` uses `inline`, `stacked`
- [x] Replace any narrative that treats `publication`, `compact`, or `inline_compact` as real recommended variants
- [x] Add one migration table from deprecated aliases to canonical names
- [x] Keep the explanation that variants inherit from the base canonical style

### 9. Verify generated output

- [x] Build at least these outputs after the refactor:
  - [x] `uv run build.py academic`
  - [x] `uv run build.py industry`
  - [x] `uv run build.py sciam`
- [x] Confirm the build completes without variant-related errors
- [ ] Visually inspect publications, projects, education, skills, and section titles
- [x] Compare `twocol` and `twocol-footer` behavior specifically
- [x] Confirm deprecated aliases still work if referenced manually in the template or a theme

### 10. Optional cleanup after the transition window

- [ ] Remove deprecated aliases from the compatibility map
- [ ] Remove migration notes from docs once no longer needed
- [ ] Keep only canonical examples everywhere

## Suggested Implementation Order

1. Update `build.py`
2. Simplify `themes/_base.yaml`
3. Update `templates/resume.tex.j2`
4. Update `README.md`
5. Update `TUTORIAL.md`
6. Build and visually verify outputs

## Notes During Implementation

- Keep the alias layer explicit and small.
- Do not mix semantic section names back into canonical variants.
- Prefer moving spacing differences into theme tokens instead of inventing new variant names.
- If a visual regression appears, preserve output first and simplify structure second.

## Acceptance Criteria

- template code uses canonical variant names only
- docs teach canonical names only
- deprecated names still work during the migration window
- `twocol-footer` follows the same variant-selection logic as `twocol` where expected
- output remains visually stable or changes only in intentional ways

## Main Risks

- some deprecated variants currently bundle layout and spacing together
- replacing names without preserving spacing may subtly change PDF rhythm
- too much hidden alias logic could keep the system confusing

To reduce risk:

- keep alias handling explicit and small
- preserve appearance first
- move spacing concerns out of semantic variants incrementally

## Recommendation

Keep deprecated aliases silent for now.

That gives a smooth migration path, keeps builds clean, and lets the project standardize on the simpler canonical model without breaking existing usage immediately.
