from __future__ import annotations

import functools
import inspect
import linecache
import os
import re
import subprocess

_SKIP_DIRS = frozenset({
    ".venv", "venv", "node_modules", "__pycache__",
    ".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache",
})
_FOUND_SOURCE: tuple[str, int] | None = None


# ── Public API ──


def resolve_func_source(func, source_text, func_globals):
    snippet = source_text.strip()[:120]
    try:
        f = inspect.getsourcefile(func)
        ln = inspect.getsourcelines(func)[1]
        if f and os.path.isfile(f):
            return (os.path.abspath(f), ln)
    except (TypeError, OSError):
        pass
    return _search_project(snippet, func_globals)


def resolve_inline_source(frame):
    module = frame.f_globals.get("__name__", "__main__").rsplit(".", 1)[-1]
    if module in ("__main__", "__mp_main__"):
        module = "_main"
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    source = (filename, lineno)

    lines = linecache.getlines(filename, frame.f_globals)
    start = max(0, lineno - 1 - 2)
    context_lines = lines[start:start + 5]
    source_text = ''.join(context_lines)

    caller_line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
    m = re.match(r"^\s*(\w+)\s*=\s*el\s*\(", caller_line)
    name = (
        f"{module}__{m.group(1)}" if m
        else f"{module}__inline@{os.path.basename(filename)}:{lineno}"
    )

    snippet = source_text.strip()[:120]
    if snippet:
        real_file = frame.f_globals.get("__file__")
        if real_file and os.path.isfile(real_file) and os.path.abspath(real_file) != os.path.abspath(filename):
            real_ln = _find_in_file(snippet, real_file)
            if real_ln is not None:
                source = (os.path.abspath(real_file), real_ln + (lineno - 1 - start))
        if not os.path.isfile(source[0]):
            hint = _find_hint_file()
            if hint:
                real_ln = _find_in_file(snippet, hint)
                if real_ln is not None:
                    source = (os.path.abspath(hint), real_ln + (lineno - 1 - start))
        if not os.path.isfile(source[0]) and caller_line.strip():
            found = _search_project(caller_line.strip()[:120], frame.f_globals)
            if found:
                source = found
    return name, source, source_text


@functools.lru_cache(maxsize=32)
def find_name_line(mod_file: str) -> dict[str, int]:
    name_re = re.compile(r"^\s*(?:(?:def\s+(\w+)\b|class\s+(\w+)\b|(\w+)\s*=)\s*)")
    lookup = {}
    try:
        with open(mod_file) as f:
            for i, line in enumerate(f, 1):
                m = name_re.match(line)
                if m:
                    lookup[m.group(1) or m.group(2) or m.group(3)] = i
    except OSError:
        pass
    return lookup


# ── Project search ──


def _search_project(snippet: str, func_globals: dict) -> tuple[str, int] | None:
    global _FOUND_SOURCE
    if _FOUND_SOURCE is not None:
        ln = _find_in_file(snippet, _FOUND_SOURCE[0])
        if ln:
            return (_FOUND_SOURCE[0], ln)
    root = _detect_root(func_globals)
    if not root:
        return
    needle = _pick_needle(snippet)
    found = _search_rg(needle, snippet, root) or _search_fallback(snippet, root)
    if found:
        _FOUND_SOURCE = found
    return found


def _detect_root(func_globals: dict) -> str:
    for key in ("__vsc_ipynb_file__", "__file__"):
        val = func_globals.get(key)
        if val and os.path.isfile(val):
            return os.path.dirname(os.path.abspath(val))
    return os.getcwd()


def _pick_needle(snippet: str) -> str:
    lines = snippet.split("\n")
    first = lines[0].strip()[:120] if lines else ""
    if first.startswith("@"):
        for line in lines[1:]:
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("class "):
                return stripped[:120]
    return first or snippet[:80]


def _search_rg(needle: str, snippet: str, root: str) -> tuple[str, int] | None:
    try:
        proc = subprocess.run(
            ["rg", "-n", "--no-heading", "--color", "never", "-F",
             "--glob", "*.py",
             "--glob", "!.venv/**", "--glob", "!venv/**",
             "--glob", "!node_modules/**", "--glob", "!__pycache__/**",
             "--glob", "!.git/**",
             needle, root],
            capture_output=True, text=True, timeout=2,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.strip().split("\n"):
                parts = line.split(":", 2)
                if len(parts) >= 2:
                    fp = os.path.abspath(parts[0])
                    ln = _find_in_file(snippet, fp)
                    if ln:
                        return (fp, ln)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass
    return


def _search_fallback(snippet: str, root: str) -> tuple[str, int] | None:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in _SKIP_DIRS]
        for f in filenames:
            if not f.endswith(".py"):
                continue
            p = os.path.join(dirpath, f)
            try:
                with open(p, errors="ignore") as fp:
                    content = fp.read()
                idx = content.find(snippet)
                if idx >= 0:
                    return (os.path.abspath(p), content[:idx].count("\n") + 1)
            except OSError:
                continue
    return


# ── Utilities ──


def _find_in_file(text: str, filepath: str) -> int | None:
    try:
        with open(filepath) as f:
            content = f.read()
        idx = content.find(text)
        if idx >= 0:
            return content[:idx].count("\n") + 1
    except OSError:
        pass
    return


def _find_hint_file() -> str | None:
    f = inspect.currentframe()
    while f:
        mod = f.f_globals.get("__name__", "")
        if mod.startswith("elf"):
            f = f.f_back
            continue
        fn = f.f_globals.get("__file__")
        if fn and os.path.isfile(fn):
            return os.path.abspath(fn)
        f = f.f_back
    return