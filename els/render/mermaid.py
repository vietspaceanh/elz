from __future__ import annotations

from ..specs import ElementSpec
from .html import display_name


def _node_label(spec: ElementSpec) -> str:
    display = display_name(spec.func_name)
    if not spec.args:
        return f"<b>{display}</b>"
    named = []
    for k, v in spec.args.items():
        val = str(v)
        display_val = (val[:40] + "...") if len(val) > 40 else val
        named.append(f"<b>{k}</b>: {display_val}")
    arg_block = "\n".join(named)
    formatted = f"<div style='text-align:left'><small><pre>{arg_block}</pre></small></div>"
    return f"`<b>{display}</b>\n{formatted}`"


def generate_mermaid_code(spec: ElementSpec) -> str:
    lines = ["graph TD"]
    seen: set[str] = set()

    def add_node(s: ElementSpec):
        nid = s.name or str(id(s))
        if nid in seen:
            return
        seen.add(nid)
        lines.append(f'    {nid}["{_node_label(s)}"]')
        for dep in s.deps:
            add_node(dep)
            dnid = dep.name or str(id(dep))
            lines.append(f'    {dnid}["{_node_label(dep)}"] --> {nid}["{_node_label(s)}"]')

    add_node(spec)
    return "\n".join(lines)
