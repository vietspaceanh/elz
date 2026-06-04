from __future__ import annotations

import html
import re
from ..specs import ElementSpec, replay_decos

_SCOPE_RE = re.compile(r"[^a-zA-Z0-9_-]")


def compile_css(css_text: str, scope: str, variants: dict | None = None) -> str:
    text = css_text.strip()
    if not text:
        return ""
    if '{' not in text:
        return f".{scope} {{\n{text}\n}}"

    root_decls: list[str] = []
    rules: list[tuple[str, str]] = []
    i = 0
    length = len(text)

    while i < length:
        brace = text.find('{', i)
        if brace == -1:
            rest = text[i:].strip()
            if rest:
                root_decls.append(rest)
            break

        selector = text[i:brace].strip()
        depth = 1
        j = brace + 1
        while j < length and depth:
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1
        declarations = text[brace + 1:j - 1].strip()

        if selector:
            rules.append((selector, declarations))
        elif declarations:
            root_decls.append(declarations)

        i = j

    result: list[str] = []
    if root_decls:
        result.append(f".{scope} {{\n{'\n'.join(root_decls)}\n}}")
    for sel, decl in rules:
        if sel.startswith("@"):
            inner = compile_css(decl, scope)
            result.append(f"{sel} {{\n{inner}\n}}")
        else:
            prefixed = ", ".join(_prefix_selector(s, scope) for s in _split_selectors(sel))
            result.append(f"{prefixed} {{\n{decl}\n}}")
    if variants:
        for cond, decl in variants.items():
            cond = cond.strip()
            at_rule = cond if cond.startswith("@") else f"@media {cond}"
            result.append(f"{at_rule} {{\n.{scope} {{\n{decl}\n}}\n}}")
    return "\n".join(result)


def collect_component_css(spec: ElementSpec) -> str:
    seen: set[str] = set()
    parts: list[str] = []

    def _walk(s: ElementSpec):
        if s.css and s.func_name and s.func_name not in seen:
            seen.add(s.func_name)
            parts.append(compile_css(s.css, scope_class(s.func_name), s.css_variants))
        if s.deps:
            for d in s.deps:
                _walk(d)

    _walk(spec)
    return "\n".join(parts)


def scope_class(func_name: str) -> str:
    return f"el-c-{_SCOPE_RE.sub('_', func_name)}"


def wrap_scope(content: str, spec: ElementSpec) -> str:
    if spec.decos:
        classes, styles, attrs = replay_decos(spec.decos)
        all_classes = ['el-deco', *classes]
        style = ';'.join(styles)
        attrs_str = ''
        for k, v in attrs.items():
            if v == '':
                attrs_str += f' {k}'
            else:
                attrs_str += f' {k}="{html.escape(str(v))}"'
        style_attr = f' style="{html.escape(style)}"' if style else ''
        content = f'<div class="{" ".join(all_classes)}"{style_attr}{attrs_str}>\n{content}\n</div>'
    if spec.css:
        return f'<div class="{scope_class(spec.func_name)}">{content}</div>'
    return content

def _split_selectors(text: str) -> list[str]:
    parts = []
    depth = start = 0
    for i, ch in enumerate(text):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ',' and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    parts.append(text[start:].strip())
    return parts


def _prefix_selector(sel: str, scope: str) -> str:
    if '&' in sel:
        return sel.replace('&', f'.{scope}')
    return f'.{scope} {sel}'