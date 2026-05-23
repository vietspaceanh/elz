from __future__ import annotations

_PAGE_CSS = """
.el {
    contain: layout style paint;
    background: var(--el-bg);
    color: var(--el-text);
    padding: var(--el-padding);
    margin: var(--el-margin);
    max-width: var(--el-max-width);
    font-family: var(--el-font-family);
    font-size: var(--el-font-size);
    line-height: calc(1em + var(--el-gap)*0.6);
}
.el-text li:has(> p) + li:has(> p) { margin-top: var(--el-gap); }
.el-dev li:has(> p) + li:has(> p) { margin-top: var(--el-gap); }
.el th, .el td { border: 1px solid var(--el-border); }
.el .highlight {
    background: var(--el-code-bg);
    border: 1px solid var(--el-border);
    border-radius: var(--el-border-radius);
    padding: var(--el-padding);
}
.el .highlight pre {
    margin: 0;
    font-family: var(--el-code-family);
    font-size: var(--el-code-size);
}
.el code:not(pre code) { font-size: var(--el-code-size); font-family: var(--el-code-family); }
.el code.hl { background: transparent; }
.el-grid-item {
    display: flex;
    flex-direction: column;
    min-height: 0;
    padding: 0 calc(var(--el-gap) * 2);
}
.el-grid-item + .el-grid-item {
    border-left: 1px solid var(--el-border);
}
.el-grid-item svg { max-width: 100%; height: auto; }
.el-grid-item[data-sticky] {
    position: sticky;
    top: 0;
    align-self: flex-start;
    max-height: 100vh;
    overflow-y: auto;
}
.el-row {
    min-width: 0;
}
"""

_MARKDOWN_CSS = """
.el h1 { margin: calc(var(--el-gap) * 3) 0 0; font-size: 2em; font-weight: 700; }
.el h2 { margin: calc(var(--el-gap) * 2.7) 0 0; font-size: 1.5em; font-weight: 700; }
.el h3 { margin: calc(var(--el-gap) * 2.5) 0 0; font-size: 1.25em; font-weight: 600; }
.el h4 { margin: calc(var(--el-gap) * 2.25) 0 0; font-size: 1.1em; font-weight: 600; }
.el p { margin-bottom: 0; }
.el-text ul, .el-text ol { margin-bottom: 0; padding-left: calc(var(--el-indent) * 2); }
.el-text li { margin-bottom: 0; }
.el-text li + li { margin-top: var(--el-gap); }
.el pre { margin-bottom: 0; }
.el blockquote { margin-bottom: 0; padding: 0 1em; opacity: var(--el-opacity); }
.el table { margin-bottom: 0; border-collapse: collapse; width: 100%; }
.el th, .el td { padding: calc(var(--el-padding) * 0.6) var(--el-padding); }
.el code { padding: 0.15em 0.3em; border-radius: calc(var(--el-border-radius) * 0.3); }
.el pre code { padding: 0; border-radius: 0; font-size: inherit; }
.el hr { margin-bottom: 0; border: none; border-top: 1px solid; opacity: calc(var(--el-opacity) * 0.35); }
.el a { color: inherit; }
.el img { max-width: 100%; }
"""

_RHYTHM_CSS = """
:is(.el, .el-dev, .el-row, .el-text, .el-fold-section, .el-grid-item) > * {
    margin-top: var(--el-gap);
    margin-bottom: 0;
}
:is(.el, .el-dev, .el-row, .el-fold-section, .el-grid-item) > :first-child {
    margin-top: 0 !important;
}
.el > div[style*="display:flex"],
.el > div[style*="display:grid"],
.el > .el-fold-section { margin-top: var(--el-gap); }
.el-fold-section > div[style*="display:flex"],
.el-fold-section > div[style*="display:grid"] { margin-top: var(--el-gap); }
:is(.el, .el-dev, .el-row, .el-text, .el-fold-section, .el-grid-item) > :is(h1, h2, h3, h4) + * {
    margin-top: calc(var(--el-gap) * 0.5);
}
:is(.el, .el-dev, .el-row, .el-text, .el-fold-section, .el-grid-item) > :is(h1, h2, h3, h4) + :is(h1, h2, h3, h4) {
    margin-top: calc(var(--el-gap) * 1);
}
:is(.el, .el-dev, .el-row, .el-text, .el-fold-section, .el-grid-item) > :is(h1, h2, h3, h4) + :is(table, .highlight) {
    margin-top: var(--el-gap);
}
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

STRUCTURAL_CSS = "\n".join([_PAGE_CSS, _MARKDOWN_CSS, _RHYTHM_CSS, _DEV_CSS])
