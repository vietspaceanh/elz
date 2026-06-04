from __future__ import annotations

import functools
import inspect
import os
import re
import sys
import typing
from dataclasses import replace

from .element import Element
from .file_search import find_name_line, resolve_func_source, resolve_inline_source
from .runtime import composition_deps, runtime
from .specs import ElementSpec, sanitize_alias

P = typing.ParamSpec("P")
PREFIXES = ("md", "html")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
SLOT_RE = re.compile(r"__ELF_(\d+)__")


@typing.overload
def el(func: typing.Callable[[], str | Element]) -> Element: ...

@typing.overload
def el(func: typing.Callable[P, str]) -> typing.Callable[P, Element]: ...

@typing.overload
def el(func: str) -> Element: ...

@typing.overload
def el(func: typing.Any) -> Element: ...

def el(func: typing.Callable[P, str] | str) -> typing.Callable[P, Element] | Element:
    if isinstance(func, str):
        fmt, content = _parse(func)
        frame = inspect.currentframe().f_back
        name, source = resolve_inline_source(frame)
        deps = []
        if (stack := composition_deps.get()) and (parent := stack[-1]):
            content, deps = _reindex_slots(content, parent)
        spec = ElementSpec(
            func_name=name,
            name=name,
            format=fmt,
            content=content,
            deps=deps,
            adhoc_fn=lambda: content,
            source=source,
        )
        return Element(spec)

    if isinstance(func, Element):
        return func

    if hasattr(func, '_repr_html_'):
        label = getattr(func, 'name', None) or type(func).__name__
        source = None

        wrapped = getattr(func, '__wrapped__', None)
        if wrapped is not None:
            try:
                f = inspect.getsourcefile(wrapped)
                if f and os.path.isfile(f):
                    source = (os.path.abspath(f), inspect.getsourcelines(wrapped)[1])
            except (TypeError, OSError):
                pass

        if not source:
            mod_name = getattr(func, '__module__', None)
            if mod_name and mod_name in sys.modules:
                mod = sys.modules[mod_name]
                mod_file = getattr(mod, '__file__', None)
                if mod_file and os.path.isfile(mod_file):
                    var_name = getattr(func, '__name__', None)
                    if var_name and getattr(mod, var_name, None) is func:
                        source = (os.path.abspath(mod_file), find_name_line(mod_file).get(var_name, 1))

        if not source:
            frame = inspect.currentframe().f_back
            _, source = resolve_inline_source(frame)

        unique_name = f"{label}@{source[0]}:{source[1]}" if source else label
        spec = ElementSpec(
            func_name=label,
            name=unique_name,
            format="html",
            source=source,
            adhoc_fn=func._repr_html_,
        )
        return Element(spec)

    ef = ElementFunction(func)
    functools.update_wrapper(ef, func)
    return ef


class ElementFunction:
    def __init__(self, func=None):
        self.func = func
        if func is not None:
            self._init_from_func(func)

    def _init_from_func(self, func):
        self.func = func
        self.name = _qualified_name(func)
        self._cached_element: Element | None = None
        self._epoch_at_cache: int | None = None
        self._error: Exception | None = None
        self._css = ""
        self._css_variants: dict | None = None
        self.source_text = inspect.getsource(func)
        self.source = resolve_func_source(func, self.source_text, func.__globals__)

        stack = composition_deps.get()
        self.is_local = bool(stack)
        self._depth = len(stack)

        if not self.is_local:
            runtime.register(self.name, self)

    def css(self, text: str, /, variants: dict | None = None) -> ElementFunction:
        self._css = text
        if variants:
            self._css_variants = variants
        return self

    def __call__(self, *args, **kwargs) -> Element:
        if self.func is None:
            self._init_from_func(args[0])
            return self

        if (
            not args
            and not kwargs
            and self._cached_element is not None
            and self._epoch_at_cache == runtime.last_change_ns
        ):
            return self._cached_element

        sig = inspect.signature(self.func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        all_args = dict(bound.arguments)

        default_kwargs = self.args
        is_default_call = default_kwargs is not None and not args and all_args == default_kwargs

        local_deps: list[ElementSpec] = []
        token = composition_deps.set(composition_deps.get() + (local_deps,))
        try:
            result = self.func(*args, **kwargs)
        finally:
            composition_deps.reset(token)

        if isinstance(result, Element):
            fmt = result.format
            content = str(result)
            adhoc_fn = result.spec.adhoc_fn
        else:
            fmt, content = _parse(str(result))
            content, local_deps = _reindex_slots(content, local_deps)
            adhoc_fn = None

        name = sanitize_alias(self.name, all_args)

        spec = ElementSpec(
            func_name=self.name,
            name=name,
            args=all_args,
            deps=list(local_deps),
            format=fmt,
            content=content,
            source=self.source,
            css=self._css,
            css_variants=self._css_variants,
            adhoc_fn=adhoc_fn,
        )

        element = Element(spec)

        if is_default_call:
            self._cached_element = element
            self._epoch_at_cache = runtime.last_change_ns

        return element

    def _err_require_args_and_cannot(self, action: str) -> None:
        if self.args is None:
            raise ValueError(
                f"Element '{self.name}' requires explicit arguments "
                f"and cannot {action}."
            )

    @property
    def args(self) -> dict | None:
        sig = inspect.signature(self.func)
        try:
            bound = sig.bind()
            bound.apply_defaults()
            return dict(bound.arguments)
        except TypeError:
            return None

    def __format__(self, _):
        self._err_require_args_and_cannot("be used in f-strings")
        stack = composition_deps.get()
        if stack:
            deps = stack[-1]
            idx = len(deps)
            el = self()
            if idx == len(deps):
                # Use replace to drop adhoc_fn — parent should use content, not re-execute
                deps.append(replace(el.spec, adhoc_fn=None))
            return f"__ELF_{idx}__"
        return str(self())

    def __str__(self):
        if self.is_local:
            if self._cached_element is None:
                self._cached_element = self()
            stack = composition_deps.get()
            if stack:
                target = stack[self._depth - 1]
                if not any(d is self._cached_element for d in target):
                    target.append(self._cached_element.spec)
            return str(self._cached_element)

        if self.args is None:
            raise RuntimeError(
                f"'{self.__name__}' element requires parameters. "
                f"Call {self.__name__}(...) and/or assign the result to a variable to use."
            )

        return str(self())

    def __getattr__(self, name):
        if self.args is None:
            raise AttributeError(
                f"You seem to access an un-initialized element (on attribute '{name}').\n"
                f"This element requires explicit arguments and cannot be called implicitly."
            )
        return getattr(self(), name)

    def __repr__(self):
        if self.args is None:
            return f"<{self.name}: requires arguments>"

        try:
            element = self()
        except Exception as err:
            self._error = err
            raise

        if element and element.content:
            return f"Element({self.name}({self.args}))"
        return ""

    def _repr_html_(self):
        if self.args is None:
            return
        if self._error is not None:
            self._error = None
        return self()._repr_html_()

    def __rich_console__(self, console, options):
        if self.args is None:
            return
        if self._error is not None:
            self._error = None
        element = self()
        yield from element.__rich_console__(console, options)

    def __or__(self, other):
        self._err_require_args_and_cannot("be used with the pipe operator")
        return self() | other

    def __ror__(self, other):
        self._err_require_args_and_cannot("be used with the pipe operator")
        return other | self()

    def __truediv__(self, other):
        self._err_require_args_and_cannot("be used with the / operator")
        return self() / other

    def __rtruediv__(self, other):
        self._err_require_args_and_cannot("be used with the / operator")
        return other / self()

    def __matmul__(self, weight):
        self._err_require_args_and_cannot("be used with the @ operator")
        return self() @ weight

    def __rmatmul__(self, weight):
        self._err_require_args_and_cannot("be used with the @ operator")
        return weight @ self()

    def save(self, path: str, title: str | None = None):
        self._err_require_args_and_cannot("be saved")
        if self._error is not None:
            raise RuntimeError(f"Element '{self.name}' has errors, cannot save.")
        self().save(path, title)

    def refresh(self):
        self._cached_element = None
        self._epoch_at_cache = None
        self._error = None


def params(cls):
    base_setattr = cls.__setattr__ if "__setattr__" in cls.__dict__ else object.__setattr__

    def __setattr__(self, name, value):
        base_setattr(self, name, value)
        runtime.bump_epoch()

    cls.__setattr__ = __setattr__
    return cls


def _reindex_slots(content: str, deps: list) -> tuple[str, list]:
    slots = sorted({int(m) for m in SLOT_RE.findall(content)})
    if len(slots) >= len(deps):
        return content, list(deps)
    remap = {old: new for new, old in enumerate(slots)}
    content = SLOT_RE.sub(lambda m: f"__ELF_{remap[int(m.group(1))]}__", content)
    return content, [deps[i] for i in slots]


def _parse(raw: str) -> tuple[str, str]:
    def _dedent(text: str) -> str:
        lines = text.split("\n")
        base = 0
        for line in lines:
            stripped = line.lstrip()
            if stripped:
                base = len(line) - len(stripped)
                break
        if base:
            out = [line[base:] if line and (len(line) - len(line.lstrip())) >= base else line for line in lines]
            return "\n".join(out).strip()
        return text.strip()

    for p in PREFIXES:
        if raw.startswith(p):
            after = raw[len(p):]
            if after and after[0] in ('\n', ' '):
                return p, COMMENT_RE.sub("", _dedent(after[1:]))
    return "html", COMMENT_RE.sub("", _dedent(raw))


def _qualified_name(func) -> str:
    module = func.__module__.rsplit(".", 1)[-1]
    if module == "__main__" or module == "__mp_main__":
        return f"_main__{func.__name__}"
    return f"{module}__{func.__name__}"