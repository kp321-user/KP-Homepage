# BeautifulSoup Methods

## Finding Elements

```python
soup.find("h1")                        # first matching tag
soup.find("a", href="/about")          # first <a> with specific attribute
soup.find("div", class_="container")  # first div with that class

soup.find_all("a")                     # all matching tags, returns list
soup.find_all("a", limit=5)            # first 5 only
soup.select("div.container a")        # CSS selector - often most readable
soup.select_one("div.container a")    # CSS selector, first match only
```

## Reading Content

```python
tag.text          # all text inside tag, including nested tags
tag.get_text()    # same but with options:
tag.get_text(strip=True)              # strips whitespace
tag.get_text(separator=" ")          # joins text nodes with separator

tag["href"]       # get attribute value - raises error if missing
tag.get("href")   # get attribute value - returns None if missing (safer)
tag.attrs         # dict of all attributes
```

## Navigating the Tree

```python
tag.parent        # one level up
tag.children      # direct children (generator)
tag.descendants   # all nested content
tag.next_sibling  # next element at same level
tag.previous_sibling
tag.find_parent("div")              # search upward
```

## Modifying

```python
tag.string = "new text"             # replace text content
tag["href"] = "/new-url"            # set attribute
tag.decompose()                     # remove tag from tree entirely
tag.extract()                       # remove and return it
parent.append(new_tag)              # add child at end
parent.insert(2, new_tag)          # add at specific position
```

## Link-DB Relevant Methods

```python
soup.find("meta", property="og:image")   # og:image thumbnail
soup.find("link", rel="icon")            # favicon
tag.get("content")                       # read meta tag content
tag.get("href")                          # read link href
```

`find()`, `get()`, and `select_one()` with a CSS selector cover about 80% of real scraping work.