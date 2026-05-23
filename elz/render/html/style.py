from __future__ import annotations

_PAGE_CSS = """
.el-element {
    contain: layout style paint;
    background: var(--el-bg);
    color: var(--el-text);
    padding: var(--el-padding);
    margin: var(--el-margin);
    font-family: var(--el-font-family);
    font-size: var(--el-font-size);
}
.el-element li:has(> p) + li:has(> p) { margin-top: var(--el-gap); }
.el-element-dev li:has(> p) + li:has(> p) { margin-top: var(--el-gap); }
.el-element th, .el-element td { border: 1px solid var(--el-border); }
.el-element .highlight {
    background: var(--el-code-bg);
    border: 1px solid var(--el-border);
    border-radius: var(--el-border-radius);
    padding: var(--el-padding);
}
.el-element .highlight pre {
    margin: 0;
    font-family: var(--el-code-family);
    font-size: var(--el-code-size);
}
.el-element code { font-size: var(--el-code-size); }
.el-element code.hl { background: transparent; }
.el-grid-item {
    display: flex;
    flex-direction: column;
    min-height: 0;
}
.el-grid-item svg { max-width: 100%; height: auto; }
.el-layout-row {
    min-width: 0;
}
.el-layout-row .el-grid-item {
    padding: var(--el-padding);
}
.el-layout-row .el-grid-item + .el-grid-item {
    border-left: 1px solid var(--el-border);
    padding-left: calc(var(--el-padding) * 2);
}
.el-layout-row .el-grid-item[data-sticky] {
    position: sticky;
    top: 0;
    align-self: flex-start;
    max-height: 100vh;
    overflow-y: auto;
}
.el-layout-text {
    padding: var(--el-padding);
}
"""

_MARKDOWN_CSS = """
.el-element h1 { margin: calc(var(--el-gap) * 1.75) 0 0; font-size: 2em; font-weight: 700; }
.el-element h2 { margin: calc(var(--el-gap) * 1.5) 0 0; font-size: 1.5em; font-weight: 700; }
.el-element h3 { margin: calc(var(--el-gap) * 1.25) 0 0; font-size: 1.25em; font-weight: 600; }
.el-element h4 { margin: calc(var(--el-gap) * 1) 0 0; font-size: 1.1em; font-weight: 600; }
:where(.el-element) p { margin: 0; }
:where(.el-element) ul, :where(.el-element) ol { margin: 0; padding-left: calc(var(--el-indent) * 2); }
:where(.el-element) li { margin: 0; }
:where(.el-element) pre { margin: 0; }
:where(.el-element) blockquote { margin: 0; padding: 0 1em; opacity: var(--el-opacity); }
:where(.el-element) table { margin: 0; border-collapse: collapse; width: 100%; }
:where(.el-element) th, :where(.el-element) td { padding: calc(var(--el-padding) * 0.6) var(--el-padding); }
:where(.el-element) code { padding: 0.15em 0.3em; border-radius: calc(var(--el-border-radius) * 0.3); }
:where(.el-element) pre code { padding: 0; border-radius: 0; font-size: inherit; }
:where(.el-element) hr { margin: 0; border: none; border-top: 1px solid; opacity: calc(var(--el-opacity) * 0.35); }
:where(.el-element) a { color: inherit; }
:where(.el-element) img { max-width: 100%; }
:where(.el-element) > :last-child { margin-bottom: 0; }
"""

_RHYTHM_CSS = """
:is(.el-element, .el-element-dev, .el-layout-row, .el-layout-text, .el-fold-section, .el-grid-item) > * {
    margin-top: var(--el-gap);
}
:is(.el-element, .el-element-dev, .el-layout-row, .el-layout-text, .el-fold-section, .el-grid-item) > :first-child {
    margin-top: 0 !important;
}
.el-element > div[style*="display:flex"],
.el-element > div[style*="display:grid"],
.el-element > .el-fold-section { margin-top: var(--el-gap); }
.el-fold-section > div[style*="display:flex"],
.el-fold-section > div[style*="display:grid"] { margin-top: var(--el-gap); }
:is(.el-element, .el-element-dev, .el-layout-row, .el-layout-text, .el-fold-section, .el-grid-item) > :is(h1, h2, h3, h4) + * {
    margin-top: calc(var(--el-gap) * 0.25);
}
"""

_DEV_CSS = """
.el-element-dev { position: relative; padding-top: 1.2em; }
.el-element-dev .el-dev-link {
    display: none; position: absolute; top: 0; right: 4px;
    z-index: 10; font-size: 0.7em;
    font-family: var(--el-code-family); white-space: nowrap;
}
.el-element-dev:hover .el-dev-link { display: inline; }
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
