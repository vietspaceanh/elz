from __future__ import annotations

import html
import re
from dataclasses import replace

from .render import generate_mermaid_code, render_full_html
from .render.html.layout import column_spec, row_spec
from .render.html.style import STRUCTURAL_CSS
from .render.theme import theme
from .runtime import composition_deps, runtime
from .specs import ElementSpec, Mods


class Element:
    def __init__(self, spec: ElementSpec):
        self.spec = spec
        self.content = None
        self._composed_at_epoch = None
        self._layout_children: list[Element] | None = None

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def deps(self):
        return self.spec.deps

    @property
    def func_name(self) -> str:
        return self.spec.func_name

    @property
    def args(self) -> dict:
        return self.spec.args

    @property
    def format(self) -> str:
        return self.spec.format

    @property
    def graph(self):
        return generate_mermaid_code(self.spec)

    def css(self, text: str, /, variants: dict | None = None) -> Element:
        self.spec.css = text
        if variants:
            self.spec.css_variants = variants
        return self

    def refresh(self):
        self.content = None

    def get(self) -> str:
        return runtime.render(self.spec)

    def _repr_html_(self) -> str | None:
        page_el = root(self)
        return render_full_html(page_el.spec, dev_mode=runtime.dev_mode)

    def __str__(self) -> str:
        return self.get()

    def __format__(self, _) -> str:
        stack = composition_deps.get()
        if stack:
            deps = stack[-1]
            idx = len(deps)
            self.spec.content = self.get()
            deps.append(self.spec)
            return f"__ELF_{idx}__"
        return self.get()

    def __repr__(self) -> str:
        return f"Element({self.func_name})"

    @property
    def _row_children(self) -> list[Element]:
        return self._layout_children or [self]

    def __or__(self, other):
        if isinstance(other, Element):
            return row(*self._row_children, *other._row_children)
        wrapped = _wrap_repr_html(other)
        if wrapped is not None:
            return row(*self._row_children, *wrapped._row_children)
        return NotImplemented

    def __ror__(self, other):
        wrapped = _wrap_repr_html(other)
        if wrapped is not None:
            return row(*wrapped._row_children, *self._row_children)
        if isinstance(other, Element):
            return row(*other._row_children, *self._row_children)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Element):
            return column(self, other)
        wrapped = _wrap_repr_html(other)
        if wrapped is not None:
            return column(self, wrapped)
        return NotImplemented

    def __rtruediv__(self, other):
        wrapped = _wrap_repr_html(other)
        if wrapped is not None:
            return column(wrapped, self)
        if isinstance(other, Element):
            return column(other, self)
        return NotImplemented

    def _copy(self) -> Element:
        return Element(replace(self.spec))

    def _apply_modifier(self, modifier):
        if isinstance(modifier, (int, float)):
            el = self._copy()
            el.spec.weight = modifier
            return el
        if isinstance(modifier, Mods):
            el = self._copy()
            el.spec.mods = (el.spec.mods or Mods()).merge(modifier)
            return el
        if isinstance(modifier, str):
            el = self._copy()
            mods = el.spec.mods or Mods()
            el.spec.mods = mods.merge(Mods.parse(modifier))
            return el
        if callable(modifier):
            el = self._copy()
            result = modifier()
            if isinstance(result, Mods):
                el.spec.mods = (el.spec.mods or Mods()).merge(result)
                return el
        return NotImplemented

    def __matmul__(self, modifier):
        return self._apply_modifier(modifier)

    def __rmatmul__(self, modifier):
        return self._apply_modifier(modifier)

    def __bool__(self):
        return True

    def save(self, path: str, title: str | None = None):
        if not path.endswith(".html"):
            raise ValueError(f"save() requires a .html file path, got: {path!r}")

        page_el = root(self)
        body = render_full_html(page_el.spec, dev_mode=False)
        body = re.sub(
            r'<script\b([^>]*?)>([\s\S]*?)</script>',
            lambda m: m.group(0) if 'src' in m.group(1)
            else f'<script{m.group(1)}>document.addEventListener("DOMContentLoaded",function(){{{m.group(2)}}});</script>',
            body,
        )
        title_html = f"<title>{html.escape(title)}</title>\n  " if title else ""

        page_css = f"""<style>
        body {{ margin: 0; background: {theme.config.palette["bg"]}; }}
        .js-plotly-plot {{ animation: fadeIn 0.3s ease-in; }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        </style>"""
        full = f"""<!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          {title_html}{page_css}<meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
        {body}
        </body>
        </html>
        """

        with open(path, "w", encoding="utf-8") as f:
            f.write(full)


def root(body: Element) -> Element:
    spec = ElementSpec(
        func_name="root",
        name="root",
        format="html",
        content='<div class="el">__ELF_0__</div>',
        deps=[body.spec],
        css=STRUCTURAL_CSS,
    )
    return Element(spec)


def row(*children: Element, weights: list[int | float] | None = None, gap: int | str | None = None) -> Element:
    specs = [c.spec for c in children]
    mods = [c.spec.mods for c in children]
    spec = row_spec(specs, cols=len(children), weights=weights, gap=gap, mods=mods)
    el = Element(spec)
    el._layout_children = list(children)
    return el


def column(*children: Element, gap: int | str | None = None) -> Element:
    specs = [c.spec for c in children]
    spec = column_spec(specs, gap=gap)
    return Element(spec)


def sticky(el):
    return el @ 'data-sticky'


def _wrap_repr_html(obj) -> Element | None:
    if callable(obj):
        return
    if hasattr(obj, '_repr_html_'):
        label = getattr(obj, 'name', None) or type(obj).__name__
        spec = ElementSpec(
            func_name=label,
            name=label,
            format="html",
            adhoc_fn=obj._repr_html_,
        )
        return Element(spec)
    return