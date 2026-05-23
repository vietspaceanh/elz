from __future__ import annotations

from .specs import ThemeConfig


DARK_PRESETS = frozenset({
    "catppuccin_mocha", "nord", "github_dark", "one_dark_pro", "kanagawa_wave",
})


def propagate_theme(config: ThemeConfig) -> None:
    _sync_external_theme(config, "deff.theme", "deff_theme")
    _sync_external_theme(config, "ttplot.theme", "ttplot_theme")


def _sync_external_theme(config: ThemeConfig, module_path: str, attr_name: str) -> None:
    try:
        import importlib
        mod = importlib.import_module(module_path)
        theme_obj = getattr(mod, attr_name)
    except (ImportError, AttributeError):
        return
    theme_obj.use(
        name=config.name,
        mode="dark" if config.name in DARK_PRESETS else "light",
        proxy=dict(config.palette),
    )
