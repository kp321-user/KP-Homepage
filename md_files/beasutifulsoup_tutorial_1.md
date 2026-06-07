# Combining Two HTML Files with Python

There are two main approaches depending on what you're trying to do.

---

## Approach 1: Simple String Concatenation

Best when you just want to paste one file's content into another at a specific spot.

### The files

**header.html**
```html
<header>
  <h1>My Site</h1>
  <nav><a href="/">Home</a></nav>
</header>
```

**body.html**
```html
<main>
  <p>Welcome to my site.</p>
</main>
```

### The program

```python
# read both files
with open("header.html", "r", encoding="utf-8") as f:
    header = f.read()

with open("body.html", "r", encoding="utf-8") as f:
    body = f.read()

# combine them into a full page
combined = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Page</title>
</head>
{header}
{body}
</html>"""

# write the result
with open("output.html", "w", encoding="utf-8") as f:
    f.write(combined)

print("Done — output.html created")
```

### Output

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Page</title>
</head>
<header>
  <h1>My Site</h1>
  <nav><a href="/">Home</a></nav>
</header>
<main>
  <p>Welcome to my site.</p>
</main>
</html>
```

---

## Approach 2: BeautifulSoup (structural merging)

Best when you want to insert specific elements from one file into a specific location in another.

### The files

**base.html**
```html
<!DOCTYPE html>
<html>
<head><title>My Page</title></head>
<body>
  <div id="sidebar">
    <p>Sidebar content</p>
  </div>
  <div id="main-content">
    <!-- insert content here -->
  </div>
</body>
</html>
```

**content.html**
```html
<article>
  <h2>My Article</h2>
  <p>Article content here.</p>
</article>
```

### The program

```python
from bs4 import BeautifulSoup

# read both files
with open("base.html", "r", encoding="utf-8") as f:
    base_soup = BeautifulSoup(f, "html.parser")

with open("content.html", "r", encoding="utf-8") as f:
    content_soup = BeautifulSoup(f, "html.parser")

# find the target location in base
target_div = base_soup.find("div", id="main-content")

# grab the elements you want from content
article = content_soup.find("article")

# insert into base
target_div.append(article)

# write the result
with open("output.html", "w", encoding="utf-8") as f:
    f.write(str(base_soup))

print("Done — output.html created")
```

### Output

```html
<!DOCTYPE html>
<html>
<head><title>My Page</title></head>
<body>
  <div id="sidebar">
    <p>Sidebar content</p>
  </div>
  <div id="main-content">
    <article>
      <h2>My Article</h2>
      <p>Article content here.</p>
    </article>
  </div>
</body>
</html>
```

---

## Choosing Between the Two

| Situation | Use |
|---|---|
| Simple top-to-bottom joining | String concatenation |
| Inserting into a specific location | BeautifulSoup |
| Files contain Jinja2 / template tags | String concatenation (BS4 breaks Jinja) |
| Plain HTML only | Either |
| Need to grab specific elements | BeautifulSoup |

---

## Common Gotchas

**Always specify encoding** — without `encoding="utf-8"` you may get errors on
Windows when files contain accented characters or special symbols.

```python
# always do this
with open("file.html", "r", encoding="utf-8") as f:
```

**BeautifulSoup adds extra tags** — BS4 sometimes adds `<html>`, `<head>`, and
`<body>` tags if it thinks they're missing. If your input files are fragments
rather than full pages, use string concatenation instead.

**Check your paths** — if the files aren't in the same folder as your script,
use the full path:

```python
with open(r"C:\Users\Ken\Python files\link-db\templates\home.html", "r", encoding="utf-8") as f:
```