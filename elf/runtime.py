from __future__ import annotations

import contextvars
import time
from dataclasses import replace

from .specs import ElementSpec
from .render import render_fragment

composition_deps: contextvars.ContextVar[tuple[list, ...]] = contextvars.ContextVar(
    "composition_deps", default=()
)


class Graph:
    def __init__(self, runtime: Runtime, spec: ElementSpec):
        self.nodes: dict[str, ElementSpec] = {}
        self.edges: dict[str, set[str]] = {}
        self._runtime = runtime
        self._aliases: dict[str, str] = {}
        self._build_graph(spec)

    def _resolve_ref(self, ref: str) -> ElementSpec | None:
        entry = self._runtime.resolve(ref)
        if entry is None or isinstance(entry, ElementSpec):
            return entry
        if entry.args is None:
            return None
        cached = getattr(entry, "_cached_element", None)
        epoch = getattr(entry, "_epoch_at_cache", None)
        if cached is not None and epoch == self._runtime.last_change_ns:
            return cached.spec
        return entry(**entry.args).spec

    def _build_graph(self, spec: ElementSpec) -> None:
        if spec.name in self.nodes:
            return
        self.nodes[spec.name] = spec
        if spec.func_name != spec.name:
            self._aliases[spec.func_name] = spec.name
        for dep in spec.deps:
            if dep.name not in self.nodes:
                resolved = self._resolve_ref(dep.func_name or dep.name)
                if resolved is not None:
                    self._build_graph(resolved)
                else:
                    self._build_graph(dep)
            if dep.name in self.nodes and dep.name != spec.name:
                self.edges.setdefault(spec.name, set()).add(dep.name)

    def topological_order(self, target: str) -> list[str]:
        order: list[str] = []
        visiting: set[str] = set()
        target = self._aliases.get(target, target)

        def visit(name: str):
            if name in order:
                return
            if name in visiting:
                raise ValueError(f"Circular dependency: {name}")
            visiting.add(name)
            for dep in self.edges.get(name, set()):
                visit(dep)
            visiting.discard(name)
            order.append(name)

        visit(target)
        return order


class Runtime:
    def __init__(self):
        self.elements: dict = {}
        self.swaps: dict = {}
        self.last_change_ns: int = 0
        self.dev_mode: bool = True
        self._graph_cache: dict[int, Graph] = {}
        self.html_cache: dict[str, str] = {}
        self._version: dict[str, int] = {}
        self._render_version: dict[str, int] = {}

    def bump_epoch(self):
        self.last_change_ns = max(time.monotonic_ns(), self.last_change_ns + 1)

    def register(self, name, entry):
        was_registered = name in self.elements
        self.elements[name] = entry
        if not isinstance(entry, ElementSpec):
            self._version[name] = max(self._version.values(), default=0) + 1

    def _clear_caches(self):
        for entry in self.elements.values():
            cached = getattr(entry, "_cached_element", None)
            if cached is not None:
                cached.content = None
        self.bump_epoch()

    def clear(self):
        self._graph_cache.clear()
        self.swaps.clear()
        self.html_cache.clear()
        self._version.clear()
        self._render_version.clear()
        self._clear_caches()

    def resolve(self, name):
        return self.swaps.get(name) or self.elements.get(name)

    def graph(self, spec: ElementSpec) -> Graph:
        key = id(spec)
        if key in self._graph_cache:
            return self._graph_cache[key]
        g = Graph(self, spec)
        self._graph_cache[key] = g
        return g

    def _fresh(self, name: str, g: Graph) -> bool:
        if name not in self.html_cache:
            return False
        my_ver = self._render_version.get(name, 0)
        return all(
            self._version.get(d.func_name, 0) <= my_ver
            for d in [g.nodes[name], *g.nodes[name].deps]
        )

    def render(self, spec: ElementSpec, dev_mode: bool | None = None) -> str:
        if dev_mode is None:
            dev_mode = self.dev_mode
        g = self.graph(spec)
        for name in g.topological_order(spec.name):
            if self._fresh(name, g):
                continue
            node = g.nodes[name]
            children = [self.html_cache.get(d.name, "") for d in node.deps]
            self.html_cache[name] = render_fragment(node, dev_mode, child_html=children)
            self._render_version[name] = max(
                self._version.get(node.func_name, 0),
                max((self._version.get(d.func_name, 0) for d in node.deps), default=0),
            )
        return self.html_cache[spec.name]

    def swap(self, mapping):
        self._graph_cache.clear()
        self.swaps.clear()
        self.html_cache.clear()
        self._version.clear()
        self._render_version.clear()
        for target, replacement in mapping.items():
            name = target.name if hasattr(target, "name") else str(target)
            if isinstance(replacement, ElementSpec):
                spec = replacement
            else:
                spec = replacement().spec
            self.swaps[name] = replace(spec, name=name, deps=list(spec.deps))
        self._clear_caches()

    def __repr__(self):
        entries = {
            name: entry for name, entry in self.elements.items()
        }
        if not entries:
            return "Runtime(\n  elements: (none)\n)"
        lines = ["  elements:"]
        for name in sorted(entries):
            lines.append(f"    {name}")
        swaps = f"  swaps: {len(self.swaps)} entries" if self.swaps else "  swaps: ()"
        lines.append(swaps)
        return "Runtime(\n" + "\n".join(lines) + "\n)"


runtime = Runtime()
