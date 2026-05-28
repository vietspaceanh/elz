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

_COPY_BTN = """<button class="el-code-copy" title="Copy code" onclick="(function(b){
var w=b.closest('.el-code-wrap');
var c=w.querySelector('.highlight');
var t=c?c.textContent.trim():'';
navigator.clipboard.writeText(t).then(function(){
b.classList.add('el-code-copied');
setTimeout(function(){b.classList.remove('el-code-copied');},2000);
}).catch(function(){});
})(this)">
<span class="el-code-copy-icon"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='9' y='9' width='13' height='13' rx='2' ry='2'/><path d='M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1'/></svg></span>
<span class="el-code-check-icon"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg></span>
</button>"""

_DEVICON_URLS: dict[str, str] = {
    "python": "python/python-original",
    "javascript": "javascript/javascript-original",
    "js": "javascript/javascript-original",
    "typescript": "typescript/typescript-original",
    "ts": "typescript/typescript-original",
    "go": "go/go-original-wordmark",
    "rust": "rust/rust-original",
    "html": "html5/html5-original",
    "css": "css3/css3-original",
    "bash": "bash/bash-original",
    "sh": "bash/bash-original",
    "shell": "bash/bash-original",
    "zsh": "bash/bash-original",
    "json": "json/json-original",
    "yaml": "yaml/yaml-original",
    "yml": "yaml/yaml-original",
    "markdown": "markdown/markdown-original",
    "md": "markdown/markdown-original",
    "ruby": "ruby/ruby-original",
    "rb": "ruby/ruby-original",
    "java": "java/java-original",
    "kotlin": "kotlin/kotlin-original",
    "scala": "scala/scala-original",
    "swift": "swift/swift-original",
    "php": "php/php-original",
    "r": "r/r-original",
    "dart": "dart/dart-original",
    "elixir": "elixir/elixir-original",
    "haskell": "haskell/haskell-original",
    "lua": "lua/lua-original",
    "perl": "perl/perl-original",
    "matlab": "matlab/matlab-original",
    "dockerfile": "docker/docker-original",
    "sql": "azuresqldatabase/azuresqldatabase-original",
}

_LANG_ICONS: dict[str, str] = {
    "python": "py",
    "javascript": "js", "js": "js",
    "typescript": "ts", "ts": "ts",
    "go": "go",
    "rust": "rs",
    "sql": "sql",
    "html": "html",
    "css": "css",
    "bash": "$", "sh": "$", "shell": "$", "zsh": "$",
    "json": "{}",
    "yaml": "ym", "yml": "ym",
    "markdown": "md", "md": "md",
    "ruby": "rb", "rb": "rb",
    "java": "java",
    "kotlin": "kt",
    "scala": "scala",
    "swift": "swift",
    "php": "php",
    "r": "r",
    "dart": "dart",
    "elixir": "ex",
    "haskell": "hs",
    "lua": "lua",
    "perl": "perl",
    "matlab": "matlab",
    "dockerfile": "docker",
    "makefile": "make",
}


_DEVICON_CDN = "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons"


def _lang_badge(lang: str) -> str:
    text = _LANG_ICONS.get(lang, lang[:2].title() if lang else "")
    path = _DEVICON_URLS.get(lang)
    if path:
        icon = f'<img src="{_DEVICON_CDN}/{path}.svg" alt="{html.escape(lang)}" class="el-code-lang-icon">'
        return f'<span class="el-code-lang-badge">{icon}<span>{html.escape(text)}</span></span>'
    return f'<span class="el-code-lang-badge">{html.escape(text)}</span>'




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
        "mermaid": json.dumps({"theme": mermaid_theme, "layout": "elk"}),
        "updateEditor": False,
        "autoSync": True,
        "updateDiagram": True,
    }, separators=(",", ":"))
    compressed = zlib.compress(payload.encode("utf-8"))
    b64 = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    svg_url = f"https://mermaid.ink/svg/pako:{b64}?bgColor={bg[1:]}"
    return f"""<div class="g-wrap"
      onwheel="
       var i = this.querySelector('img');
       var oldS = parseFloat(this.dataset.s) || 1;
       var s = Math.max(0.2, Math.min(10, oldS * (event.deltaY > 0 ? 0.9 : 1.1)));
       this.dataset.s = s;
       var cr = i.getBoundingClientRect();
       var cx = event.clientX - cr.left - cr.width / 2;
       var cy = event.clientY - cr.top - cr.height / 2;
       var oldTx = parseFloat(this.dataset.tx) || 0;
       var oldTy = parseFloat(this.dataset.ty) || 0;
       var tx = oldTx + cx * (1 - s / oldS);
       var ty = oldTy + cy * (1 - s / oldS);
       this.dataset.tx = tx;
       this.dataset.ty = ty;
       i.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + s + ')';
       event.preventDefault()
      "
     onmousedown="
      this.dataset.dx = event.clientX - (parseFloat(this.dataset.tx) || 0);
      this.dataset.dy = event.clientY - (parseFloat(this.dataset.ty) || 0);
      this.dataset.drag = 1;
      this.style.cursor = 'grabbing';
      event.preventDefault()
     "
     onmousemove="
      if (this.dataset.drag == '1') {{
        var tx = event.clientX - (parseFloat(this.dataset.dx) || 0);
        var ty = event.clientY - (parseFloat(this.dataset.dy) || 0);
        this.dataset.tx = tx;
        this.dataset.ty = ty;
        this.querySelector('img').style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + (parseFloat(this.dataset.s) || 1) + ')';
      }}
     "
     onmouseup="
      this.dataset.drag = 0;
      this.style.cursor = 'grab'
     "
     onmouseleave="
      this.dataset.drag = 0;
      this.style.cursor = 'grab'
     ">
      <img src="{svg_url}" alt="graph" onload="this.parentElement.classList.add('loaded')">
      <button class="g-btn" title="Toggle full screen"
        onclick="
          event.stopPropagation();
          (function(g) {{
            try {{
              var i = g.querySelector('img');
              if (!i) return;
              var s = i.getAttribute('src');

              var o = document.querySelector('.el-overlay');
              if (o) {{
                try {{
                  if (o._c) o._c();
                  o.remove();
                }} catch (e) {{}}
                return;
              }}

              o = document.createElement('div');
              o.className = 'el-overlay';
              var bg = getComputedStyle(g).backgroundColor || '#1f1f28';
              o.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:99999;background:' + bg + ';display:flex;align-items:center;justify-content:center';

              var r = g.getBoundingClientRect();
              var t = Math.max(0, r.top + r.height / 2 - window.innerHeight / 2);
              o.style.paddingTop = t + 'px';
              o.setAttribute('tabindex', '-1');

              var initZ = parseFloat(g.dataset.s) || 1;
              var initTx = parseFloat(g.dataset.tx) || 0;
              var initTy = parseFloat(g.dataset.ty) || 0;
              o.dataset.z = initZ;
              o.dataset.tx = initTx;
              o.dataset.ty = initTy;

              o.onwheel = function(e) {{
                var oldZ = parseFloat(this.dataset.z) || 1;
                var z = Math.max(0.2, Math.min(10, oldZ * (e.deltaY > 0 ? 0.9 : 1.1)));
                this.dataset.z = z;
                var cr = c.getBoundingClientRect();
                var cx = e.clientX - cr.left - cr.width / 2;
                var cy = e.clientY - cr.top - cr.height / 2;
                var oldTx = parseFloat(this.dataset.tx) || 0;
                var oldTy = parseFloat(this.dataset.ty) || 0;
                var tx = oldTx + cx * (1 - z / oldZ);
                var ty = oldTy + cy * (1 - z / oldZ);
                this.dataset.tx = tx;
                this.dataset.ty = ty;
                c.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + z + ')';
                e.preventDefault()
              }};
              o.ontouchmove = function(e) {{ e.preventDefault() }};
              o.onmousedown = function(e) {{
                this.dataset.dx = e.clientX - (parseFloat(this.dataset.tx) || 0);
                this.dataset.dy = e.clientY - (parseFloat(this.dataset.ty) || 0);
                this.dataset.drag = 1;
                this.style.cursor = 'grabbing';
                e.preventDefault()
              }};

              var c = document.createElement('img');
              c.src = s;
              c.style.cssText = 'width:100%;height:100%;max-width:90vw;max-height:85vh;object-fit:contain;border-radius:4px;pointer-events:none;user-select:none';
              c.draggable = false;
              c.style.transform = 'translate(' + initTx + 'px,' + initTy + 'px) scale(' + initZ + ')';

              var onmove = function(e) {{
                if (o.dataset.drag == '1') {{
                  var tx = e.clientX - (parseFloat(o.dataset.dx) || 0);
                  var ty = e.clientY - (parseFloat(o.dataset.dy) || 0);
                  var z = parseFloat(o.dataset.z) || 1;
                  o.dataset.tx = tx;
                  o.dataset.ty = ty;
                  c.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + z + ')';
                }}
              }};

              var onup = function() {{
                o.dataset.drag = 0;
                o.style.cursor = 'default'
              }};

              o._c = function() {{
                document.removeEventListener('mousemove', onmove);
                document.removeEventListener('mouseup', onup);
                document.removeEventListener('keydown', k);
                window.removeEventListener('blur', bFn)
              }};

              document.addEventListener('mousemove', onmove);
              document.addEventListener('mouseup', onup);

              o.appendChild(c);

              var x = document.createElement('button');
              x.innerHTML = '&#x2715;';
              x.style.cssText = 'position:fixed;top:12px;right:12px;z-index:1;width:36px;height:36px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:#fff;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1';
              x.onclick = function(e) {{
                e.stopPropagation();
                try {{
                  if (o._c) o._c();
                  o.remove();
                }} catch (e) {{}}
              }};
              o.appendChild(x);

              var k = function(e) {{
                if (e.key === 'Escape') {{
                  try {{
                    if (o._c) o._c();
                    o.remove();
                  }} catch (e) {{}}
                }}
              }};
              document.addEventListener('keydown', k);

              var bFn = function() {{
                try {{
                  if (o._c) o._c();
                  o.remove();
                }} catch (e) {{}}
              }};
              if (/electron/i.test(navigator.userAgent) || typeof window.acquireVsCodeApi === 'function') {{
                window.addEventListener('blur', bFn);
              }}

              document.body.appendChild(o);
              o.focus()
            }} catch (e) {{}}
          }})(this.parentElement)
        ">&#x26F6; Full screen</button>
    </div>"""


def render_codefence(text: str, info: str | None = None, **kwargs) -> str:
    lang = (info.split(None, 1)[0] if info else "") or ""
    if lang == "mermaid":
        return _render_mermaid(text)

    highlighted = _highlight_code_cached(text, lang, theme.config.pygments_style)
    badge = _lang_badge(lang) if lang else ""

    return f'<div class="el-code-wrap">{badge}{_COPY_BTN}{highlighted}</div>'


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


md = mistune.create_markdown(escape=False, plugins=[_codefence_plugin, _table_plugin.table, _math_plugin])
