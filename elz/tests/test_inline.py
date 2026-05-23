from elz import el, Element, runtime

# Inline element
intro = el("""md
    # Test intro
    ## Section 1
""")

assert "intro" in intro.name, f"expected 'intro' in name, got {intro.name}"
print(f"name: {intro.name}")
print(f"content: {repr(intro.content)}")

# Inline in @el f-string
@el
def page():
    return f"""md
    {intro}
    # Section 2
    """

p = page()
assert "# Section 2" in p.content
assert len(p.deps) == 1
assert "intro" in p.deps[0].name
print(f"\npage content: {repr(p.content)}")
print(f"page deps: {[d.name for d in p.deps]}")

# @el decorator still works
@el
def header():
    return """md
    ## Header
    """

h = header()
assert h.content == "## Header"
print(f"\nheader content: {repr(h.content)}")

# Multiple inlines
greeting = el("""md
    # Welcome
""")

@el
def full():
    return f"""md
    {greeting}
    {intro}
    ## Footer
    """

f = full()
assert len(f.deps) == 2
print(f"\nfull deps: {[d.name for d in f.deps]}")
print(full.graph)

# HTML inline
button = el("""html
    <button>Click</button>
""")
assert button.format == "html"
print(f"\nbutton: {repr(button.content)}")

# Dep graph works
print(f"\npage graph:\n{page.graph}")

print("\nAll tests passed!")
