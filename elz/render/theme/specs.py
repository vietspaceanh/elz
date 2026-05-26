from __future__ import annotations

from dataclasses import dataclass, field
from pygments.style import Style


BORDER_DARK = "#42434B"
BORDER_LIGHT = "#acb0be"

PALETTES: dict[str, dict[str, str]] = {
    "catppuccin_mocha": {
        "bg": "#1e1e2e", "text": "#cdd6f4",
        "border": BORDER_DARK, "link": "#89b4fa",
        "surface0": "#313244", "surface1": "#45475a", "surface2": "#585b70",
        "blue": "#89b4fa", "green": "#a6e3a1", "orange": "#fab387",
        "purple": "#cba6f7", "red": "#f38ba8", "teal": "#94e2d5",
        "yellow": "#f9e2af", "pink": "#f5c2e7", "gray": "#6c7086",
    },
    "catppuccin_latte": {
        "bg": "#e6e9ef", "text": "#4c4f69",
        "border": BORDER_LIGHT, "link": "#1c4ed8",
        "surface0": "#d0d4dd", "surface1": "#d0d4dd", "surface2": "#acb0be",
        "blue": "#1c4ed8", "green": "#2d7a1e", "orange": "#d95b0a",
        "purple": "#6d28d9", "red": "#d20f39", "teal": "#179299",
        "yellow": "#df8e1d", "pink": "#ea76cb", "gray": "#4f5368",
    },
    "nord": {
        "bg": "#2e3440", "text": "#d8dee9",
        "border": BORDER_DARK, "link": "#81a1c1",
        "surface0": "#3b4252", "surface1": "#434c5e", "surface2": "#4c566a",
        "blue": "#81a1c1", "green": "#a3be8c", "orange": "#d08770",
        "purple": "#b48ead", "red": "#bf616a", "teal": "#8fbcbb",
        "yellow": "#ebcb8b", "pink": "#b48ead", "gray": "#4c566a",
    },
    "github_dark": {
        "bg": "#0d1117", "text": "#c9d1d9",
        "border": BORDER_DARK, "link": "#58a6ff",
        "surface0": "#21262d", "surface1": "#30363d", "surface2": "#484f58",
        "blue": "#58a6ff", "green": "#3fb950", "orange": "#d29922",
        "purple": "#bc8cff", "red": "#f85149", "teal": "#56d364",
        "yellow": "#d29922", "pink": "#db61a2", "gray": "#484f58",
    },
    "github_light": {
        "bg": "#e6e9ef", "text": "#24292f",
        "border": BORDER_LIGHT, "link": "#0969da",
        "surface0": "#e8eaed", "surface1": "#d0d7de", "surface2": "#afb8c1",
        "blue": "#0969da", "green": "#1a7f37", "orange": "#9a6700",
        "purple": "#8250df", "red": "#cf222e", "teal": "#2da44e",
        "yellow": "#9a6700", "pink": "#bf3989", "gray": "#656d76",
    },
    "one_dark_pro": {
        "bg": "#282c34", "text": "#abb2bf",
        "border": BORDER_DARK, "link": "#61afef",
        "surface0": "#353b45", "surface1": "#3e4452", "surface2": "#5c6370",
        "blue": "#61afef", "green": "#98c379", "orange": "#d19a66",
        "purple": "#c678dd", "red": "#e06c75", "teal": "#56b6c2",
        "yellow": "#e5c07b", "pink": "#c678dd", "gray": "#5c6370",
    },
    "kanagawa_wave": {
        "bg": "#1f1f28", "text": "#dcd7ba",
        "border": BORDER_DARK, "link": "#7e9cd8",
        "surface0": "#363646", "surface1": "#54546d", "surface2": "#72727e",
        "blue": "#7e9cd8", "green": "#98bb6c", "orange": "#ffa066",
        "purple": "#957fb8", "red": "#e46876", "teal": "#7fb4ca",
        "yellow": "#dca561", "pink": "#b8b4d0", "gray": "#72727e",
    },
    "thithi": {
        "bg": "#F8E0DD", "text": "#4c4f69",
        "border": BORDER_LIGHT, "link": "#6d54e9",
        "surface0": "#d8dae2", "surface1": "#d0d4dd", "surface2": "#b0b4be",
        "blue": "#6d54e9", "green": "#44B17E", "orange": "#ffb96e",
        "purple": "#8868b8", "red": "#ff739d", "teal": "#489898",
        "yellow": "#c88078", "pink": "#d088b0", "gray": "#505870",
    },
}


@dataclass
class ThemeConfig:
    name: str
    pygments_style: type[Style]
    padding: str
    margin: str
    border_radius: str
    max_width: str
    gap: str
    font_family: str
    font_size: str
    code_font_family: str
    code_font_size: str
    indent: str = "1em"
    opacity: str = "0.85"
    sidebar_width: str = "280px"
    toc_width: str = "260px"
    header_height: str = "64px"
    footer_height: str = "48px"
    palette: dict = field(default_factory=dict)
    css: str = ""