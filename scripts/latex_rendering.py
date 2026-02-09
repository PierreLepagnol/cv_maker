"""LaTeX rendering infrastructure.

This module centralizes LaTeX emission mechanics (indentation, environments,
macro calls) so section generators can focus on *what* to render.

Patterns:
  - Builder: LatexBuilder
  - Template Method: ListSectionRenderer
  - Strategy: renderers implement .render(data)
  - Composite: CompositeRenderer
"""

from contextlib import contextmanager, nullcontext

from latex_escaper import escape_latex


def fmt_date_range(start, end, sep=" - "):
    start_s = str(start or "").strip()
    end_s = str(end or "").strip()
    parts = [p for p in (start_s, end_s) if p]
    return sep.join(parts)


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def latex_href(url, title_text):
    """Render a hyperref link: \\href{url}{title}.

    Notes:
      - URLs should not be LaTeX-escaped (see escape_latex() rules)
      - Title text is escaped to be safe in LaTeX
    """

    url_s = str(url or "").strip()
    title_s = str(title_text or "").strip()
    safe_title = escape_latex(title_s)
    return f"\\href{{{url_s}}}{{{safe_title}}}"


class LatexBuilder:
    def __init__(self, indent="  "):
        self._indent = indent
        self._level = 0
        self._lines = []

    def _args_tex(self, args):
        return "".join(f"{{{a}}}" for a in args)

    @contextmanager
    def indent(self):
        self._level += 1
        try:
            yield
        finally:
            self._level -= 1

    def line(self, text=""):
        if text:
            self._lines.append(f"{self._indent * self._level}{text}")
        else:
            self._lines.append("")

    @contextmanager
    def env(
        self,
        name,
        *begin_args,
        blank_after_begin=True,
        blank_before_end=False,
        blank_after_end=False,
    ):
        args_tex = self._args_tex(begin_args)
        self.line(f"\\begin{{{name}}}{args_tex}")
        if blank_after_begin:
            self.line()

        try:
            with self.indent():
                yield
        finally:
            if blank_before_end:
                self.line()
            self.line(f"\\end{{{name}}}")
            if blank_after_end:
                self.line()

    def command(self, name, *args):
        args_tex = self._args_tex(args)
        self.line(f"\\{name}{args_tex}")

    @contextmanager
    def command_body(self, name, *args):
        """Emit a macro call where the last argument is a block.

        Generates:
          \\macro{a}{b}{
            <body>
          }
        """

        args_tex = self._args_tex(args)
        self.line(f"\\{name}{args_tex}{{")
        try:
            with self.indent():
                yield
        finally:
            self.line("}")

    def render(self):
        text = "\n".join(self._lines).rstrip()
        return f"{text}\n" if text else ""


class CompositeRenderer:
    """Combine multiple renderers into a single output."""

    def __init__(self, *renderers):
        self._renderers = tuple(renderers)

    def render(self, data):
        parts = []
        for renderer in self._renderers:
            part = renderer.render(data)
            if part and part.strip():
                parts.append(part.rstrip())
        if not parts:
            return ""
        return "\n\n".join(parts).rstrip() + "\n"


class ListSectionRenderer:
    """Template Method for list-based sections.

    Subclasses provide:
      - key: name of the list in the data dict
      - outer_env: optional LaTeX environment to wrap the list
      - render_item(builder, item): how to render one item
    """

    key = ""
    outer_env = None
    outer_env_args = ()
    outer_env_blank_after_begin = True
    item_blank_line = True

    def _get_items(self, data):
        if data is None:
            return []

        if hasattr(data, "get"):
            return data.get(self.key, []) or []
        return getattr(data, self.key, []) or []

    def render(self, data):
        items = self._get_items(data)

        if not isinstance(items, list) or not items:
            return ""

        b = LatexBuilder()

        env_context = nullcontext()
        if self.outer_env:
            env_context = b.env(
                self.outer_env,
                *self.outer_env_args,
                blank_after_begin=self.outer_env_blank_after_begin,
            )

        with env_context:
            for item in items:
                if item is None:
                    continue
                wrote = self.render_item(b, item)
                if wrote and self.item_blank_line:
                    b.line()

        return b.render()

    def render_item(self, _builder, _item):
        raise NotImplementedError
