from __future__ import annotations

import functools
import html
import re

import mistune
import pygments
from mistune.plugins import table as _table_plugin
from pygments.lexers import get_lexer_by_name

from .lexer import ElfPythonLexer
from ..theme import theme

PYG_RE = re.compile(r"py`([^`]+)`")
PYG_PH_RE = re.compile(r"<!--PYG_(\d+)-->")

_md: mistune.Markdown | None = None


@functools.lru_cache(maxsize=512)
def _highlight_code_cached(text: str, lang: str, style: str) -> str:
    try:
        if lang == "python":
            lexer = ElfPythonLexer(stripall=True)
        else:
            lexer = get_lexer_by_name(lang, stripall=True) if lang else get_lexer_by_name("text")
        return pygments.highlight(text, lexer, theme.get_formatter())
    except Exception:
        return f"<pre><code>{html.escape(text)}</code></pre>"


def highlight_code(text: str, info: str | None = None, **kwargs) -> str:
    lang = (info.split(None, 1)[0] if info else "") or ""
    return _highlight_code_cached(text, lang, theme.config.pygments_style)


@functools.lru_cache(maxsize=512)
def _highlight_inline_cached(text: str, style: str) -> str:
    try:
        formatter = pygments.formatters.HtmlFormatter(style=style, nowrap=True)
        highlighted = pygments.highlight(text, ElfPythonLexer(stripall=True), formatter).rstrip(chr(10))
        return f'<code class="hl">{highlighted}</code>'
    except Exception:
        return f"<code>{html.escape(text)}</code>"


def highlight_inline(text: str) -> str:
    return _highlight_inline_cached(text, theme.config.pygments_style)


def process_pyg(text: str, codes: dict[str, str]) -> str:
    def _replacer(m):
        idx = str(len(codes))
        codes[idx] = m.group(1)
        return f"<!--PYG_{idx}-->"
    return PYG_RE.sub(_replacer, text)


def restore_pyg(html_text: str, codes: dict[str, str]) -> str:
    def _replacer(m):
        return highlight_inline(codes[m.group(1)])
    return PYG_PH_RE.sub(_replacer, html_text)


def _pygments_plugin(md):
    md.renderer.block_code = highlight_code


def _heading_slugify(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def get_md() -> mistune.Markdown:
    global _md
    if _md is None:
        _md = mistune.create_markdown(escape=False, plugins=[_pygments_plugin, _table_plugin.table])
        _heading = _md.renderer.heading
        def _heading_with_id(text, level, **attrs):
            slug = _heading_slugify(text)
            return f'<h{level} id="{slug}">{text}</h{level}>'
        _md.renderer.heading = _heading_with_id
    return _md
