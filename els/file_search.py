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
_FP_LINES = 20


# ──────────────────────────────── Public API ──────────────────────────────── #

def resolve_func_source(func, source_text, func_globals):
    try:
        f = inspect.getsourcefile(func)
        ln = inspect.getsourcelines(func)[1]
        if f and os.path.isfile(f):
            return (os.path.abspath(f), ln)
    except (TypeError, OSError):
        pass
    return _search_project(source_text, func_globals)


def resolve_inline_source(frame):
    module = frame.f_globals.get("__name__", "__main__").rsplit(".", 1)[-1]
    if module in ("__main__", "__mp_main__"):
        module = "_main"
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    source = (filename, lineno)

    lines = linecache.getlines(filename, frame.f_globals)
    context_lines = lines[lineno - 1 : lineno - 1 + _FP_LINES]
    caller_line = context_lines[0] if context_lines else ""
    source_text = ''.join(context_lines)

    m = re.match(r"^\s*(\w+)\s*=\s*el\s*\(", caller_line)
    name = (
        f"{module}__{m.group(1)}" if m
        else f"{module}__inline@{os.path.basename(filename)}:{lineno}"
    )

    if source_text.strip():
        found = _search_project(source_text, frame.f_globals)
        if found:
            source = found
    return name, source, source_text


@functools.lru_cache(maxsize=32)
def find_name_line(mod_file: str) -> dict[str, int]:
    name_re = re.compile(r"^\s*(?:(?:(?:async\s+)?def\s+(\w+)\b|class\s+(\w+)\b|(\w+)\s*(?::[^=]*)?=(?!=))\s*)")
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


# ────────────────────────────── Project search ────────────────────────────── #

def _search_project(snippet: str, func_globals: dict) -> tuple[str, int] | None:
    lines = snippet.split("\n")
    if not lines:
        return
    fingerprint = "\n".join(lines[:_FP_LINES])
    root = _detect_root(func_globals)
    if not root:
        return
    return _search_rg(fingerprint, root) or _search_fallback(fingerprint, root)


def _detect_root(func_globals: dict) -> str:
    for key in ("__vsc_ipynb_file__", "__file__"):
        val = func_globals.get(key)
        if val and os.path.isfile(val):
            return os.path.dirname(os.path.abspath(val))
    return os.getcwd()


def _search_rg(fingerprint: str, root: str) -> tuple[str, int] | None:
    fp_lines = fingerprint.split('\n')
    rg_skip = [g for d in sorted(_SKIP_DIRS) for g in ("--glob", f"!{d}/**")]
    try:
        proc = subprocess.run(
            ["rg", "-n", "--no-heading", "--color", "never", "-F", "-U",
             "--glob", "*.py",
             *rg_skip,
             fingerprint, root],
            capture_output=True, text=True, timeout=2,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.strip().split("\n"):
                parts = line.split(":", 2)
                if len(parts) >= 2:
                    fp = os.path.abspath(parts[0])
                    ln = int(parts[1])
                    try:
                        with open(fp) as f:
                            file_lines = f.readlines()
                    except OSError:
                        continue
                    if all(
                        file_lines[ln - 1 + i].rstrip() == fp_lines[i]
                        for i in range(min(len(fp_lines), len(file_lines) - ln + 1))
                    ):
                        return (fp, ln)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass
    return


def _search_fallback(fingerprint: str, root: str) -> tuple[str, int] | None:
    fp_lines = fingerprint.split('\n')
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in _SKIP_DIRS]
        for f in filenames:
            if not f.endswith(".py"):
                continue
            p = os.path.join(dirpath, f)
            try:
                with open(p, errors="ignore") as fp:
                    file_lines = fp.readlines()
            except OSError:
                continue
            for i in range(len(file_lines) - len(fp_lines) + 1):
                if all(
                    file_lines[i + j].rstrip() == fp_lines[j]
                    for j in range(len(fp_lines))
                ):
                    return (os.path.abspath(p), i + 1)
    return