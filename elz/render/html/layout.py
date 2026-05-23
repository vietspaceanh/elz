from __future__ import annotations

import html
from ...specs import ElementSpec, Mods


def grid_spec(
    children: list[ElementSpec],
    cols: int = 2,
    weights: list[int | float] | None = None,
    gap: int | str | None = None,
    mods: list[Mods | None] | None = None,
) -> ElementSpec:
    _weights = weights or [c.weight for c in children]
    if _weights and any(w is not None for w in _weights):
        col_templates = " ".join(f"{w}fr" if w is not None else "1fr" for w in _weights)
    else:
        col_templates = f"repeat({cols}, 1fr)"
    if gap is None:
        gap_str = "var(--el-gap)"
    elif isinstance(gap, int):
        gap_str = f"{gap}px"
    else:
        gap_str = gap
    items = "\n".join(
        _grid_item_html(f"__ELF_{i}__", mods=mods[i] if mods else None)
        for i in range(len(children))
    )
    content = (
        f'<div style="display:grid;grid-template-columns:{col_templates};row-gap:{gap_str}">\n'
        f"{items}\n"
        f"</div>"
    )
    args = {}
    if weights is not None:
        args["weights"] = weights
    if cols != 2:
        args["cols"] = cols
    if gap is not None:
        args["gap"] = gap
    return _layout_spec("grid", content, deps=children, args=args)


def _grid_item_html(ph: str, extra_style: str = "", mods: Mods | None = None) -> str:
    el_classes = ['el-grid-item']
    styles = ["min-width:0"]
    extra = ""
    if mods:
        el_classes = mods.apply_classes(el_classes)
        styles.extend(mods.styles)
        for k, v in mods.attrs.items():
            extra += f' {k}' if v == '' else f' {k}="{html.escape(str(v))}"'
    if extra_style:
        styles.append(extra_style)
    return f'    <div class="{" ".join(el_classes)}" style="{";".join(styles)}"{extra}>{ph}</div>'


def _layout_spec(
    func_suffix: str,
    content: str,
    deps: list | None = None,
    args: dict | None = None,
    weight: int | float | None = None,
) -> ElementSpec:
    parts = [d.name or f"_{i}" for i, d in enumerate(deps or [])]
    name = f"layout_{func_suffix}__{'__'.join(parts)}___{id(content)}" if parts else f"layout_{func_suffix}"
    kw = dict(
        func_name=f"layout__{func_suffix}",
        name=name,
        format="html",
        content=content,
        adhoc_fn=lambda: content,
        deps=deps or [],
        args=args or {},
    )
    if weight is not None:
        kw["weight"] = weight
    return ElementSpec(**kw)