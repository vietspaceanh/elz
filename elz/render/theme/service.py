from __future__ import annotations
import re
from typing import Literal

from pygments.formatters.html import HtmlFormatter
from .pygments import _build_pygments_style
from .specs import PALETTES, ThemeConfig
from .integration import propagate_theme


def _build_config(name: str) -> ThemeConfig:
    palette = dict(PALETTES[name])

    return ThemeConfig(
        name=name,
        palette=palette,
        pygments_style=_build_pygments_style(name, palette),
        padding="10px",
        margin="0",
        border_radius="14px",
        gap="12px",
        max_width="95%",
        font_family="HarmonyOS Sans, Inter, Ubuntu, Noto Sans, sans-serif",
        font_size="1em",
        code_font_family='"Iosevka SS02", monospace',
        code_font_size="1em",
        css="",
    )


PRESET_FACTORIES = {name: lambda n=name: _build_config(n) for name in PALETTES}
DEFAULT_THEME = "kanagawa_wave"


class ThemeService:
    def __init__(self):
        self._config = PRESET_FACTORIES[DEFAULT_THEME]()
        self._formatter: HtmlFormatter | None = None
        self._css_cache: str | None = None

    @property
    def config(self) -> ThemeConfig:
        return self._config

    def use(self, preset_or_config: str | ThemeConfig | None = None, /, **overrides):
        if preset_or_config is None:
            pass
        elif isinstance(preset_or_config, str):
            factory = PRESET_FACTORIES.get(preset_or_config)
            if factory is None:
                raise ValueError(
                    f"Unknown theme: {preset_or_config!r}. "
                    f"Available: {list(PRESET_FACTORIES)}"
                )
            self._config = factory()
        elif isinstance(preset_or_config, ThemeConfig):
            self._config = preset_or_config
        else:
            raise TypeError(
                f"Expected str, ThemeConfig, or None, got {type(preset_or_config).__name__}"
            )

        for k, v in overrides.items():
            if not hasattr(self._config, k):
                raise TypeError(f"ThemeConfig has no field {k!r}")
            setattr(self._config, k, v)

        self._invalidate()
        propagate_theme(self._config)

    def reset(self):
        self.use(DEFAULT_THEME)

    def _invalidate(self):
        self._formatter = None
        self._css_cache = None

    def get_formatter(self) -> HtmlFormatter:
        if self._formatter is None:
            self._formatter = HtmlFormatter(style=self._config.pygments_style)
        return self._formatter

    def get_css(self, pygments: bool = True) -> str:
        if self._css_cache is None:
            pyg = self.get_formatter().get_style_defs(".highlight")
            pyg = re.sub(
                r'(\.highlight)((?:\s+\.\w+)?)',
                lambda m: f'.highlight, .hl{m.group(2)}' if not m.group(2)
                         else f'.highlight{m.group(2)}, .hl{m.group(2)}',
                pyg
            )
            self._pygments_css = pyg
            t = self._config
            p = t.palette
            bg = p["bg"]
            _r, _g, _b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
            self._css_cache = f"""
            :root {{
                --el-bg: {bg};
                --el-text: {p["text"]};
                --el-border: {p["border"]};
                --el-padding: {t.padding};
                --el-margin: {t.margin};
                --el-border-radius: {t.border_radius};
                --el-gap: {t.gap};
                --el-max-width: {t.max_width};
                --el-link: {p["link"]};
                --el-font-family: {t.font_family};
                --el-font-size: {t.font_size};
                --el-code-family: {t.code_font_family};
                --el-code-size: {t.code_font_size};
                --el-code-bg: transparent;
                --el-dev-link: {p["link"]};
                --el-dev-link-bg: rgba({_r},{_g},{_b},0.85);
                --el-opacity: {t.opacity};
                --el-indent: {t.indent};
                --el-sidebar-width: {t.sidebar_width};
                --el-toc-width: {t.toc_width};
                --el-header-height: {t.header_height};
                --el-footer-height: {t.footer_height};
            }}
            .el-page {{
                max-width: var(--el-max-width);
                width: 100%;
                margin: 0 auto;
            }}
            """
            if t.css:
                self._css_cache += "\n" + t.css

        if pygments:
            return self._pygments_css + "\n" + self._css_cache
        return self._css_cache


theme = ThemeService()

def set_theme(
    name_or_config: Literal[
        "catppuccin_mocha",
        "catppuccin_latte",
        "nord",
        "github_dark",
        "github_light",
        "one_dark_pro",
        "kanagawa_wave",
        "thithi",
    ],
    **overrides
):
    theme.use(name_or_config, **overrides)
