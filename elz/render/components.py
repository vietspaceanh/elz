from __future__ import annotations

import html as html_mod
import re

from ..decorator import el

_HEADING_RE = re.compile(r'<h([1-6])([^>]*)>(.*?)</h\1>', re.DOTALL)
_ID_RE = re.compile(r'\bid="([^"]+)"')


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')


def _extract_headings(html_str: str) -> list[tuple[int, str, str]]:
    headings = []
    for m in _HEADING_RE.finditer(html_str):
        level = int(m.group(1))
        raw_text = m.group(3)
        text = re.sub(r'<[^>]+>', '', raw_text)
        text = html_mod.unescape(text).strip()
        attrs = m.group(2)
        id_m = _ID_RE.search(attrs)
        slug = id_m.group(1) if id_m else _slugify(text)
        headings.append((level, text, slug))
    return headings


def _render_toc_tree(headings: list[tuple[int, str, str]]) -> str:
    if not headings:
        return "<ul>\n</ul>"

    def _render(idx, parent_level):
        items: list[str] = []
        while idx < len(headings):
            level, text, slug = headings[idx]
            if level <= parent_level:
                break
            item = f'  <li><a href="#{slug}">{html_mod.escape(text)}</a>'
            idx += 1
            if idx < len(headings) and headings[idx][0] > level:
                sub, idx = _render(idx, level)
                item += "\n" + sub + "\n  </li>"
            else:
                item += "</li>"
            items.append(item)
        return "<ul>\n" + "\n".join(items) + "\n</ul>", idx

    result, _ = _render(0, 0)
    return result


def _scrollspy_img() -> str:
    js = (
        "(function(e){"
        "var r=e.previousElementSibling;"
        "if(!r||!r.classList.contains('el-root')){e.remove();return}"
        "e.remove();"
        "function s(){"
        "var l=Array.from(r.querySelectorAll('a')).filter(function(a){return a.getAttribute('href')&&a.getAttribute('href').charAt(0)==='#'});"
        "if(!l.length)return;"
        "var ids=l.map(function(a){return a.getAttribute('href').slice(1)});"
        "var hs=ids.map(function(id){return document.getElementById(id)}).filter(Boolean);"
        "if(!hs.length)return;"
        "var cur=null;"
        "function a(id){if(id===cur)return;cur=id;l.forEach(function(x){x.classList.toggle('el-active',x.getAttribute('href')==='#'+id)})}"
        "function u(){var c=null;for(var i=0;i<hs.length;i++){if(hs[i].getBoundingClientRect().top<=1)c=hs[i].id}if(c)a(c)}"
        "var t=false;"
        "window.addEventListener('scroll',function(){if(!t){requestAnimationFrame(function(){u();t=false});t=true}},{passive:true});"
        "u()"
        "}"
        "if(document.readyState!=='loading')s();"
        "else document.addEventListener('DOMContentLoaded',s)"
        "})(this)"
    )
    return f'<img style="display:none" src="x" onerror="{js}">'


def _drawer_html(title: str, tree_html: str) -> str:
    return f"""html
    <div class="el-root">
      <button class="el-hb" onclick="this.parentElement.classList.toggle('open')" aria-label="{title}">
        <span></span><span></span><span></span>
      </button>
      <nav class="el-drawer">
        <div class="el-drawer-h">
          <h3>{title}</h3>
          <button class="el-drawer-x" onclick="this.closest('.el-root').classList.remove('open')" aria-label="Close">&times;</button>
        </div>
        {tree_html}
      </nav>
      <div class="el-bd" onclick="this.closest('.el-root').classList.remove('open')"></div>
    </div>
    """


def _drawer_css(position: str) -> str:
    is_left = position == "left"
    edge = "left" if is_left else "right"
    opposite = "right" if is_left else "left"
    translate = "translateX(-100%)" if is_left else "translateX(100%)"
    translate_open = "translateX(0)"
    border_side = f"border-{opposite}"
    hb_edge = f"{edge}: 16px"
    width_var = "var(--el-sidebar-width)" if is_left else "var(--el-toc-width)"

    return f"""
    .el-hb, .el-bd, .el-drawer-x {{ display: none; }}
    .el-drawer {{
        padding: 0; display: flex; flex-direction: column; gap: 16px;
    }}
    .el-drawer-h {{ display: flex; justify-content: space-between; align-items: center; }}
    .el-drawer-h h3 {{ margin: 0; font-size: 1.1em; font-weight: 600; }}
    .el-root ul {{ list-style: none; padding: 0; margin: 0; }}
    .el-root li {{ position: relative; padding: 2px 0; }}
    .el-root ul ul > li {{ padding-left: 1.4em; }}
    .el-root ul ul > li::before {{ content: ''; position: absolute; left: 0; top: 0; bottom: 0; border-left: 1px solid var(--el-border); }}
    .el-root ul ul > li:last-child::before {{ height: .75em; bottom: auto; }}
    .el-root ul ul > li::after {{ content: ''; position: absolute; top: .65em; left: 0; width: .9em; border-top: 1px solid var(--el-border); }}
    a {{ color: var(--el-link-color); text-decoration: none; font-size: .95em; }}
    a:hover {{ text-decoration: underline; }}
    .el-root a.el-active {{ color: var(--el-accent, #0066cc); font-weight: 600; }}
    @media (max-width: 768px) {{
        .el-hb {{
            display: flex; position: fixed; top: 16px; {hb_edge}; z-index: 999;
            width: 40px; height: 40px; border: none; background: var(--el-bg);
            border-radius: 8px; cursor: pointer;
            flex-direction: column; align-items: center; justify-content: center; gap: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,.12);
            transition: opacity .25s, transform .25s;
        }}
        .el-hb:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,.18); }}
        .el-hb span {{ display: block; width: 20px; height: 2px; background: var(--el-text); border-radius: 1px; transition: all .3s; }}
        .el-root.open .el-hb {{ opacity: 0; transform: scale(.8); pointer-events: none; }}
        .el-drawer {{
            position: fixed; {edge}: 0; top: 0; height: 100vh; width: {width_var};
            background: var(--el-bg); {border_side}: 1px solid var(--el-border);
            transform: {translate}; transition: transform .3s ease;
            z-index: 1001; overflow-y: auto; padding: 24px; box-sizing: border-box;
        }}
        .el-root.open .el-drawer {{ transform: {translate_open}; }}
        .el-drawer-x {{ display: inline; border: none; background: none; font-size: 24px; cursor: pointer; color: var(--el-text); padding: 0 4px; line-height: 1; opacity: .6; }}
        .el-drawer-x:hover {{ opacity: 1; }}
        .el-bd {{
            display: block; position: fixed; inset: 0; background: rgba(0,0,0,.3); z-index: 1000;
            opacity: 0; pointer-events: none; transition: opacity .3s;
        }}
        .el-root.open .el-bd {{ opacity: 1; pointer-events: auto; }}
    }}
    """


@el
def sidebar(items: list[str] | None = None):
    sidebar.css(_drawer_css("left"))
    lis = "\n".join(f'<li>{item}</li>' for item in (items or []))
    return _drawer_html("Navigation", f"<ul>\n{lis}\n</ul>")


@el
def toc(element):
    toc.css(_drawer_css("right"))
    headings = _extract_headings(element.get())
    return _drawer_html("Contents", _render_toc_tree(headings)) + _scrollspy_img()
