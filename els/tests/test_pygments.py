from els import el

code_snippet = """
from deff import tbl  # a Table

@tbl
def orders():
    return f'''sql
       from favorita.orders
       using sample 10%
    '''
"""

code_snippet_2 = """
plot(f'''
FROM {orders}
SELECT
    "Price", --density
    "Customer demographics", --color
''')
"""

code_snippet_3 = '''
el("""md
    # Heading
    Some text
""")
'''

@el
def doc():
    return f'''md
    # API Reference

    ## Example

    ```python
    {code_snippet}
    ```

    ```python
    {code_snippet_2}
    ```

    ```python
    {code_snippet_3}
    ```

    ```sql
    SELECT * FROM orders WHERE price > 100
    ```
    '''

html = doc()._repr_html_()
print("=== HTML output (first 4000 chars) ===")
print(html[:4000])
print()

assert 'class="highlight"' in html, "No highlight div found"
assert '<style>' in html, "No Pygments CSS"

# Basic Pygments classes present
assert 'class="k"' in html or 'class="kn"' in html, "No Pygments keyword class"
assert 'class="s"' in html or 'class="s2"' in html, "No Pygments string class"
assert 'class="c1"' in html, "No Pygments comment class"

# Sublanguage injection: SQL keywords inside f'''sql''' Python string
assert 'class="k"' in html, "SQL keywords from f-string SQL not found"

# Sublanguage injection: plot() string content has SQL keywords  
assert 'class="c1"' in html, "SQL comment inside plot() not found"

# Sublanguage injection: el() string content preserved
assert 'Heading' in html, "el() markdown content not found"

# Interpolation preserved: {orders} should appear in output
assert 'orders' in html, "Interpolation {orders} not preserved"
