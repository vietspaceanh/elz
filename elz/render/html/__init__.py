from __future__ import annotations

import html
import os
import re

from ...specs import ElementSpec
from ..css import collect_component_css, wrap_scope
from ..codefence import md, process_pyg, restore_pyg, _heading_slugify
from ..theme import theme

_SLOT_RE = re.compile(r"__ELF_(\d+)__")


def _render_markdown(text: str) -> str:
    slug_counts: dict[str, int] = {}
    original = md.renderer.heading

    def _heading(text, level, **attrs):
        slug = _heading_slugify(text)
        n = slug_counts.get(slug, 0) + 1
        slug_counts[slug] = n
        if n > 1:
            slug = f"{slug}-{n}"
        return f'<h{level} id="{slug}">{text}</h{level}>'

    md.renderer.heading = _heading
    try:
        return md(text)
    finally:
        md.renderer.heading = original


def render_full_html(spec: ElementSpec, dev_mode: bool = True) -> str:
    body = render_fragment(spec, dev_mode)

    style = theme.get_css(pygments=True)
    css = collect_component_css(spec)
    if css:
        style += "\n" + css

    katex = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>
<script>
renderMathInElement(document.body,{delimiters:[{left:"\\\\(",right:"\\\\)",display:false},{left:"\\\\[",right:"\\\\]",display:true},{left:"$$",right:"$$",display:true}]})
</script>"""

    return f'<style>{style}</style>\n{katex}\n{body}'


def render_fragment(spec: ElementSpec, dev_mode: bool = True, child_html: list[str] | None = None,
                   codes: dict[str, str] | None = None) -> str:
    if codes is None:
        codes = {}
    content = spec.adhoc_fn() if spec.adhoc_fn else (spec.content or "")
    if not spec.deps:
        body = _render_text(content, spec.format, codes)
    elif _is_flat_template(content):
        body = _render_rows(spec, content, dev_mode, codes, child_html)
    else:
        if child_html is None:
            child_html = [render_fragment(d, dev_mode, None, codes) for d in spec.deps]
        body = _fill_slots(content, child_html, spec.format, codes)
    body = wrap_scope(body, spec)
    return _maybe_wrap_dev_child(body, spec, dev_mode)


def display_name(func_name: str | None) -> str:
    if func_name is None:
        return "?"
    parts = func_name.split("__", 1)
    if len(parts) == 2:
        if parts[0] == "_main":
            return parts[1]
        return f"{parts[0]}.{parts[1]}"
    return parts[0]


def _render_badge(spec: ElementSpec, name: str) -> str:
    if spec.source:
        filepath, lineno = spec.source
        filepath = os.path.abspath(filepath)
        if os.path.isfile(filepath):
            return (
                f'<a href="{html.escape(filepath)}:{lineno}"'
                f' class="el-dev-link"'
                f' title="{html.escape(filepath)}:{lineno}">{name}</a>'
            )
    return f'<span class="el-dev-link">{name}</span>'


def _maybe_wrap_dev_child(content: str, spec: ElementSpec, dev_mode: bool = True) -> str:
    if not dev_mode or not spec.source:
        return content
    name = html.escape(display_name(spec.func_name) if spec.func_name else spec.name or "")
    badge = _render_badge(spec, name)
    return f'<div class="el-dev">{content}{badge}</div>'


def _is_flat_template(content: str) -> bool:
    for line in content.split("\n"):
        stripped = line.strip()
        if _SLOT_RE.search(stripped):
            remaining = _SLOT_RE.sub("", stripped).strip()
            if remaining:
                return False
    return True


def _render_text(text: str, fmt: str, codes: dict[str, str]) -> str:
    rendered = process_pyg(text, codes)
    if fmt != "html":
        rendered = _render_markdown(rendered)
    return restore_pyg(rendered, codes)


def _fill_slots(content: str, children: list[str], fmt: str, codes: dict) -> str:
    parts = _SLOT_RE.split(content)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            result.append(_render_text(part, fmt, codes))
        else:
            result.append(children[int(part)])
    return "".join(result)


def _split_into_rows(content: str) -> list[tuple]:
    lines = content.split("\n")
    groups: list[tuple[str, str, list[int], bool]] = []
    text_buf: list[str] = []

    for line in lines:
        indices = [int(m) for m in _SLOT_RE.findall(line)]
        if indices:
            if text_buf:
                groups.append(("text", "\n".join(text_buf), [], False))
                text_buf = []
            groups.append(("element", line, indices, len(indices) > 1))
        else:
            text_buf.append(line)

    if text_buf:
        groups.append(("text", "\n".join(text_buf), [], False))
    return groups


def _render_rows(spec: ElementSpec, content: str, dev_mode: bool, codes: dict,
                         child_html: list[str] | None = None) -> str:
    groups = _split_into_rows(content)
    results = []
    for gtype, gcontent, indices, has_multiple in groups:
        if gtype == "text":
            if not gcontent.strip():
                continue
            html = _fill_slots(gcontent, [], spec.format, codes)
            results.append(f'    <div class="el-text">{html}</div>')
        else:
            def _remap(m):
                old = int(m.group(1))
                return f"__ELF_{indices.index(old)}__"
            if child_html is not None:
                children = [child_html[i] for i in indices]
            else:
                children = [render_fragment(spec.deps[i], dev_mode, None, codes) for i in indices]
            html = _fill_slots(_SLOT_RE.sub(_remap, gcontent), children, spec.format, codes)

            if has_multiple:
                results.append(f'    <div class="el-row">{html}</div>')
            else:
                results.append(html)

    items = "\n".join(results)
    return items