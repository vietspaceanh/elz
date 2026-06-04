from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class ElementSpec:
    func_name: str | None
    name: str | None
    args: dict = field(default_factory=dict)
    deps: list[ElementSpec] = field(default_factory=list)
    format: str = "md"
    content: str | None = None
    source: tuple[str, int] | None = None
    css: str = ""
    css_variants: dict | None = None
    decos: list[Deco] = field(default_factory=list)
    weight: int | float = 1
    adhoc_fn: Callable[[], str] | None = None


@dataclass
class Deco:
    """A single decoration applied to an element via the @ operator."""
    classes: list[str] = field(default_factory=list)
    classes_remove: list[str] = field(default_factory=list)
    classes_toggle: list[str] = field(default_factory=list)
    styles: list[str] = field(default_factory=list)
    attrs: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def parse(modifier: str) -> Deco:
        if modifier.startswith('!.'):
            return Deco(classes_remove=[modifier[2:]])
        if modifier.startswith('?.'):
            return Deco(classes_toggle=[modifier[2:]])
        if modifier.startswith('.'):
            return Deco(classes=[modifier[1:]])
        if '=' in modifier:
            k, v = modifier.split('=', 1)
            return Deco(attrs={k: v})
        if ':' in modifier:
            return Deco(styles=[modifier])
        return Deco(attrs={modifier: ''})

    def apply_classes(self, base: list[str]) -> list[str]:
        result = list(base)
        result.extend(self.classes)
        for c in self.classes_remove:
            if c in result:
                result.remove(c)
        for c in self.classes_toggle:
            if c in result:
                result.remove(c)
            else:
                result.append(c)
        return result


@dataclass
class Wrapper:
    """A structural wrapper applied to an element (e.g., badge)."""
    content: str
    css: str = ""
    func_name: str | None = None


def replay_decos(decos: list[Deco]) -> tuple[list[str], list[str], dict[str, str]]:
    """Replay a list of decorations to compute final classes, styles, attrs."""
    classes: list[str] = []
    styles: list[str] = []
    attrs: dict[str, str] = {}
    for d in decos:
        classes = d.apply_classes(classes)
        styles.extend(d.styles)
        attrs.update(d.attrs)
    return classes, styles, attrs


def sanitize_alias(func_name: str, args: dict) -> str:
    if not args:
        return func_name
    parts = [v.name if hasattr(v, "name") else str(v) for v in args.values()]
    raw = "_".join(parts)
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", raw)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return f"{func_name}__{sanitized}"
