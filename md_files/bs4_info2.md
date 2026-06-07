# When to Use BeautifulSoup for Complex HTML Combination

String concatenation is dumb — it just pastes text. BeautifulSoup lets you
read, inspect, and conditionally act on what's actually in the files before
combining them. Use it when the combination requires **decisions based on
content** rather than just position.

---

## Useful Scenarios

### Deduplicating Elements Across Files

You have two HTML files that both contain navigation links and want to merge
them without duplicates:

```python
# collect all existing hrefs from file 1
existing_links = {a.get("href") for a in soup1.find_all("a")}

# only add links from file 2 that aren't already there
for a in soup2.find_all("a"):
    if a.get("href") not in existing_links:
        nav.append(a)
```

---

### Merging Two Tables Into One

You have two HTML files each with a `<table>` and want all the rows combined:

```python
table1 = soup1.find("table")
rows_from_file2 = soup2.find_all("tr")

for row in rows_from_file2:
    table1.append(row)
```

---

### Selectively Pulling Sections by Heading

You have several HTML files and want only the sections under a specific `<h2>`:

```python
for h2 in soup.find_all("h2"):
    if "Installation" in h2.text:
        # grab everything until the next h2
        section_content = []
        for sibling in h2.next_siblings:
            if sibling.name == "h2":
                break
            section_content.append(sibling)
```

---

### Building a Single-Page Reference From Multiple Files

You have 60 separate HTML files and want to combine them into one long page
with a generated table of contents:

```python
toc = soup_base.new_tag("ul")

for filepath in all_article_files:
    with open(filepath, "r", encoding="utf-8") as f:
        article_soup = BeautifulSoup(f, "html.parser")

    # grab the h1 for the table of contents
    h1 = article_soup.find("h1")
    article_id = filepath.stem        # e.g. "01_paleolithic"

    # add toc entry
    li = soup_base.new_tag("li")
    a = soup_base.new_tag("a", href=f"#{article_id}")
    a.string = h1.text
    li.append(a)
    toc.append(li)

    # add id anchor to the article heading
    h1["id"] = article_id

    # append article to main content
    main.append(article_soup)
```

This is impossible with string concatenation because you need to read the
`<h1>` of each file to build the TOC, and inject an `id` attribute into each
heading so the TOC links work.

---

## The General Rule

Use BeautifulSoup when combining requires any of:

| Need | Why BS4 |
|---|---|
| Reading content to make decisions | Can inspect tags and text |
| Avoiding duplicates | Can check what already exists |
| Injecting attributes | Can set `id`, `class`, `href` on existing tags |
| Targeting specific sections | Can navigate by tag, class, id, text |
| Merging lists or tables | Can append rows/items selectively |
