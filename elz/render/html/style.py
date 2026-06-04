from __future__ import annotations

# Spacing multipliers (scale against variables like --el-gap)
_GAP_STANDARD = 1
_H1_TOP_EM = 1.5
_H2_TOP_EM = 1.3
_H3_TOP_EM = 1.3
_H4_TOP_EM = 1.3
_H1_SIZE = 1.75
_H2_SIZE = 1.45
_H3_SIZE = 1.3
_H4_SIZE = 1.2
_LINE_HEIGHT_FACTOR = 0.5
_HEADING_LINE_HEIGHT = 1.2
_GRID_PADDING_X = 2.5
_CELL_PADDING = 0.6
_LIST_INDENT = 2
_LI_GAP = 0.33
_LI_NESTED_GAP = 0.5
_P_LIST_GAP = 0.5

# All structural wrapper classes are transparent (no margin on themselves)
_TRANSPARENT_WRAPPERS = ".el-row, .el-grid-item, .el-dev, .el-fold-section, .el-text, .el-deco"
# All containers that can hold markdown-rendered content
_CONTENT_SCOPES = ".el, .el-dev, .el-row, .el-fold-section, .el-grid-item, .el-text, .el-deco"

_PAGE_CSS = f"""
/* Root container */
.el {{
    contain: layout style paint;
    background: var(--el-bg);
    color: var(--el-text);
    padding: var(--el-padding);
    margin: var(--el-margin);
    max-width: var(--el-max-width);
    font-family: var(--el-font-family);
    font-size: var(--el-font-size);
    line-height: calc(1em + var(--el-gap)*{_LINE_HEIGHT_FACTOR});
}}

/* Consistent list spacing between all items */
:is({_CONTENT_SCOPES}) li + li {{ margin-top: calc(var(--el-gap) * {_LI_GAP}); }}
/* Nested list spacing */
:is({_CONTENT_SCOPES}) li > ul, :is({_CONTENT_SCOPES}) li > ol {{ margin-top: calc(var(--el-gap) * {_LI_NESTED_GAP}); }}

/* Grid item layout */
.el-grid-item {{
    display: flex;
    flex-direction: column;
    min-height: 0;
    padding: 0 calc(var(--el-gap) * {_GRID_PADDING_X});
}}
.el-grid-item + .el-grid-item {{
    border-left: 1px solid var(--el-border);
}}
.el-grid-item svg {{ max-width: 100%; height: auto; }}
.el-grid-item[data-sticky] {{
    position: sticky;
    top: 0;
    align-self: flex-start;
    max-height: 100vh;
    overflow-y: auto;
}}

/* Row container */
.el-row {{
    min-width: 0;
}}
"""

_WRAPPERS_RULE = f"""
/* All structural wrappers are transparent */
:is({_TRANSPARENT_WRAPPERS}) {{
    margin-top: 0 !important;
}}
"""

_MARKDOWN_CSS = f"""
:is({_CONTENT_SCOPES}) h1 {{ font-size: {_H1_SIZE}em; font-weight: 600; line-height: {_HEADING_LINE_HEIGHT}; }}
:is({_CONTENT_SCOPES}) h2 {{ font-size: {_H2_SIZE}em; font-weight: 600; line-height: {_HEADING_LINE_HEIGHT}; }}
:is({_CONTENT_SCOPES}) h3 {{ font-size: {_H3_SIZE}em; font-weight: 600; line-height: {_HEADING_LINE_HEIGHT}; }}
:is({_CONTENT_SCOPES}) h4 {{ font-size: {_H4_SIZE}em; font-weight: 600; line-height: {_HEADING_LINE_HEIGHT}; }}
:is({_CONTENT_SCOPES}) p {{ margin-bottom: 0; }}
:is({_CONTENT_SCOPES}) ul, :is({_CONTENT_SCOPES}) ol {{ margin-bottom: 0; padding-left: calc(var(--el-indent) * {_LIST_INDENT}); }}
:is({_CONTENT_SCOPES}) li {{ margin-bottom: 0; }}
:is({_CONTENT_SCOPES}) ol > li::marker {{ font-weight: 600; }}
:is({_CONTENT_SCOPES}) li > p {{ margin-top: 0; margin-bottom: 0; }}
:is({_CONTENT_SCOPES}) li > span.math {{ display: inline-block; margin: 0; }}
:is({_CONTENT_SCOPES}) pre {{ margin-bottom: 0; }}
:is({_CONTENT_SCOPES}) blockquote {{ margin-bottom: 0; padding: 0 1em; opacity: var(--el-opacity); }}
:where({_CONTENT_SCOPES}) table {{ margin-bottom: 0; border-collapse: separate; border-spacing: 0; width: 100%; border: 1px solid var(--el-border); border-radius: var(--el-border-radius); overflow: hidden; }}
:where({_CONTENT_SCOPES}) table {{ margin-top: calc(var(--el-gap) * {_GAP_STANDARD}); }}
:is({_CONTENT_SCOPES}) th {{ padding: calc(var(--el-padding) * {_CELL_PADDING}) var(--el-padding); border: none; border-right: 1px solid var(--el-border); border-bottom: 1px solid var(--el-border); background: rgba(128,128,128,0.04); text-align: center; }}
:is({_CONTENT_SCOPES}) td {{ padding: calc(var(--el-padding) * {_CELL_PADDING}) var(--el-padding); border: none; border-right: 1px solid var(--el-border); border-bottom: 1px solid var(--el-border); }}
:is({_CONTENT_SCOPES}) th:last-child, :is({_CONTENT_SCOPES}) td:last-child {{ border-right: none; }}
:is({_CONTENT_SCOPES}) tbody tr:last-child td, :is({_CONTENT_SCOPES}) tfoot tr:last-child th, :is({_CONTENT_SCOPES}) tfoot tr:last-child td {{ border-bottom: none; }}
:is({_CONTENT_SCOPES}) code {{ padding: 0.15em 0.3em; border-radius: calc(var(--el-border-radius) * 0.3); color: var(--el-code-color); font-size: var(--el-code-size); font-family: var(--el-code-family); }}
:is({_CONTENT_SCOPES}) pre code {{ padding: 0; border-radius: 0; font-size: inherit; background: transparent; color: inherit; }}
:is({_CONTENT_SCOPES}) hr {{ margin-bottom: 0; border: none; border-top: 1px solid; opacity: calc(var(--el-opacity) * 0.35); }}
:is({_CONTENT_SCOPES}) a {{ color: var(--el-link-color); }}
:is({_CONTENT_SCOPES}) img {{ max-width: 100%; }}
:is({_CONTENT_SCOPES}) .highlight {{
    background: var(--el-code-bg);
    border: 1px solid var(--el-border);
    border-radius: var(--el-border-radius);
    padding: var(--el-padding);
}}
.el-code-wrap .highlight {{ border: none; border-radius: 0 0 var(--el-border-radius) var(--el-border-radius); }}
:is({_CONTENT_SCOPES}) .highlight pre {{
    margin: 0;
    font-family: var(--el-code-family);
    font-size: var(--el-code-size);
}}
:is({_CONTENT_SCOPES}) code:not(pre code) {{ font-size: var(--el-code-size); font-family: var(--el-code-family); }}
:is({_CONTENT_SCOPES}) code.hl {{ background: transparent; }}
:is({_CONTENT_SCOPES}) .math {{ margin-top: calc(var(--el-gap) * {_GAP_STANDARD}); margin-bottom: 0; }}
:is({_CONTENT_SCOPES}) .math .katex-display {{ margin: 0; }}
"""

_RHYTHM_CSS = f"""
/* Standard vertical rhythm — everything gets margin-top: 0.5×gap */
:where({_CONTENT_SCOPES}) > * {{
    margin-top: calc(var(--el-gap) * {_GAP_STANDARD});
    margin-bottom: 0;
}}

/* Headings: em-based top margins */
:is({_CONTENT_SCOPES}) h1 {{ margin-top: {_H1_TOP_EM}em; }}
:is({_CONTENT_SCOPES}) h2 {{ margin-top: {_H2_TOP_EM}em; }}
:is({_CONTENT_SCOPES}) h3 {{ margin-top: {_H3_TOP_EM}em; }}
:is({_CONTENT_SCOPES}) h4 {{ margin-top: {_H4_TOP_EM}em; }}

/* Tighter spacing between paragraph and following list */
:is({_CONTENT_SCOPES}) > p + ul, :is({_CONTENT_SCOPES}) > p + ol {{ margin-top: calc(var(--el-gap) * {_P_LIST_GAP}); }}

/* Flex/grid containers follow the standard gap */
.el > div[style*="display:flex"],
.el > div[style*="display:grid"],
.el > .el-fold-section {{ margin-top: calc(var(--el-gap) * {_GAP_STANDARD}); }}
.el-fold-section > div[style*="display:flex"],
.el-fold-section > div[style*="display:grid"] {{ margin-top: calc(var(--el-gap) * {_GAP_STANDARD}); }}
"""

_MERMAID_CSS = """
.g-wrap { overflow: hidden; width: 100%; height: 500px; cursor: grab;
           border: 1px solid var(--el-border); border-radius: 14px;
           background: var(--el-bg); position: relative; user-select: none; }
.g-wrap img { display: block; width: 100%; height: 100%; object-fit: contain;
                pointer-events: none; }
.g-btn { position: absolute; top: 8px; right: 8px; z-index: 10;
          background: rgba(0,0,0,0.35); backdrop-filter: blur(4px);
          border: 1px solid rgba(255,255,255,0.15); border-radius: 8px;
          color: #ddd; font-size: 0.8em; padding: 3px 10px;
          cursor: pointer; opacity: 0; transition: opacity 0.2s; }
.g-wrap:not(.loaded)::before { content: 'Loading\u2026'; position: absolute; inset: 0; z-index: 5;
    display: flex; align-items: center; justify-content: center;
    color: var(--el-text); opacity: 0.45; font-size: 0.85em; }
.g-wrap:not(.loaded) img { opacity: 0; }
.g-wrap.loaded img { opacity: 1; transition: opacity 0.3s; }
.g-wrap:hover .g-btn { opacity: 1; }
.g-btn:hover { opacity: 1; color: #fff; }
"""

_DEV_CSS = """
.el-dev { position: relative; padding-top: 1.2em; }
.el-dev .el-dev-link {
    display: none; position: absolute; top: 0; right: 4px;
    z-index: 10; font-size: 0.7em;
    font-family: var(--el-code-family); white-space: nowrap;
}
.el-dev:hover .el-dev-link { display: inline; }
.el-dev-link {
    color: var(--el-dev-link); text-decoration: none; opacity: 0.7;
    background: var(--el-dev-link-bg); padding: 1px 6px;
    border-radius: 4px; cursor: default;
}
.el-dev-link:hover { opacity: 1; text-decoration: underline; }
.el-fold-section > summary {
    cursor: pointer; user-select: none; outline: none;
    list-style: none;
}
.el-fold-section > summary::-webkit-details-marker { display: none; }
"""

_CODEFENCE_CSS = f"""
/* 0.5em is the size of the code badge */
.el-code-wrap {{
    position: relative; border: 1px solid var(--el-border);
    border-radius: var(--el-border-radius);
    margin-top: calc(var(--el-gap) * {_GAP_STANDARD} + 0.5em);
}}
""" + """
.el-code-lang-badge {
    position: absolute; top: -0.5em; left: 0.75em; z-index: 1;
    padding: 0 0.5em; font-size: 0.8em; font-family: var(--el-code-family);
    font-weight: 600; letter-spacing: 0.04em; color: var(--el-text);
    background: var(--el-bg);
    border-radius: var(--el-border-radius) 0 var(--el-border-radius) 0;
    user-select: none; pointer-events: none; display: flex; align-items: center;
    gap: 4px; line-height: 1;
}
.el-code-lang-badge .el-code-lang-icon { height: 1.1em; }
.el-code-copy {
    position: absolute; top: calc(var(--el-padding) * 0.66);
    right: calc(var(--el-padding) * 0.66); z-index: 1; opacity: 0;
    transition: opacity 0.15s ease; display: flex; align-items: center;
    justify-content: center; width: 28px; height: 28px;
    border: 1px solid var(--el-border); border-radius: 6px;
    background: color-mix(in srgb, var(--el-surface0) 50%, var(--el-bg));
    color: var(--el-text); cursor: pointer; padding: 0;
}
.el-code-copy .el-code-check-icon { display: none; }
.el-code-copy.el-code-copied .el-code-copy-icon { display: none; }
.el-code-copy.el-code-copied .el-code-check-icon { display: flex; }
.el-code-wrap:hover .el-code-copy { opacity: 0.75; }
.el-code-wrap:hover .el-code-copy:hover {
    opacity: 1;
    background: color-mix(in srgb, var(--el-surface0) 70%, transparent);
}
.el-code-wrap .highlight { overflow-x: auto; }
.el-code-wrap .highlight pre { margin: 0; }
"""

STRUCTURAL_CSS = "\n".join([
    _PAGE_CSS,
    _WRAPPERS_RULE,
    _MARKDOWN_CSS,
    _RHYTHM_CSS,
    _MERMAID_CSS,
    _DEV_CSS,
    _CODEFENCE_CSS,
])
