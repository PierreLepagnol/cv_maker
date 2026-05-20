#!/usr/bin/env python3
"""Build a CV from YAML data, YAML theme, and one Jinja2 template."""

from __future__ import annotations

import argparse
import copy
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined
from jsonschema import validate

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "resume.yaml"
SCHEMA_PATH = ROOT / "schema.yaml"
THEME_SCHEMA_PATH = ROOT / "theme-schema.yaml"
THEMES_DIR = ROOT / "themes"
BASE_THEME_PATH = THEMES_DIR / "_base.yaml"
TEMPLATE_PATH = ROOT / "templates" / "resume.tex.j2"
OUTPUT_DIR = ROOT / "out"
CV_DIR = ROOT / "cv"

VARIANTS = {
    "academic": ("academic", "single"),
    "industry": ("minimal", "twocol"),
    "industry-footer": ("minimal", "twocol-footer"),
    "sciam": ("bold", "twocol"),
}
_LAYOUT_ALIASES = {"two-column": "twocol", "two-column-footer": "twocol-footer"}
LATEX_ESCAPES = {
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
MACRO_ARITIES = {
    "cvname": 1,
    "cvtitle": 1,
    "cvmeta": 1,
    "cvbody": 1,
    "cvsmall": 1,
    "cventry": 4,
    "cvskill": 2,
    "cvsectiontitle": 1,
}
TEXT_MACRO_VARIANTS = {
    "cvname": {
        "font": "heading",
        "size": "name",
        "line": "name_line",
        "color": "primary",
        "weight": "bold",
        "shape": "normal",
        "case": "normal",
    },
    "cvtitle": {
        "font": "body",
        "size": "title",
        "line": "title_line",
        "color": "accent",
        "weight": "normal",
        "shape": "normal",
        "case": "normal",
    },
    "cvmeta": {
        "font": "body",
        "size": "body",
        "line": "body_line",
        "color": "muted",
        "weight": "normal",
        "shape": "normal",
        "case": "normal",
    },
    "cvbody": {
        "font": "body",
        "size": "body",
        "line": "body_line",
        "color": None,
        "weight": "normal",
        "shape": "normal",
        "case": "normal",
    },
    "cvsmall": {
        "font": "body",
        "size": "small",
        "line": "small_line",
        "color": None,
        "weight": "normal",
        "shape": "normal",
        "case": "normal",
    },
}
STYLE_LAYOUT_MACRO_STYLES = {
    "cventry": {
        "font": "body",
        "size": "body",
        "line": "body_line",
        "meta_size": "small",
        "meta_line": "small_line",
        "line1_left_weight": "bold",
        "line1_left_shape": "normal",
        "line1_left_color": None,
        "line1_right_weight": "normal",
        "line1_right_shape": "normal",
        "line1_right_color": "primary",
        "line2_left_weight": "normal",
        "line2_left_shape": "italic",
        "line2_left_color": None,
        "line2_right_weight": "normal",
        "line2_right_shape": "normal",
        "line2_right_color": "muted",
        "meta_color": "muted",
    },
    "cvskill": {
        "font": "body",
        "size": "body",
        "line": "body_line",
        "label_weight": "bold",
        "label_color": None,
        "value_color": None,
        "separator": ": ",
    },
    "cvsectiontitle": {
        "font": "heading",
        "size": "section",
        "line": "section_line",
        "color": "primary",
        "weight": "bold",
        "shape": "normal",
        "case": "normal",
        "rule_enabled": True,
        "rule_color": "rule",
        "rule_width": "section_rule_width",
        "rule_length": r"\linewidth",
    },
}
STYLE_LAYOUT_MACRO_LAYOUTS = {
    "cventry": {
        "standard": {
            "mode": "standard",
            "line_gap": "tight_spacing",
            "bottom_gap": "entry_gap",
            "bottom_mode": "linebreak",
        },
        "inline": {
            "mode": "inline",
            "line_gap": "tight_spacing",
            "bottom_gap": "entry_gap",
            "bottom_mode": "linebreak",
        },
        "inline_left": {
            "mode": "inline_left",
            "line_gap": "tight_spacing",
            "bottom_gap": "entry_gap",
            "bottom_mode": "linebreak",
        },
        "stacked": {
            "mode": "stacked",
            "line_gap": "project_spacing",
            "bottom_gap": "entry_gap",
            "bottom_mode": "linebreak",
        },
    },
    "cvskill": {
        "inline": {"mode": "inline", "stack_gap": "tight_spacing"},
        "stacked": {"mode": "stacked", "stack_gap": "stack_gap"},
    },
    "cvsectiontitle": {
        "standard": {
            "mode": "standard",
            "rule_gap_before": "section_rule_gap",
            "rule_gap_after": "section_spacing",
        },
        "sidebar": {
            "mode": "sidebar",
            "rule_gap_before": "sidebar_rule_gap",
            "rule_gap_after": "sidebar_spacing",
        },
    },
}
TEXT_MACRO_DEFAULT_VARIANT_NAMES = {name: "standard" for name in TEXT_MACRO_VARIANTS}
STYLE_LAYOUT_DEFAULT_STYLE_NAME = "base"
STYLE_LAYOUT_DEFAULT_LAYOUT_NAMES = {
    "cventry": "standard",
    "cvskill": "inline",
    "cvsectiontitle": "standard",
}
_WEIGHT_VALUES = {"normal", "bold"}
_SHAPE_VALUES = {"normal", "italic", "slanted"}
STYLE_FIELD_ENUMS = {
    "weight": _WEIGHT_VALUES,
    "label_weight": _WEIGHT_VALUES,
    "line1_left_weight": _WEIGHT_VALUES,
    "line1_right_weight": _WEIGHT_VALUES,
    "line2_left_weight": _WEIGHT_VALUES,
    "line2_right_weight": _WEIGHT_VALUES,
    "shape": _SHAPE_VALUES,
    "line1_left_shape": _SHAPE_VALUES,
    "line1_right_shape": _SHAPE_VALUES,
    "line2_left_shape": _SHAPE_VALUES,
    "line2_right_shape": _SHAPE_VALUES,
    "case": {"normal", "uppercase", "smallcaps"},
}
LAYOUT_FIELD_ENUMS = {
    "bottom_mode": {"linebreak", "paragraph"},
}
LAYOUT_MODE_VALUES = {
    "cventry": {"standard", "stacked", "inline", "inline_left"},
    "cvskill": {"inline", "stacked"},
    "cvsectiontitle": {"standard", "sidebar"},
}
COLOR_REF_FIELDS = {
    "color",
    "rule_color",
    "line1_left_color",
    "line1_right_color",
    "line2_left_color",
    "line2_right_color",
    "meta_color",
    "label_color",
    "value_color",
}
TEXT_MACRO_ALLOWED_KEYS = {
    name: set(fields) for name, fields in TEXT_MACRO_VARIANTS.items()
}
STYLE_LAYOUT_STYLE_KEYS = {
    name: set(fields) for name, fields in STYLE_LAYOUT_MACRO_STYLES.items()
}
STYLE_LAYOUT_LAYOUT_KEYS = {
    name: set(next(iter(layouts.values())))
    for name, layouts in STYLE_LAYOUT_MACRO_LAYOUTS.items()
}


def latex_escape(text: str) -> str:
    """Escape LaTeX special characters in user data."""
    value = "" if text is None else str(text)
    for char, escaped in LATEX_ESCAPES.items():
        value = value.replace(char, escaped)
    return value.strip()


def md_to_latex(text: str) -> str:
    """Convert a subset of Markdown to LaTeX (currently: **bold**)."""
    value = latex_escape(text)
    value = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", value)
    return value


def latex_href(url: str, label: str) -> str:
    return f"\\href{{{url}}}{{{latex_escape(label)}}}"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def normalize_layout(layout: str) -> str:
    result = _LAYOUT_ALIASES.get(layout, layout)
    if result not in {"single", "twocol", "twocol-footer"}:
        raise ValueError(
            f"Unknown layout {layout!r}. Expected: single, twocol, two-column"
        )
    return result


def resolve_args(args: argparse.Namespace) -> tuple[str, str, Path]:
    if args.variant:
        if args.variant not in VARIANTS:
            known = ", ".join(sorted(VARIANTS))
            raise ValueError(
                f"Unknown variant {args.variant!r}. Expected one of: {known}"
            )
        theme, layout = VARIANTS[args.variant]
    else:
        if not args.theme or not args.layout:
            raise ValueError("Pass either a variant or both --theme and --layout")
        theme = args.theme
        layout = args.layout
    return theme, normalize_layout(layout), args.output_dir


def latex_column_ratio(theme: dict) -> str:
    ratios = theme.get("rules", {}).get("column_ratios")
    if not ratios:
        return ""
    if not isinstance(ratios, list) or len(ratios) != 2:
        raise ValueError(
            "theme.rules.column_ratios must be a list of exactly two values"
        )
    if any(float(ratio) <= 0 for ratio in ratios):
        raise ValueError("theme.rules.column_ratios values must be positive")
    joined = ",".join(str(ratio) for ratio in ratios)
    return f"\\columnratio{{{joined}}}"


def merge_dicts(base: dict, override: dict) -> dict:
    merged = base.copy()
    merged.update(override)
    return merged


def merge_nested_dicts(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = merge_nested_dicts(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def normalize_text_macro(macro_name: str, macro_config: dict) -> dict:
    raw_variants = macro_config.get("variants", {})
    base_variant = TEXT_MACRO_VARIANTS[macro_name]
    base_variant_name = TEXT_MACRO_DEFAULT_VARIANT_NAMES[macro_name]
    base_input = merge_dicts(base_variant, raw_variants.get(base_variant_name, {}))
    variants = {base_variant_name: base_input}
    for variant_name, variant_values in raw_variants.items():
        if variant_name == base_variant_name:
            continue
        variants[variant_name] = merge_dicts(base_input, variant_values)
    return {
        "default": macro_config.get("default", base_variant_name),
        "variants": variants,
    }


def resolve_layout_config(macro_name: str, layout_name: str, layout: dict) -> dict:
    mode = layout.get("mode")
    if mode is None:
        raise ValueError(f"Missing {macro_name}.{layout_name}.mode")
    if mode not in LAYOUT_MODE_VALUES[macro_name]:
        known = ", ".join(sorted(LAYOUT_MODE_VALUES[macro_name]))
        raise ValueError(
            f"Unsupported {macro_name} mode {mode!r} for {layout_name}. "
            f"Expected one of: {known}"
        )
    return merge_dicts(STYLE_LAYOUT_MACRO_LAYOUTS[macro_name][mode], layout)


def normalize_style_layout_macro(macro_name: str, macro_config: dict) -> dict:
    raw_styles = macro_config.get("styles", {})
    raw_layouts = macro_config.get("layouts", {})

    base_style = STYLE_LAYOUT_MACRO_STYLES[macro_name]
    base_input = merge_dicts(
        base_style, raw_styles.get(STYLE_LAYOUT_DEFAULT_STYLE_NAME, {})
    )
    styles = {STYLE_LAYOUT_DEFAULT_STYLE_NAME: base_input}
    for style_name, style_values in raw_styles.items():
        if style_name == STYLE_LAYOUT_DEFAULT_STYLE_NAME:
            continue
        styles[style_name] = merge_dicts(base_input, style_values)

    layouts = {}
    for layout_name, base_layout in STYLE_LAYOUT_MACRO_LAYOUTS[macro_name].items():
        layout_input = merge_dicts(base_layout, raw_layouts.get(layout_name, {}))
        layouts[layout_name] = resolve_layout_config(
            macro_name, layout_name, layout_input
        )
    for layout_name, layout_values in raw_layouts.items():
        if layout_name in layouts:
            continue
        layouts[layout_name] = resolve_layout_config(
            macro_name, layout_name, layout_values
        )

    return {
        "default_style": macro_config.get(
            "default_style", STYLE_LAYOUT_DEFAULT_STYLE_NAME
        ),
        "default_layout": macro_config.get(
            "default_layout", STYLE_LAYOUT_DEFAULT_LAYOUT_NAMES[macro_name]
        ),
        "styles": styles,
        "layouts": layouts,
    }


def normalize_theme(theme: dict) -> dict:
    normalized = copy.deepcopy(theme)
    macros = normalized.setdefault("macros", {})

    for macro_name in TEXT_MACRO_VARIANTS:
        macro_config = copy.deepcopy(macros.get(macro_name, {}))
        macros[macro_name] = normalize_text_macro(macro_name, macro_config)

    for macro_name in STYLE_LAYOUT_MACRO_STYLES:
        macro_config = copy.deepcopy(macros.get(macro_name, {}))
        macros[macro_name] = normalize_style_layout_macro(macro_name, macro_config)

    return normalized


def validate_common_field(
    theme: dict, owner: str, field_name: str, value: str | bool | None
) -> None:
    if field_name == "font":
        if value not in theme["fonts"]:
            known = ", ".join(sorted(theme["fonts"]))
            raise ValueError(
                f"Unknown font token for {owner}.{field_name}: {value!r}. "
                f"Expected one of: {known}"
            )
        return

    if field_name in COLOR_REF_FIELDS:
        if value is not None and value not in theme["colors"]:
            known = ", ".join(sorted(theme["colors"]))
            raise ValueError(
                f"Unknown color token for {owner}.{field_name}: {value!r}. "
                f"Expected one of: {known}"
            )
        return

    if field_name == "rule_enabled":
        if not isinstance(value, bool):
            raise ValueError(f"Expected boolean for {owner}.{field_name}")
        return

    if not isinstance(value, str):
        raise ValueError(f"Expected string for {owner}.{field_name}")


def validate_text_variant_fields(
    theme: dict, macro_name: str, variant_name: str, variant: dict
) -> None:
    allowed_keys = TEXT_MACRO_ALLOWED_KEYS[macro_name]
    unknown_keys = sorted(set(variant) - allowed_keys)
    if unknown_keys:
        joined = ", ".join(unknown_keys)
        raise ValueError(f"Unknown {macro_name}.{variant_name} fields: {joined}")

    owner = f"{macro_name}.{variant_name}"
    for field_name, value in variant.items():
        if field_name in STYLE_FIELD_ENUMS:
            if value not in STYLE_FIELD_ENUMS[field_name]:
                known = ", ".join(sorted(STYLE_FIELD_ENUMS[field_name]))
                raise ValueError(
                    f"Invalid {owner}.{field_name}: {value!r}. Expected one of: {known}"
                )
            continue
        validate_common_field(theme, owner, field_name, value)


def validate_style_fields(
    theme: dict, macro_name: str, style_name: str, style: dict
) -> None:
    allowed_keys = STYLE_LAYOUT_STYLE_KEYS[macro_name]
    unknown_keys = sorted(set(style) - allowed_keys)
    if unknown_keys:
        joined = ", ".join(unknown_keys)
        raise ValueError(f"Unknown {macro_name}.styles.{style_name} fields: {joined}")

    owner = f"{macro_name}.styles.{style_name}"
    for field_name, value in style.items():
        if field_name in STYLE_FIELD_ENUMS:
            if value not in STYLE_FIELD_ENUMS[field_name]:
                known = ", ".join(sorted(STYLE_FIELD_ENUMS[field_name]))
                raise ValueError(
                    f"Invalid {owner}.{field_name}: {value!r}. Expected one of: {known}"
                )
            continue
        validate_common_field(theme, owner, field_name, value)


def validate_layout_fields(macro_name: str, layout_name: str, layout: dict) -> None:
    allowed_keys = STYLE_LAYOUT_LAYOUT_KEYS[macro_name]
    unknown_keys = sorted(set(layout) - allowed_keys)
    if unknown_keys:
        joined = ", ".join(unknown_keys)
        raise ValueError(f"Unknown {macro_name}.layouts.{layout_name} fields: {joined}")

    owner = f"{macro_name}.layouts.{layout_name}"
    for field_name, value in layout.items():
        if field_name == "mode":
            if value not in LAYOUT_MODE_VALUES[macro_name]:
                known = ", ".join(sorted(LAYOUT_MODE_VALUES[macro_name]))
                raise ValueError(
                    f"Invalid {owner}.{field_name}: {value!r}. Expected one of: {known}"
                )
            continue
        if field_name in LAYOUT_FIELD_ENUMS:
            if value not in LAYOUT_FIELD_ENUMS[field_name]:
                known = ", ".join(sorted(LAYOUT_FIELD_ENUMS[field_name]))
                raise ValueError(
                    f"Invalid {owner}.{field_name}: {value!r}. Expected one of: {known}"
                )
            continue
        if not isinstance(value, str):
            raise ValueError(f"Expected string for {owner}.{field_name}")


def validate_theme_semantics(theme: dict) -> None:
    for macro_name in TEXT_MACRO_VARIANTS:
        config = theme["macros"][macro_name]
        default_variant = config["default"]
        variants = config["variants"]
        if default_variant not in variants:
            known = ", ".join(sorted(variants))
            raise ValueError(
                f"Unknown default variant {default_variant!r} for {macro_name}. "
                f"Expected one of: {known}"
            )
        for variant_name, variant in variants.items():
            validate_text_variant_fields(theme, macro_name, variant_name, variant)

    for macro_name in STYLE_LAYOUT_MACRO_STYLES:
        config = theme["macros"][macro_name]
        default_style = config["default_style"]
        default_layout = config["default_layout"]
        styles = config["styles"]
        layouts = config["layouts"]
        if default_style not in styles:
            known = ", ".join(sorted(styles))
            raise ValueError(
                f"Unknown default style {default_style!r} for {macro_name}. "
                f"Expected one of: {known}"
            )
        if default_layout not in layouts:
            known = ", ".join(sorted(layouts))
            raise ValueError(
                f"Unknown default layout {default_layout!r} for {macro_name}. "
                f"Expected one of: {known}"
            )
        for style_name, style in styles.items():
            validate_style_fields(theme, macro_name, style_name, style)
        for layout_name, layout in layouts.items():
            validate_layout_fields(macro_name, layout_name, layout)


def load_theme(path: Path) -> dict:
    if not BASE_THEME_PATH.exists():
        raise FileNotFoundError(f"Missing base theme file: {BASE_THEME_PATH}")
    theme = merge_nested_dicts(load_yaml(BASE_THEME_PATH), load_yaml(path))
    theme_schema = load_yaml(THEME_SCHEMA_PATH)
    normalized = normalize_theme(theme)
    validate(instance=normalized, schema=theme_schema)
    validate_theme_semantics(normalized)
    return normalized


def resolve_theme_value(
    theme: dict, reference: str | None, groups: tuple[str, ...]
) -> str | None:
    if reference is None:
        return None
    for group_name in groups:
        group = theme[group_name]
        if reference in group:
            return str(group[reference])
    return str(reference)


def resolve_font_command(theme: dict, reference: str) -> str:
    if reference not in theme["fonts"]:
        known = ", ".join(sorted(theme["fonts"]))
        raise ValueError(f"Unknown font token {reference!r}. Expected one of: {known}")
    return f"\\resumefont{reference}"


def latex_weight(weight: str) -> str:
    return {"normal": "", "bold": r"\bfseries"}[weight]


def latex_shape(shape: str) -> str:
    return {
        "normal": "",
        "italic": r"\itshape",
        "slanted": r"\slshape",
    }[shape]


def transform_case(case: str, content: str) -> tuple[str, str]:
    if case == "uppercase":
        return "", rf"\MakeUppercase{{{content}}}"
    if case == "smallcaps":
        return r"\scshape", content
    return "", content


def build_styled_text(
    theme: dict,
    content: str,
    *,
    font: str,
    size: str,
    line: str,
    color: str | None,
    weight: str,
    shape: str,
    case: str,
) -> str:
    commands = [
        resolve_font_command(theme, font),
        rf"\fontsize{{{resolve_theme_value(theme, size, ('sizes',))}}}"
        rf"{{{resolve_theme_value(theme, line, ('sizes',))}}}\selectfont",
    ]
    extra_case_command, rendered_content = transform_case(case, content)
    for command in [
        latex_weight(weight),
        latex_shape(shape),
        extra_case_command,
        rf"\color{{{color}}}" if color else "",
    ]:
        if command:
            commands.append(command)
    return "{" + " ".join(commands + [rendered_content]) + "}"


def build_text_variant_body(theme: dict, variant: dict, content: str) -> str:
    return build_styled_text(
        theme,
        content,
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["color"],
        weight=variant["weight"],
        shape=variant["shape"],
        case=variant["case"],
    )


def build_entry_variant_body(theme: dict, variant: dict) -> str:
    line1_left = build_styled_text(
        theme,
        "#1",
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["line1_left_color"],
        weight=variant["line1_left_weight"],
        shape=variant["line1_left_shape"],
        case="normal",
    )
    line1_right = build_styled_text(
        theme,
        "#2",
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["line1_right_color"],
        weight=variant["line1_right_weight"],
        shape=variant["line1_right_shape"],
        case="normal",
    )
    line2_left = build_styled_text(
        theme,
        "#3",
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["line2_left_color"],
        weight=variant["line2_left_weight"],
        shape=variant["line2_left_shape"],
        case="normal",
    )
    line2_right = build_styled_text(
        theme,
        "#4",
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["line2_right_color"],
        weight=variant["line2_right_weight"],
        shape=variant["line2_right_shape"],
        case="normal",
    )
    meta_line = build_styled_text(
        theme,
        r"#2\ifstrempty{#4}{}{\enspace\textbullet\enspace #4}",
        font=variant["font"],
        size=variant["meta_size"],
        line=variant["meta_line"],
        color=variant["meta_color"],
        weight="normal",
        shape="normal",
        case="normal",
    )
    line_gap = resolve_theme_value(theme, variant["line_gap"], ("rules", "sizes"))
    bottom_gap = resolve_theme_value(theme, variant["bottom_gap"], ("rules", "sizes"))
    assert line_gap is not None
    assert bottom_gap is not None
    entry_tail = build_entry_tail(bottom_gap, variant["bottom_mode"])

    if variant["mode"] == "stacked":
        return rf"""
{{
  {line1_left}\\[{line_gap}]
  \ifstrempty{{#3}}{{}}{{{line2_left}\\[{line_gap}]}}
  \ifstrempty{{#2}}{{
    \ifstrempty{{#4}}{{}}{{{build_styled_text(theme, "#4", font=variant["font"], size=variant["meta_size"], line=variant["meta_line"], color=variant["meta_color"], weight="normal", shape="normal", case="normal")}{entry_tail}}}
  }}{{{meta_line}{entry_tail}}}
}}
""".strip()

    if variant["mode"] == "inline":
        return rf"""
{{
  {line1_left}
  \hfill
  \ifstrempty{{#3}}{{}}{{{line2_left}\ifstrempty{{#2}}{{}}{{,\ }}}}{line1_right}
  {entry_tail}
}}
""".strip()

    if variant["mode"] == "inline_left":
        return rf"""
{{
  {line1_left}\ifstrempty{{#3}}{{}}{{,\ {line2_left}}}
  \hfill
  {line1_right}
  {entry_tail}
}}
""".strip()

    return rf"""
{{
  {line1_left}
  \ifstrempty{{#2}}{{}}{{ \hfill {line1_right}}}
  \\[{line_gap}]
  \ifstrempty{{#3}}{{
    \ifstrempty{{#4}}{{}}{{{line2_right}}}
  }}{{
    {line2_left}
    \ifstrempty{{#4}}{{}}{{ \hfill {line2_right}}}
  }}
  {entry_tail}
}}
""".strip()


def build_entry_tail(bottom_gap: str, bottom_mode: str) -> str:
    if bottom_mode == "paragraph":
        return rf"\par\vspace*{{{bottom_gap}}}"
    return rf"\\[{bottom_gap}]"


def build_skill_variant_body(theme: dict, variant: dict) -> str:
    label = build_styled_text(
        theme,
        "#1",
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["label_color"],
        weight=variant["label_weight"],
        shape="normal",
        case="normal",
    )
    value = build_styled_text(
        theme,
        "#2",
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["value_color"],
        weight="normal",
        shape="normal",
        case="normal",
    )
    stack_gap = resolve_theme_value(theme, variant["stack_gap"], ("rules", "sizes"))

    if variant["mode"] == "stacked":
        return rf"""
{{
  {label}
  \ifstrempty{{#2}}{{\\}}{{\\[{stack_gap}] {value}\\}}
}}
""".strip()

    separator = variant["separator"]
    return rf"""
{{
  \ifstrempty{{#2}}{{{label}\\}}{{{label}{separator}{value}\\}}
}}
""".strip()


def build_sectiontitle_variant_body(theme: dict, variant: dict) -> str:
    title = build_styled_text(
        theme,
        "#1",
        font=variant["font"],
        size=variant["size"],
        line=variant["line"],
        color=variant["color"],
        weight=variant["weight"],
        shape=variant["shape"],
        case=variant["case"],
    )
    if not variant["rule_enabled"]:
        return rf"\par\nointerlineskip{title}\par"
    rule_color = variant["rule_color"]
    rule_width = resolve_theme_value(theme, variant["rule_width"], ("rules", "sizes"))
    rule_length = resolve_theme_value(theme, variant["rule_length"], ("rules", "sizes"))
    gap_before = resolve_theme_value(
        theme, variant["rule_gap_before"], ("rules", "sizes")
    )
    gap_after = resolve_theme_value(
        theme, variant["rule_gap_after"], ("rules", "sizes")
    )
    rule_block = rf"{{\color{{{rule_color}}}\rule{{{rule_length}}}{{{rule_width}}}}}"
    if variant["mode"] == "sidebar":
        return (
            rf"\par\nointerlineskip\vspace*{{{gap_before}}}"
            rf"{rule_block}\par\nointerlineskip\vspace*{{{gap_after}}}"
            rf"{title}\par\nointerlineskip\vspace*{{{gap_after}}}"
            rf"{rule_block}\par\nointerlineskip\vspace*{{{gap_before}}}"
        )
    return (
        rf"\par\nointerlineskip{title}\par\nointerlineskip\vspace*{{{gap_before}}}"
        rf"{rule_block}\par\nointerlineskip\vspace*{{{gap_after}}}"
    )


def private_macro_definition(
    macro_name: str, variant_name: str, arity: int, body: str
) -> str:
    params = "".join(f"#{index}" for index in range(1, arity + 1))
    return (
        rf"\expandafter\def\csname resume@{macro_name}@{variant_name}\endcsname"
        rf"{params}{{{body}}}"
    )


def private_style_layout_definition(
    macro_name: str, style_name: str, layout_name: str, arity: int, body: str
) -> str:
    params = "".join(f"#{index}" for index in range(1, arity + 1))
    return (
        rf"\expandafter\def\csname resume@{macro_name}@{style_name}@{layout_name}\endcsname"
        rf"{params}{{{body}}}"
    )


def build_private_macro_body(theme: dict, macro_name: str, variant: dict) -> str:
    if macro_name in {"cvname", "cvtitle", "cvmeta", "cvbody", "cvsmall"}:
        return build_text_variant_body(theme, variant, "#1")
    if macro_name == "cventry":
        return build_entry_variant_body(theme, variant)
    if macro_name == "cvskill":
        return build_skill_variant_body(theme, variant)
    if macro_name == "cvsectiontitle":
        return build_sectiontitle_variant_body(theme, variant)
    raise ValueError(f"Unsupported macro {macro_name!r}")


def generate_macro_definitions(theme: dict) -> list[str]:
    lines = []

    for macro_name in TEXT_MACRO_VARIANTS:
        config = theme["macros"][macro_name]
        arity = MACRO_ARITIES[macro_name]
        for variant_name, variant in config["variants"].items():
            body = build_private_macro_body(theme, macro_name, variant)
            lines.append(
                private_macro_definition(macro_name, variant_name, arity, body)
            )

    for macro_name in STYLE_LAYOUT_MACRO_STYLES:
        config = theme["macros"][macro_name]
        arity = MACRO_ARITIES[macro_name]
        for style_name, style in config["styles"].items():
            for layout_name, layout in config["layouts"].items():
                body = build_private_macro_body(
                    theme, macro_name, merge_dicts(style, layout)
                )
                lines.append(
                    private_style_layout_definition(
                        macro_name, style_name, layout_name, arity, body
                    )
                )
    return lines


def generate_macro_dispatchers(theme: dict) -> list[str]:
    wrappers = []

    for macro_name in TEXT_MACRO_VARIANTS:
        arity = MACRO_ARITIES[macro_name]
        default_variant = theme["macros"][macro_name]["default"]
        if arity == 1:
            wrappers.append(
                rf"\NewDocumentCommand{{\{macro_name}}}{{O{{{default_variant}}}m}}{{%"
            )
            wrappers.append(rf"  \resumedispatchone{{{macro_name}}}{{#1}}{{#2}}%")
            wrappers.append(r"}")
            continue

        if arity == 2:
            wrappers.append(
                rf"\NewDocumentCommand{{\{macro_name}}}{{O{{{default_variant}}}mm}}{{%"
            )
            wrappers.append(rf"  \resumedispatchtwo{{{macro_name}}}{{#1}}{{#2}}{{#3}}%")
            wrappers.append(r"}")
            continue

        if arity == 4:
            wrappers.append(
                rf"\NewDocumentCommand{{\{macro_name}}}{{O{{{default_variant}}}mmmm}}{{%"
            )
            wrappers.append(
                rf"  \resumedispatchfour{{{macro_name}}}{{#1}}{{#2}}{{#3}}{{#4}}{{#5}}%"
            )
            wrappers.append(r"}")
            continue

        raise ValueError(f"Unsupported macro arity for {macro_name}: {arity}")

    for macro_name in STYLE_LAYOUT_MACRO_STYLES:
        arity = MACRO_ARITIES[macro_name]
        default_style = theme["macros"][macro_name]["default_style"]
        default_layout = theme["macros"][macro_name]["default_layout"]
        if arity == 1:
            wrappers.append(
                rf"\NewDocumentCommand{{\{macro_name}}}{{O{{{default_style}}}O{{{default_layout}}}m}}{{%"
            )
            wrappers.append(
                rf"  \resumedispatchpairone{{{macro_name}}}{{#1}}{{#2}}{{#3}}%"
            )
            wrappers.append(r"}")
            continue

        if arity == 2:
            wrappers.append(
                rf"\NewDocumentCommand{{\{macro_name}}}{{O{{{default_style}}}O{{{default_layout}}}mm}}{{%"
            )
            wrappers.append(
                rf"  \resumedispatchpairtwo{{{macro_name}}}{{#1}}{{#2}}{{#3}}{{#4}}%"
            )
            wrappers.append(r"}")
            continue

        if arity == 4:
            wrappers.append(
                rf"\NewDocumentCommand{{\{macro_name}}}{{O{{{default_style}}}O{{{default_layout}}}mmmm}}{{%"
            )
            wrappers.append(
                rf"  \resumedispatchpairfour{{{macro_name}}}{{#1}}{{#2}}{{#3}}{{#4}}{{#5}}{{#6}}%"
            )
            wrappers.append(r"}")
            continue

        raise ValueError(f"Unsupported macro arity for {macro_name}: {arity}")

    return wrappers


def generate_color_blocks(theme: dict) -> list[str]:
    return [
        rf"\definecolor{{{name}}}{{HTML}}{{{value.replace('#', '')}}}"
        for name, value in theme["colors"].items()
    ]


def generate_font_blocks(theme: dict) -> list[str]:
    options = "[Path=fonts/,UprightFont=*-Regular,BoldFont=*-Bold,ItalicFont=*-Italic,BoldItalicFont=*-BoldItalic]"
    body_font = theme["fonts"]["body"]
    lines = [rf"\setmainfont{{{body_font}}}{options}"]
    for name, value in theme["fonts"].items():
        lines.append(rf"\newfontfamily\resumefont{name}{{{value}}}{options}")
    return lines


def generate_dispatch_helpers() -> list[str]:
    return [
        r"\makeatletter",
        r"\newcommand{\resumeunknownvariant}[2]{%",
        r"  \ClassError{resume}{Unknown #1 variant '#2'}{%",
        r"    Define the variant in the active theme or remove the optional argument.%",
        r"  }%",
        r"}",
        r"\newcommand{\resumeunknownstylelayout}[3]{%",
        r"  \ClassError{resume}{Unknown #1 style/layout '#2'/'#3'}{%",
        r"    Define the style and layout in the active theme or remove the optional arguments.%",
        r"  }%",
        r"}",
        r"\newcommand{\resumedispatchone}[3]{%",
        r"  \@ifundefined{resume@#1@#2}{%",
        r"    \resumeunknownvariant{#1}{#2}%",
        r"  }{%",
        r"    \csname resume@#1@#2\endcsname{#3}%",
        r"  }%",
        r"}",
        r"\newcommand{\resumedispatchtwo}[4]{%",
        r"  \@ifundefined{resume@#1@#2}{%",
        r"    \resumeunknownvariant{#1}{#2}%",
        r"  }{%",
        r"    \csname resume@#1@#2\endcsname{#3}{#4}%",
        r"  }%",
        r"}",
        r"\newcommand{\resumedispatchfour}[6]{%",
        r"  \@ifundefined{resume@#1@#2}{%",
        r"    \resumeunknownvariant{#1}{#2}%",
        r"  }{%",
        r"    \csname resume@#1@#2\endcsname{#3}{#4}{#5}{#6}%",
        r"  }%",
        r"}",
        r"\newcommand{\resumedispatchpairone}[4]{%",
        r"  \@ifundefined{resume@#1@#2@#3}{%",
        r"    \resumeunknownstylelayout{#1}{#2}{#3}%",
        r"  }{%",
        r"    \csname resume@#1@#2@#3\endcsname{#4}%",
        r"  }%",
        r"}",
        r"\newcommand{\resumedispatchpairtwo}[5]{%",
        r"  \@ifundefined{resume@#1@#2@#3}{%",
        r"    \resumeunknownstylelayout{#1}{#2}{#3}%",
        r"  }{%",
        r"    \csname resume@#1@#2@#3\endcsname{#4}{#5}%",
        r"  }%",
        r"}",
        r"\newcommand{\resumedispatchpairfour}[7]{%",
        r"  \@ifundefined{resume@#1@#2@#3}{%",
        r"    \resumeunknownstylelayout{#1}{#2}{#3}%",
        r"  }{%",
        r"    \csname resume@#1@#2@#3\endcsname{#4}{#5}{#6}{#7}%",
        r"  }%",
        r"}",
        r"\makeatother",
    ]


def generate_class(theme: dict) -> str:
    sizes = theme["sizes"]
    rules = theme["rules"]
    lines = [
        r"\NeedsTeXFormat{LaTeX2e}",
        r"\ProvidesClass{resume}[2026/03/20 Generated CV class]",
        r"\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}",
        r"\ProcessOptions\relax",
        r"\LoadClass{article}",
        "",
        r"\RequirePackage[",
        rf"  top={sizes['margin_top']},",
        rf"  bottom={sizes['margin_bottom']},",
        rf"  left={sizes['margin_side']},",
        rf"  right={sizes['margin_side']}",
        r"]{geometry}",
        r"\RequirePackage{fontspec}",
        r"\RequirePackage{xcolor}",
        r"\RequirePackage{hyperref}",
        r"\RequirePackage{paracol}",
        r"\RequirePackage{enumitem}",
        r"\RequirePackage{titlesec}",
        r"\RequirePackage{tcolorbox}",
        r"\RequirePackage{etoolbox}",
        r"\RequirePackage{xparse}",
        r"\RequirePackage{graphicx}",
        r"\RequirePackage{tikz}",
        r"\pagestyle{empty}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\parskip}{0pt}",
        r"\hypersetup{colorlinks=true, urlcolor=accent}",
        "",
    ]
    lines.extend(generate_font_blocks(theme))
    lines.append("")
    lines.extend(generate_color_blocks(theme))
    lines.append("")
    lines.extend(generate_dispatch_helpers())
    lines.append("")
    lines.extend(generate_macro_definitions(theme))
    lines.append("")
    lines.extend(generate_macro_dispatchers(theme))
    lines.append(r"\newcommand{\cvblocksep}[1]{\par\addvspace{#1}}")
    lines.append(rf"\setlength{{\columnsep}}{{{rules['column_gap']}}}")
    ratio_block = latex_column_ratio(theme)
    if ratio_block:
        lines.append(ratio_block)
    return "\n".join(lines).strip() + "\n"


_DATE_ORDERS = {
    "fr": "{month}/{year}",
    "en": "{year}/{month}",
}
_ONGOING_DATE_LABELS = {
    "fr": "présent",
    "en": "present",
}
_ONGOING_DATE_VALUES = frozenset(_ONGOING_DATE_LABELS.values())


def make_format_date(lang: str):
    fmt = _DATE_ORDERS.get(lang, _DATE_ORDERS["en"])
    ongoing_label = _ONGOING_DATE_LABELS.get(lang, _ONGOING_DATE_LABELS["en"])

    def format_date(value: str) -> str:
        if value and re.fullmatch(r"\d{4}-\d{2}", value):
            year, month = value.split("-")
            return fmt.format(year=year, month=month)
        if value in _ONGOING_DATE_VALUES:
            return ongoing_label
        return value if value else ""

    return format_date


def render_text(template_text: str, resume: dict, theme: dict, layout: str) -> str:
    env = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.filters["latex_escape"] = latex_escape
    env.filters["md_to_latex"] = md_to_latex
    env.filters["format_date"] = make_format_date(
        resume.get("meta", {}).get("lang", "en")
    )
    env.globals["latex_href"] = latex_href
    template = env.from_string(template_text)
    return template.render(**resume, theme=theme, layout=layout)


def copy_assets(output_dir: Path) -> None:
    fonts_src = CV_DIR / "fonts"
    if fonts_src.exists():
        shutil.copytree(fonts_src, output_dir / "fonts", dirs_exist_ok=True)
    for asset_name in ["profile.jpg"]:
        asset = CV_DIR / asset_name
        if asset.exists():
            shutil.copy2(asset, output_dir / asset.name)
    for svg_name in ["github.svg", "huggingface.svg", "linkedin.svg", "scholar.svg"]:
        svg = CV_DIR / svg_name
        if svg.exists():
            pdf_out = output_dir / svg.with_suffix(".pdf").name
            subprocess.run(
                ["rsvg-convert", "--format=pdf", f"--output={pdf_out}", str(svg)],
                check=True,
            )


def compile_pdf(output_dir: Path) -> None:
    result = subprocess.run(
        [
            "latexmk",
            "-lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "resume.tex",
        ],
        cwd=output_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout[-4000:])
        print(result.stderr[-2000:])
        raise RuntimeError("LuaLaTeX compilation failed")


def build(
    theme_name: str, layout: str, output_dir: Path, data_path: Path = DATA_PATH
) -> None:
    resume = load_yaml(data_path)
    schema = load_yaml(SCHEMA_PATH)
    theme_path = THEMES_DIR / f"{theme_name}.yaml"
    if not theme_path.exists():
        raise FileNotFoundError(f"Missing theme file: {theme_path}")

    validate(instance=resume, schema=schema)
    theme = load_theme(theme_path)
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    copy_assets(output_dir)
    (output_dir / "resume.cls").write_text(generate_class(theme), encoding="utf-8")
    (output_dir / "resume.tex").write_text(
        render_text(template_text, resume, theme, layout), encoding="utf-8"
    )
    compile_pdf(output_dir)
    print(f"Built {output_dir / 'resume.pdf'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build CV from YAML data, theme, and layout"
    )
    parser.add_argument(
        "variant", nargs="?", help="Optional variant alias: academic, industry, sciam"
    )
    parser.add_argument("--theme", help="Theme name from themes/*.yaml")
    parser.add_argument("--layout", help="Layout flag: single or twocol")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory (default: out)",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DATA_PATH,
        help="Path to resume YAML data file (default: data/resume.yaml)",
    )
    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()
        theme, layout, output_dir = resolve_args(args)
        build(theme, layout, output_dir, data_path=args.data)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
