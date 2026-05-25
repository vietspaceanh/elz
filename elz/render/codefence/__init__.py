from __future__ import annotations

import base64
import functools
import html
import re
import zlib
import json

import mistune
import pygments
from mistune.plugins import table as _table_plugin
from mistune.plugins.math import math as _math_plugin
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


@functools.lru_cache(maxsize=256)
def _render_mermaid(text: str) -> str:
    palette = theme.config.palette
    bg = palette["bg"]
    r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
    dark = (0.299 * r + 0.587 * g + 0.114 * b) / 255 < 0.5
    mermaid_theme = "dark" if dark else "default"
    payload = json.dumps({
        "code": text,
        "mermaid": json.dumps({"theme": mermaid_theme}),
        "updateEditor": False,
        "autoSync": True,
        "updateDiagram": True,
    }, separators=(",", ":"))
    compressed = zlib.compress(payload.encode("utf-8"))
    b64 = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    svg_url = f"https://mermaid.ink/svg/pako:{b64}?bgColor={bg[1:]}"
    return f"""<div class="g-wrap"
     onwheel="var i=this.querySelector('img');var s=parseFloat(this.dataset.s)||1;s=Math.max(0.2,Math.min(10,s*(event.deltaY>0?0.9:1.1)));this.dataset.s=s;i.style.transform='translate('+(parseFloat(this.dataset.tx)||0)+'px,'+(parseFloat(this.dataset.ty)||0)+'px) scale('+s+')';event.preventDefault()"
     onmousedown="this.dataset.dx=event.clientX-(parseFloat(this.dataset.tx)||0);this.dataset.dy=event.clientY-(parseFloat(this.dataset.ty)||0);this.dataset.drag=1;this.style.cursor='grabbing';event.preventDefault()"
     onmousemove="if(this.dataset.drag=='1'){{var tx=event.clientX-(parseFloat(this.dataset.dx)||0);var ty=event.clientY-(parseFloat(this.dataset.dy)||0);this.dataset.tx=tx;this.dataset.ty=ty;this.querySelector('img').style.transform='translate('+tx+'px,'+ty+'px) scale('+(parseFloat(this.dataset.s)||1)+')'}}"
     onmouseup="this.dataset.drag=0;this.style.cursor='grab'"
     onmouseleave="this.dataset.drag=0;this.style.cursor='grab'">
      <img src="{svg_url}" alt="graph">
      <button class="g-btn" title="Toggle full screen"
        onclick="event.stopPropagation();var g=this.parentElement;var fs=document.fullscreenElement||document.webkitFullscreenElement;if(fs==g){{if(document.exitFullscreen)document.exitFullscreen();else if(document.webkitExitFullscreen)document.webkitExitFullscreen()}}else{{if(g.requestFullscreen)g.requestFullscreen();else if(g.webkitRequestFullscreen)g.webkitRequestFullscreen()}}">&#x26F6; Full screen</button>
    </div>"""


def render_codefence(text: str, info: str | None = None, **kwargs) -> str:
    lang = (info.split(None, 1)[0] if info else "") or ""
    if lang == "mermaid":
        return _render_mermaid(text)
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


def _codefence_plugin(md):
    md.renderer.block_code = render_codefence


def _heading_slugify(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def get_md() -> mistune.Markdown:
    global _md
    if _md is None:
        _md = mistune.create_markdown(escape=False, plugins=[_codefence_plugin, _table_plugin.table, _math_plugin])
        _heading = _md.renderer.heading
        def _heading_with_id(text, level, **attrs):
            slug = _heading_slugify(text)
            return f'<h{level} id="{slug}">{text}</h{level}>'
        _md.renderer.heading = _heading_with_id
    return _md
