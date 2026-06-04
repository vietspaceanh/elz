from __future__ import annotations

from .specs import Deco, Wrapper


def to_modifier(modifier) -> Deco | Wrapper | int | float | None:
    """Convert various types to a Deco, Wrapper, or numeric weight."""
    if modifier is None:
        return None
    if isinstance(modifier, (Deco, Wrapper)):
        return modifier
    if isinstance(modifier, (int, float)):
        return modifier
    if isinstance(modifier, str):
        return Deco.parse(modifier)
    if callable(modifier):
        result = modifier()
        return to_modifier(result)
    return None


def center(pct: float | None = None) -> Deco:
    styles = ['margin-left: auto', 'margin-right: auto']
    if pct is not None:
        styles.append(f'width: {pct * 100}%')
    return Deco(styles=styles)


def right() -> Deco:
    return Deco(styles=['margin-left: auto'])


def sticky() -> Deco:
    return Deco(attrs={'data-sticky': ''})


def badge(text: str) -> Wrapper:
    return Wrapper(
        content=(
            '<div style="position:relative;margin-top:calc(var(--el-gap) + 1.4em)">'
            '<span style="position:absolute;top:-1.4em;left:50%;'
            'transform:translateX(-50%);z-index:1;'
            'background:var(--el-surface0);border:1px solid var(--el-border);'
            'border-radius:0.4em;padding:0 8px;font-size:0.8em;font-weight:600;'
            'line-height:1.4;white-space:nowrap;display:inline-flex;'
            'align-items:center;gap:4px">'
            f'{text}</span>'
            '__ELF_0__'
            '</div>'
        ),
        func_name="badge",
    )
