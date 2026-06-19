## XML
XML stands for **eXtensible Markup Language**. It's a way of structuring text data using nested tags, similar in spirit to HTML but designed for data rather than display. The "extensible" part means there's no fixed set of tags like HTML's `<div>` or `<p>` — you invent whatever tags make sense for your data.
## OPML
OPML stands for **Outline Processor Markup Language**. It's just XML, but with a specific agreed-upon tag vocabulary designed for one purpose: representing a list (an "outline") of things, most commonly a list of RSS/Atom feeds.
Looking at your file again with this lens:
```xml
<opml version="1.0">
  <head>
    <title>Export from Plenary</title>
  </head>
  <body>
    <outline text="CBC | Top Stories News" 
        xmlUrl="https://www.cbc.ca/cmlink/rss-topstories" type="rss" />
    ...
  </body>
</opml>
```
`<opml>` is the root tag, signaling "this XML document follows the OPML convention." `<head>` holds metadata about the file itself (in this case, which app exported it — Plenary, an RSS reader app). `<body>` holds the actual content. Each `<outline>` tag represents one item in the list — here, one feed — with xmlUrl being the actual feed URL, `text`/`title` being the human-readable name, and `type="rss"` telling readers what kind of outline this is.

So **OPML** is really just "XML with a standardized schema for representing lists of feeds." That standardization is exactly why your script and any RSS reader app can both understand the same file.
## ElementTree (etree)
Now the Python side. Python doesn't understand XML natively — it just sees a big string of text. `ElementTree` is a module built into Python's standard library (no installation needed) that parses that string into a navigable tree structure your code can walk through.
The name "ElementTree" describes exactly what it produces: a tree made of Element objects, where each XML tag becomes a node you can inspect.
```python
from xml.etree import ElementTree as ET

tree = ET.parse("canada_feeds.opml")   # reads the file, builds the tree
root = tree.getroot()                   # the top node — here, the <opml> tag
```
From there, `root.iter("outline")` walks through the entire tree and yields every <outline> element found anywhere inside it, regardless of how deeply nested. Each one of those `outline` objects lets you pull attributes off it with `.get()`:
```python
for outline in root.iter("outline"):
    url = outline.get("xmlUrl")    # reads the xmlUrl="..." attribute
    title = outline.get("title")   # reads the title="..." attribute
```
This mirrors what `BeautifulSoup` does for HTML in your fetch_metadata route — same underlying idea (parse markup into a tree, then query it), just XML instead of HTML, and a different library since BeautifulSoup is built for HTML's looser, often broken structure while ElementTree expects well-formed XML.

### The chain, end to end
A feed reader app like Plenary exports your subscriptions as one OPML file (which is just XML following a feed-list schema) → you read that file as raw text from disk → ElementTree parses that text into a tree of Python objects → you loop through the tree pulling out the `xmlUrl` attribute from each `outline` node → you now have a clean Python list of feed URLs ready to hand to `feedparser`.