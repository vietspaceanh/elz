from __future__ import annotations

import html
import re
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Mods:
    classes: list[str] = field(default_factory=list)
    classes_remove: list[str] = field(default_factory=list)
    classes_toggle: list[str] = field(default_factory=list)
    styles: list[str] = field(default_factory=list)
    attrs: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def parse(modifier: str) -> Mods:
        if modifier.startswith('!.'):
            return Mods(classes_remove=[modifier[2:]])
        if modifier.startswith('?.'):
            return Mods(classes_toggle=[modifier[2:]])
        if modifier.startswith('.'):
            return Mods(classes=[modifier[1:]])
        if '=' in modifier:
            k, v = modifier.split('=', 1)
            return Mods(attrs={k: v})
        if ':' in modifier:
            return Mods(styles=[modifier])
        return Mods(attrs={modifier: ''})

    def merge(self, other: Mods) -> Mods:
        return Mods(
            classes=self.classes + other.classes,
            classes_remove=self.classes_remove + other.classes_remove,
            classes_toggle=self.classes_toggle + other.classes_toggle,
            styles=self.styles + other.styles,
            attrs={**self.attrs, **other.attrs},
        )

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

    def wrap_content(self, content: str) -> str:
        classes = self.apply_classes(['el-mods'])
        style = ';'.join(self.styles)
        attrs_str = ''
        for k, v in self.attrs.items():
            if v == '':
                attrs_str += f' {k}'
            else:
                attrs_str += f' {k}="{html.escape(str(v))}"'
        style_attr = f' style="{html.escape(style)}"' if style else ''
        return f'<div class="{" ".join(classes)}"{style_attr}{attrs_str}>\n{content}\n</div>'


@dataclass
class ElementSpec:
    func_name: str | None
    name: str | None
    args: dict = field(default_factory=dict)
    deps: list[ElementSpec] = field(default_factory=list)
    format: str = "md"
    content: str | None = None
    source: tuple[str, int] | None = None
    source_text: str | None = None
    css: str = ""
    css_variants: dict | None = None
    mods: Mods | None = None
    weight: int | float = 1
    adhoc_fn: Callable[[], str] | None = None


def sanitize_alias(func_name: str, args: dict) -> str:
    if not args:
        return func_name
    parts = [v.name if hasattr(v, "name") else str(v) for v in args.values()]
    raw = "_".join(parts)
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", raw)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return f"{func_name}__{sanitized}"
