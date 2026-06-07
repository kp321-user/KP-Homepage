# Claude Secret Codes:
- `/ghost` before promt - human sounding
- `OODA` before promt - apply military style decision-making framwork
- `/artifacts` at end of prompt - turn into working app or game 
- `L99` at end - respond at advanced expert level like a world-class specialist
- `/god mode` before promt - unlocks Claude's most agressive and comprehensive response

----

## Shell commands
A "shell" is the program that accepts text commands and talks to your operating system. When you open a terminal and type something, you're talking to a shell. "Shell commands" just means commands you type there — ls, cd, mkdir, cp, etc. It's the general term, not tied to any specific shell program.

## Bash commands
Bash (Bourne Again Shell) is the most common specific shell on Linux and Mac. So "bash commands" are shell commands written for Bash specifically. On Windows, the default shells are CMD and PowerShell, which have different syntax — but you can also install Bash on Windows (Git Bash, WSL).
The distinction matters because shell syntax varies slightly between shells. A bash script won't necessarily run in PowerShell. Since you're on Windows, when I use bash_tool in our sessions I'm running commands inside a Linux container — which is why the commands are bash-flavored.

## `curl`
curl is a specific command-line tool for making HTTP requests — fetching URLs from the terminal. It's like a browser, but text-only and scriptable.
```bash
curl https://example.com          # fetch a webpage
curl -X POST https://api.com/data # send a POST request
curl -O https://example.com/file.zip  # download a file
```
It's extremely common for testing APIs, downloading files in scripts, and checking whether a server is responding. You've indirectly used its logic every time Flask's `requests` library fetches a URL — `requests` is essentially Python's version of curl.

The short version: shell is the environment, bash is a specific shell, curl is a tool you run inside that shell.

---------------

# Python Naming Conventions

Classes are capitalized (PascalCase). Everything else is lowercase.

## The Convention Table

| Thing | Convention | Example |
|---|---|---|
| Classes | CapitalizedWords (PascalCase) | `Tag`, `BeautifulSoup`, `FlaskForm` |
| Variables | lowercase_with_underscores | `my_tag`, `soup`, `new_link` |
| Functions | lowercase_with_underscores | `find()`, `get_text()`, `append()` |
| Constants | ALL_CAPS | `MAX_SIZE`, `DEBUG` |

## Classes vs Instances

When you see something capitalized in Python it's almost always a class. The lowercase versions are instances of those classes:

```python
soup = BeautifulSoup(...)   # soup is an instance of BeautifulSoup
tag = soup.find("a")        # tag is an instance of Tag
```

## Examples From Your Stack

| Capitalized (class) | Lowercase (instance) |
|---|---|
| `BeautifulSoup` | `soup` |
| `Tag` | `tag` |
| `NavigableString` | `tag.string` |
| `FlaskForm` | `form` |
| `SQLAlchemy` | `db` |

Capitalization is a signal — it tells you "this is a class, not a function or variable" before you even look it up.

----

# Python Dot Notation

The dot always means **"belonging to"** or **"coming from"**. Read it left to right.

```python
soup.find("a").get("href")
```

- `soup` — your BeautifulSoup object
- `soup.find("a")` — call the `find` method *on* soup, returns a `Tag` object
- `soup.find("a").get("href")` — call `get` *on that Tag*, returns the href value

Each dot is just asking the thing on the left to give you something.

---

## The Three Things That Appear After a Dot

### 1. A Method (function attached to an object)

```python
soup.find("a")        # find() is a method on soup
tag.get_text()        # get_text() is a method on tag
response.json()       # json() is a method on response
```

Recognizable because it has `()` at the end.

### 2. An Attribute (variable attached to an object)

```python
tag.text              # text is an attribute of Tag
tag.parent            # parent is an attribute of Tag
response.status_code  # status_code is an attribute of response
```

No `()` — just a value stored on the object.

### 3. Something From a Module (after an import)

```python
os.path.join()        # join is inside path which is inside os
flask.Flask           # Flask class inside the flask module
```

Looks identical to the others but the left side is a module name rather than an object instance.

---

## Breaking Down a Chain

When a chain confuses you, break it into separate steps — they are identical:

```python
# chained (one line):
result = soup.find("meta").get("content")

# broken into steps (identical, often clearer):
meta_tag = soup.find("meta")     # step 1
result = meta_tag.get("content") # step 2
```

Breaking a chain into separate variables is always valid and never changes the result.