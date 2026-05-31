from .specs import Mods


def center(pct: float | None = None) -> Mods:
    styles = ['margin-left: auto', 'margin-right: auto']
    if pct is not None:
        styles.append(f'width: {pct * 100}%')
    return Mods(styles=styles)


def right() -> Mods:
    return Mods(styles=['margin-left: auto'])


def sticky() -> Mods:
    return Mods(attrs={'data-sticky': ''})
