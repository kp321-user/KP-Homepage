<a href="index.html">&larr; Back Home</a><br>
<nav>
    <a href="#section-1-opening-closing-files">Section 1 — Opening & Closing Files</a>
    <a href="#section-2-file-modes">Section 2 — File Modes</a>
    <a href="#section-3-reading-files">Section 3 — Reading Files</a>
    <a href="#section-4-writing-files">Section 4 — Writing Files</a>
    <a href="#section-5-working-with-paths-os-pathlib">Section 5 — Paths</a>
    <a href="#section-6-exception-handling">Section 6 — Exception Handling</a>
    <a href="#section-7-csv-files">Section 7 — CSV Files</a>
    <a href="#section-8-json">Section 8 — JSON</a>
    <a href="#section-9-apis-with-requests">Section 9 — APIs</a>
    <a href="#section-10-sample-programs">Section 10 — Sample Programs</a>
    <a href="#section-11-list-comprehension">Section 11 — List Comprehension</a>
    <a href="#section-12-dicts-and-dict-comprehension">Section 12 — Dicts</a>
    <a href="#section-13-virtual-environments">Section 13 — Virtual Environments</a>
    <a href="#section-14-modules">Section 14 — Modules</a>
    <a href="#section-15-packages">Section 15 — Packages</a>
    <a href="#section-16-error-handling">Section 16 — Error Handling</a>
    <a href="#section-17-object-oriented-programming-oop">Section 17 — OOP</a>
    <a href="#section-18-generators">Section 18 — Generators</a>
    <a href="#section-19-decorators">Section 19 — Decorators</a>
    <a href="#section-20-testing-with-pytest">Section 20 — Testing</a>
    <a href="#section-21-structured-query-language-sql">Section 21 — SQL</a>
    <a href="#section-22-flask-html-render-website">Section 22 — Flask</a>
    <span class="site-title">Python Notes 2026</span>
</nav>

# Python Tutorial Notes 2026

## Section 1 — Opening & Closing Files

```python
# Always use 'with' — it auto-closes the file
with open("file.txt", "r") as f:
    content = f.read()

# Without 'with' (not recommended)
f = open("file.txt", "r")
content = f.read()
f.close()  # easy to forget!
```

## Section 2 — File Modes

| Mode          | Description                        |
|---------------|------------------------------------|
| `"r"`         | Read only. Error if missing.       |
| `"w"`         | Write. Overwrites existing!        |
| `"a"`         | Append to end.                     |
| `"x"`         | Create new. Error if exists.       |
| `"rb"`/`"wb"` | Binary read/write.                 |

## Section 3 — Reading Files

```python
with open("file.txt", "r") as f:
    content = f.read()       # entire file as string
    lines = f.readlines()    # list of lines
    line = f.readline()      # one line at a time

# Best for large files — memory efficient
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())  # strip() removes \n
```

## Section 4 — Writing Files

```python
# write() — single string
with open("file.txt", "w") as f:
    f.write("Hello, world!\n")

# writelines() — list of strings (no auto \n)
lines = ["line 1\n", "line 2\n", "line 3\n"]
with open("file.txt", "w") as f:
    f.writelines(lines)

# join() approach
with open("file.txt", "w") as f:
    f.write("\n".join(lines))

# append mode
with open("file.txt", "a") as f:
    f.write("This will be added to the end.\n")
```

## Section 5 — Working with Paths: `os` & `pathlib`

```python
import os
from pathlib import Path
```

### Path Operations

```python
os.path.exists("file.txt")           # True or False
os.path.join("folder", "file.txt")   # safe path joining
os.path.basename("/a/b/file.txt")    # "file.txt"
os.path.dirname("/a/b/file.txt")     # "/a/b"
os.path.isfile("file.txt")           # is it a file?
os.path.isdir("folder")              # is it a directory?
os.path.getsize("file.txt")          # size in bytes
```

### Directory Operations

```python
os.getcwd()                          # current working directory
os.chdir("/new/path")                # change directory
os.listdir(".")                      # list files & folders
os.mkdir("new_folder")               # create one folder
os.makedirs("a/b/c")                 # create nested folders
os.rmdir("empty_folder")             # remove empty folder
```

### File Operations

```python
os.remove("file.txt")                # delete a file
os.rename("old.txt", "new.txt")      # rename or move

# Walk entire directory tree
for root, dirs, files in os.walk("folder"):
    for file in files:
        print(os.path.join(root, file))
```

### Environment Variables

```python
os.environ["PATH"]                   # get a variable
os.environ.get("MY_KEY", "default")  # safe get
os.environ["MY_KEY"] = "value"       # set a variable
```

### `os` vs `pathlib` Quick Comparison

| `os` style                  | `pathlib` style                  |
|-----------------------------|----------------------------------|
| `os.path.exists(p)`         | `Path(p).exists()`               |
| `os.path.join(a, b)`        | `Path(a) / b`                    |
| `os.listdir(p)`             | `list(Path(p).iterdir())`        |
| `os.mkdir(p)`               | `Path(p).mkdir()`                |
| `os.path.isfile(p)`         | `Path(p).is_file()`              |

## Section 6 — Exception Handling

```python
try:
    # code that might fail
    with open("file.txt", "r") as f:
        content = f.read()

except FileNotFoundError:
    print("File not found!")        # runs if file doesn't exist

except PermissionError:
    print("Permission denied!")     # runs if no read access

except Exception as e:
    print(f"Unexpected error: {e}") # catches anything else

else:
    print("File read successfully!") # runs only if NO exception occurred

finally:
    print("Done.")                  # ALWAYS runs, error or not
```

### Common File Exceptions

| Exception             | Cause                                  |
|-----------------------|----------------------------------------|
| `FileNotFoundError`   | File or folder doesn't exist           |
| `PermissionError`     | No read/write access                   |
| `IsADirectoryError`   | Tried to open a folder as a file       |
| `FileExistsError`     | File already exists (mode `"x"`)       |
| `OSError`             | General OS-level file error            |
| `UnicodeDecodeError`  | Wrong encoding when reading            |

## Section 7 — CSV Files

```python
import csv
```

### Reading CSV Files

```python
# reader — rows as lists
with open("data.csv", "r", newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)  # ['Ken', '30', 'Montreal']

# DictReader — rows as dicts (uses header row as keys)
with open("data.csv", "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["city"])
```

### Writing CSV Files

```python
# writer — write rows as lists
with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age", "city"])       # header
    writer.writerow(["Ken", 30, "Montreal"])
    writer.writerows([                              # multiple rows
        ["Alice", 25, "Toronto"],
        ["Bob", 35, "Vancouver"]
    ])

# DictWriter — write rows as dicts
with open("data.csv", "w", newline="") as f:
    fields = ["name", "age", "city"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerow({"name": "Ken", "age": 30, "city": "Montreal"})
```

### `reader` vs `DictReader`

| `reader` (list)       | `DictReader` (dict)        |
|-----------------------|----------------------------|
| `row[0]  # "Ken"`     | `row["name"]  # "Ken"`     |
| `row[1]  # "30"`      | `row["age"]   # "30"`      |
| `row[2]  # "Montreal"`| `row["city"]  # "Montreal"`|
| Good for simple files | More readable, preferred   |

### Key Gotchas

> **Always use `newline=""`** — without it you get blank lines between rows on Windows.  
> **Everything is a string** — convert with `int(row[1])` or `float(row[1])` as needed.  
> **`DictReader` skips the header** — it uses the first row as keys automatically.  
> **Use `encoding="utf-8"`** — for files with accents or special characters.

## Section 8 — JSON

### What is JSON?

JSON (JavaScript Object Notation) is a human-readable data format used everywhere in APIs. It looks like Python dicts and lists:

```json
{
    "name": "Ken",
    "age": 30,
    "city": "Montreal",
    "hobbies": ["Python", "coding"],
    "active": true
}
```

### The 4 Key Functions

| Function           | Description                        |
|--------------------|------------------------------------|
| `json.load(f)`     | Read JSON from a file              |
| `json.dump(data, f)` | Write JSON to a file             |
| `json.loads(string)` | Parse JSON from a string         |
| `json.dumps(data)` | Convert data to a JSON string      |

> **Memory trick:** `load`/`dump` = files. `loads`/`dumps` = strings (the `s` = string).

### Reading & Writing JSON Files

```python
import json

# Read from file
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
print(data["name"])  # access like a dict

# Write to file
person = {"name": "Ken", "age": 30, "city": "Montreal"}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(person, f, indent=4)  # indent=4 makes it human-readable
```

### Working with JSON Strings

```python
# loads — parse a JSON string into Python
json_string = '{"name": "Ken", "age": 30}'
data = json.loads(json_string)
print(data["name"])  # "Ken"

# dumps — convert Python to JSON string
person = {"name": "Ken", "age": 30}
json_string = json.dumps(person, indent=4)
print(json_string)
```

> You'll use `loads`/`dumps` a lot with APIs — responses come back as strings, not files.  
> `loads()` converts a string → dict. `dumps()` converts a dict → string.

### Key Gotchas

> **JSON keys must be strings** — `{1: "a"}` will fail, use `{"1": "a"}`.  
> **`true`/`false` vs `True`/`False`** — JSON uses lowercase; `json.load()` converts automatically.  
> **Always use `encoding="utf-8"`** — especially important with French accented characters.  
> **Use `indent=`for readability** — `json.dump(data, f, indent=4)` writes pretty-printed JSON.

## Section 9 — APIs with `requests`

An API lets programs talk to each other. Web APIs use HTTP requests to exchange data, usually in JSON format.

### Making HTTP Requests

```python
import requests

# GET request — retrieve data
response = requests.get("https://api.example.com/data")
if response.status_code == 200:
    data = response.json()  # parse JSON response
    print(data)
else:
    print(f"Error: {response.status_code}")

# POST request — send data
payload = {"name": "Ken", "age": 30}
response = requests.post("https://api.example.com/users", json=payload)
if response.status_code == 201:
    print("User created successfully!")
else:
    print(f"Error: {response.status_code}")
```

### `requests` Exception Handling

```python
# Note: more specific exceptions must come before broader ones
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.ConnectionError:
    print("No internet connection.")
except requests.exceptions.Timeout:
    print("Request timed out.")
except requests.exceptions.HTTPError as e:    # before RequestException!
    print(f"HTTP error occurred: {e}")
except requests.exceptions.RequestException as e:
    print(f"Something went wrong: {e}")
```

### Key Gotchas

> **Always check status codes** — 200 = success (GET), 201 = created (POST).  
> **Use `.json()`** to parse JSON responses into a dict.  
> **`HTTPError` before `RequestException`** — `HTTPError` is a subclass, so it must come first.  
> **Use `timeout=`** — always set a timeout so your program doesn't hang forever.

### `fetchurl.py` — Reusable Fetch Function

```python
import requests

def fetch(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("No internet connection.")
    except requests.exceptions.Timeout:
        print("Request timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Something went wrong: {e}")
    return None
```

## Section 10 — Sample Programs

### GitHub Repo Search — Fetch & Save to CSV

```python
import requests
import csv

url = "https://api.github.com/search/repositories"
query = input("Enter search query: ")
params = {"q": query, "sort": "stars", "per_page": 5}

try:
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()
    with open("repositories.csv", "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Name", "Stargazers", "Description"])
        for repo in data["items"]:
            print(repo["name"])
            print(repo["stargazers_count"])
            description = repo["description"] or "No description provided."
            print(description[:100] + "..." if len(description) > 100 else description)
            print("---")
            csvwriter.writerow([repo["name"], repo["stargazers_count"], description])
except requests.exceptions.ConnectionError:
    print("No internet connection.")
except requests.exceptions.Timeout:
    print("Request timed out.")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error occurred: {e}")
except requests.exceptions.RequestException as e:
    print(f"Something went wrong: {e}")
```


## Section 11 — List Comprehension

### Basic Structure
```python
[expression for item in iterable]
```
### With Optional Filter
```python
[expression for item in iterable if condition]
```
### Example:
```python
word_list = ["python", "json", "csv", "requests"]
uppercase_list = [item.upper() for item in list if len(item) > 3]
print(uppercase_list)
```

## Section 12 — Dicts and Dict Comprehension

### Methods to know:
```python
person.keys()    # dict_keys(['name', 'age'])
person.values()  # dict_values(['Ken', 30])
person.items()   # dict_items([('name', 'Ken'), ('age', 30)])
```
`.items()` lets you loop over both **key** and **value** at once:
```python
for key, value in person.items():
    print(f"{key}: {value}")
```
And `.get()` for safe lookups:
```python
person["city"]                  # KeyError if missing!
person.get("city")              # None — no crash
person.get("city", "unknown")   # "unknown" — default value
```

### Example:
```python
def dict_summary(data):
    notes = data.get("notes", "No notes")
    print("Dictionary Summary:")
    for key, value in data.items():
        print(f"    {key}: {value}")
    if "notes" not in data:
        print(f"    notes: {notes}")

person = {"name": "Ken", "age": 30, "city": "Trois-Rivières"}
dict_summary(person)
```
### Dict comprehension:
```python
# list comprehension
[repo.name for repo in repos]

# dict comprehension
{repo.name: repo.stars for repo in repos}
# result: {"redis": 74520, "redux": 61447, ...}
```
Pattern: `{key_expression: value_expression for item in iterable}`

## Section 13 — Virtual Environments

### To start any project:

1. Create the virtual environment
`python -m venv venv`

2. Activate it (Windows)
`venv\Scripts\activate`

3. Install requests
`pip install` whatever you need (e.g. requests)

4. Save dependencies
`pip freeze > requirements.txt`

5. Add `venv/` to `.gitignore` before pushing to GitHub

## Section 14 — Modules

The pattern: `module_name.thing_inside_it`. The dot is how you reach inside.
```python
# Style 1 — import the whole module
import math_helpers
math_helpers.add(3, 5)      # must use the module name as prefix

# Style 2 — grab specific names from it
from math_helpers import add, PI
add(3, 5)                   # no prefix needed
print(PI)

# Style 3 — give it a nickname (alias)
import math_helpers as mh
mh.add(3, 5)                # shorter prefix
```
## Section 15 — Packages

A package is just a folder with an `__init__.py` file inside it. 
Here's the structure:
```
my_project/
    main.py
    helpers/              ← this is the package
        __init__.py       ← this makes it a package
        math_helpers.py
        file_helpers.py
```
And how you import from it:
```python
# main.py

from helpers import math_helpers
math_helpers.add(3, 5)

# or go straight to the function
from helpers.math_helpers import add
add(3, 5)
```
The dot in `helpers.math_helpers` means "inside the `helpers` package, find `math_helpers`." You can read it like a file path — `helpers/math_helpers.py`. The `__init__.py` file can be completely empty — and often is. Its job is just to mark the folder as a package.
But it can also do something useful: pre-load the things you want exposed at the package level:
```python
# helpers/__init__.py

from .math_helpers import add, multiply
from .file_helpers import read_lines
```
The dot before the module name (`.math_helpers`) means "look inside this same package." It's called a relative import.

### A well-structured version:
```python
my_project/
    main.py              ← only the entry point, ties everything together
    io/
        __init__.py
        reader.py        ← reads files, nothing else
        writer.py        ← writes files, nothing else
    processing/
        __init__.py
        cleaner.py       ← cleans/validates data
        calculator.py    ← does the math
```
Each file has one job. `reader.py` doesn't know anything about math. `calculator.py` doesn't know anything about files.

### How the files talk to each other:
```python
# main.py

from io.reader import load_csv
from processing.cleaner import clean_data
from processing.calculator import summarize
from io.writer import write_report

data = load_csv("sales.csv")
data = clean_data(data)
summary = summarize(data)
write_report(summary, "report.txt")
```
`main.py` reads like a table of contents for your whole program. That's the goal.

## Section 16 — Error Handling

`try` — run this code. 
`except` — if this specific error happens, do this instead

### Exceptions are just classes
This is the key insight. Every exception in Python is a class, and they form an inheritance hierarchy. That's why this works:
```python
except Exception as e:
    print(e)
```
`Exception` is the base class for almost every error — catching it catches nearly anything. But that's usually too broad. You want to catch specific exceptions so you handle each case appropriately.
Here's a slice of the hierarchy relevant to your project:
```python
BaseException
└── Exception
    ├── ValueError
    ├── TypeError
    ├── OSError
    │   └── FileNotFoundError
    └── requests.exceptions.RequestException
        ├── ConnectionError
        ├── Timeout
        └── HTTPError
```

### `else` and `finally`:
```python
try:
    response = requests.get(url, timeout=5)
except requests.exceptions.ConnectionError:
    print("No internet connection.")
else:
    # runs only if NO exception was raised
    print("Request succeeded!")
finally:
    # runs ALWAYS — exception or not
    print("Done attempting request.")
```
`else` is useful for code that should only run on success — keeps it visually separate from the try block. `finally` is useful for cleanup — closing files, closing connections — things that must happen regardless.

### Raising your own exceptions:
```python
def get_query():
    query = input("Enter search query: ")
    if not query.strip():
        raise ValueError("Search query cannot be empty.")
    return query
```
And catch them wherever you call it:
```python
try:
    query = get_query()
except ValueError as e:
    print(e)
```
This is cleaner than printing inside the function and returning None — the function signals that something went wrong, and the caller decides what to do about it.

### Custom exception classes:
For bigger projects you can define your own:
```python
class APIError(Exception):
    pass

class NoResultsError(Exception):
    pass
```
Then raise and catch them by name:
```python
raise APIError("GitHub returned a 403.")
```
```python
except APIError as e:
    print(f"API problem: {e}")
```
This makes error handling much more readable — you can tell at a glance what kind of thing went wrong.

`raise` manually creates an error that can be used to validate data that does not violate Python's rules. Execution stops at the raise line and Python unwinds up the call stack looking for an except block that matches. If it finds one, that code runs. If it never finds one, the program crashes with a traceback.

### Note "CALL STACK":
A call stack is the chain of functions that got you to where you are. When your program runs, Python keeps track of every function that's currently "in progress." That list is the call stack.
A simple example:
```python
def c():
    raise ValueError("oops")

def b():
    c()

def a():
    b()

a()
```
When c() raises the error, the call stack looks like this:
```python
a()  ← called first
  b()  ← called by a
    c()  ← called by b, error happens here
```
Python prints this when your program crashes — you've seen it before, it's the traceback:
```python
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    a()
  File "main.py", line 7, in a
    b()
  File "main.py", line 4, in b
    c()
  File "main.py", line 2, in c
    raise ValueError("oops")
ValueError: oops
```
Read it bottom to top — the bottom is where the error actually happened, the top is where your program started.

### What "unwinds up the call stack" means:
When an exception is raised, Python backs out of each function one by one looking for a try/except block. If c() doesn't catch it, it backs out to b(). If b() doesn't catch it, it backs out to a(). If nothing catches it, the program crashes.
```python
def c():
    raise ValueError("oops")  # raised here

def b():
    c()                        # no try/except, backs out to a()

def a():
    try:
        b()
    except ValueError as e:
        print(f"Caught it: {e}")  # caught here
```
The exception "bubbles up" until something handles it.

### Python built-in exceptions

| Function           | Description                        |
|--------------------|------------------------------------|
| `ValueError`     | The value is the wrong type or out of range              |
| `TypeError` | The wrong type was passed entirely            |
| `ConnectionError` | Network/connection problemTimeoutErrorSomething took too long         |
| `FileNotFoundError` | File doesn't exist      |
| `KeyError` | Dictionary key doesn't exist      |
| `IndexError` | List index out of range      |
| `RuntimeErrorGeneral` | General "something went wrong" catch-all      |

### The full structure together:
```python
try:
    # attempt this
except SomeError:
    # if this specific error occurs
else:
    # if NO error occurred
finally:
    # always, no matter what
```
You'll rarely use all four together — most real code uses just try/except, or try/except/finally. else is the least common of the four.

## Section 17 — Object Oriented Programming (OOP)

Everything in Python is already an object — strings, lists, dictionaries, your exceptions. OOP is just the practice of creating your own object types to model your problem.
You do that with a class.

### The four concepts:

1. Encapsulation — bundling data and behaviour together in one class
2. Inheritance — one class building on another
3. Polymorphism — different classes sharing the same interface
4. Abstraction — hiding complexity behind a simple interface


The four pillars of Object Oriented Programming, in the order to study them:

1. ENCAPSULATION
   - What a class is and how to define one
   - The __init__ method (constructor)
   - Instance variables and methods
   - The `self` keyword
   - Bundling data and behaviour together

2. INHERITANCE
   - How one class can build on another
   - The `super()` function
   - Overriding methods
   - Parent and child classes

3. POLYMORPHISM
   - Different classes sharing the same interface
   - Method overriding in practice
   - Why this makes code more flexible

4. ABSTRACTION
   - Hiding complexity behind a simple interface
   - Abstract base classes (abc module)
    (a way to define a class that cannot be instantiated directly, but can be subclassed. It allows us to define methods that must be implemented by any subclass, ensuring a consistent interface.)
   - What the user of a class needs to know vs. what they don't

### In the GitHub Search Example:

- Encapsulation — `Repo` bundles data and behaviour
- Inheritance — `Repo` builds on `GitHubResult`
- Polymorphism — `display.py` and `to_csv_row` work across any subclass
- Abstraction — `GitHubResult` enforces the contract via ABC

## Section 18 — Generators

A generator is like a list comprehension, but instead of building the entire list in memory at once, it produces one item at a time as you need it.

### The difference:
```python
# list comprehension — builds everything in memory immediately
names = [repo.name for repo in repos]

# generator — produces one name at a time, on demand
names = (repo.name for repo in repos)
```
Only difference in syntax is [ ] vs ( ). But what happens under the hood is completely different.

### Generator functions:
You can also write a generator as a function using yield instead of return:
```python
def get_popular_repos(repos, min_stars):
    for repo in repos:
        if repo.stars > min_stars:
            yield repo   # pause here, hand back this value, resume next time
```
`yield` is the key word. Every time the generator is asked for the next value, the function resumes from where it left off at the last yield.
Compare to `return` — `return` exits the function completely. yield pauses it and resumes later.

The generator approach makes sense in two specific situations:
1. You only need one pass — if you were only displaying results and not saving to CSV, the generator would work perfectly and save memory.
2. Early stopping — if you were searching through thousands of results and wanted to stop as soon as you found a match, a generator lets you do that without fetching everything first:
```python
for repo in fetch_all_pages(query):
    if repo.name == "redis":
        print("Found it!")
        break   # stops fetching immediately — remaining pages never requested
```
With a list you'd fetch all pages first, then search. With a generator you stop the moment you find what you need.

## Section 19 — Decorators

Example:
```python
import time

def timer(func):              # 1. takes a function as argument
    def wrapper(*args, **kwargs):   # 2. defines a wrapper
        start = time.time()
        result = func(*args, **kwargs)  # 3. calls the original function
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result         # 4. returns the original result
    return wrapper            # 5. returns the wrapper

@timer
def fetch_repos(query):
    print("Fetching repos...")
    return []
```

You can also pass arguments to decorators:
```python
def retry(attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except APIError:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(1)
            raise APIError("All retry attempts failed.")
        return wrapper
    return decorator

@retry(attempts=5)   # ← now configurable
def fetch_all_pages(query, pages=5):
    ...
```
## Section 20 — Testing with pytest

What makes a good test:
Each test should check one specific behaviour. Not "does the whole program work" but "does this one function do this one thing correctly."

Three parts to every good test — sometimes called AAA:
```python
def test_repo_description_fallback():
    # Arrange — set up the data
    repo = Repo(name="redis", stars=74520, description=None, url="https://...")
    
    # Act — do the thing
    result = repo.description
    
    # Assert — check the result
    assert result == "No description provided."
```

## Section 21 — Structured Query Language (SQL)
SQL is the language used to talk to databases. A database stores data in tables — think of them like spreadsheets:

| id                | Query                 | timestamp                 |
|-------------------|-----------------------|---------------------------|
|1                  | redis                 | 2026-05-27 23:00 |
|2                  | flask                 | 2026-05-27 23:05 |

SQL lets you create tables, insert rows, and retrieve data:
```sql
-- save a search
INSERT INTO searches (query, timestamp) VALUES ("redis", "2026-05-27");

-- get all searches
SELECT * FROM searches;
```

### SQLite — the simplest database
SQLite is a database that lives in a single file on your computer — no setup, no server required. Perfect for learning and small projects. Python has it built in (no installation needed):
```python
import sqlite3
```

## Section 22 — Flask HTML & Render website

Flask 


### Pushing to Render
```python
git add .
git commit -m "Add search history with SQLite"
git push
```