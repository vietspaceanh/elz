from __future__ import annotations

from pygments.style import Style
from pygments.token import (
    Comment, Error, Generic, Keyword, Literal, Name, Number, Operator,
    Punctuation, String,
)


TOKEN_PROXY: dict[tuple, str | tuple[str, str]] = {
    Comment:              ("gray", "italic"),
    Comment.Hashbang:     ("gray", "italic"),
    Comment.Multiline:    ("gray", "italic"),
    Comment.Preproc:      "orange",
    Comment.Single:       ("gray", "italic"),
    Comment.Special:      ("gray", "bold italic"),
    Error:                ("red", "bg:surface0"),
    Generic.Heading:      ("blue", "bold"),
    Generic.Subheading:   ("blue", "bold"),
    Keyword:              "purple",
    Keyword.Constant:     "orange",
    Keyword.Declaration:  "purple",
    Keyword.Namespace:    "purple",
    Keyword.Type:         "red",
    Literal:              "text",
    Name.Attribute:       "blue",
    Name.Builtin:         "red",
    Name.Class:           "yellow",
    Name.Constant:        "orange",
    Name.Decorator:       "pink",
    Name.Entity:          "pink",
    Name.Exception:       "red",
    Name.Function:        "blue",
    Name.Label:           "yellow",
    Name.Namespace:       "yellow",
    Name.Tag:             "purple",
    Name.Variable:        "text",
    Number:               "orange",
    Operator:             "blue",
    Operator.Word:        "purple",
    Punctuation:          "text",
    String:               "green",
    String.Doc:           "gray",
    String.Escape:        "pink",
    String.Interpol:      "pink",
}


def _build_pygments_style(name: str, palette: dict[str, str]) -> type[Style]:
    styles = {}
    for token, spec in TOKEN_PROXY.items():
        if isinstance(spec, str):
            proxy = spec
            extra = ""
        else:
            proxy, extra = spec

        color = palette[proxy]
        if "bg:" in extra:
            for key, val in palette.items():
                extra = extra.replace(f"bg:{key}", f"bg:{val}")

        parts = [color]
        if extra:
            parts.append(extra)
        styles[token] = " ".join(parts)

    return type(
        name,
        (Style,),
        {
            "background_color": palette["bg"],
            "highlight_color": palette["surface0"],
            "styles": styles,
        },
    )
