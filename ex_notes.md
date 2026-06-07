<a href="index.html">&larr; Back Home</a><br>
<nav>
    <a href="#section-1-syntax-basics">Section 1 — Syntax Basics</a>
    <a href="#section-2-control-flow">Section 2 — Control Flow</a>
    <a href="#section-3-functions">Section 3 — Functions</a>
    <a href="#section-4-arrays-and-objects">Section 4 — Arrays and Objects</a>
    <a href="#section-5-the-dom">Section 5 — The DOM</a>
    <a href="#section-6-fetch-and-async">Section 6 — Fetch and Async</a>
    <a href="#section-7-practical-project">Section 7 — Practical Project</a>
    <span class="site-title">JavaScript Notes 2026</span>
</nav>

# JavaScript Tutorial Notes 2026

## Section 1 — Syntax Basics

JavaScript runs in the browser and controls what happens on a webpage. You already know Python — this section maps JavaScript syntax directly to what you already know.

### Variables

Python uses plain assignment. JavaScript has three keywords:

| JavaScript        | Python equivalent | Notes                              |
|-------------------|-------------------|------------------------------------|
| `const x = 5`     | `x = 5`           | Cannot be reassigned               |
| `let x = 5`       | `x = 5`           | Can be reassigned                  |
| `var x = 5`       | `x = 5`           | Old style — avoid it               |

```javascript
const name = "Ken";       // won't change — use const by default
let score = 0;            // will change — use let
score = 10;               // reassign is fine
```

> **Rule of thumb:** always use `const` unless you know the value will change, then use `let`. Never use `var`.

### Data Types

```javascript
const name = "Ken";           // string
const age = 30;               // number (no int/float distinction)
const active = true;          // boolean (lowercase, unlike Python's True)
const nothing = null;         // intentional empty value (like Python's None)
let notDefined;               // undefined — declared but no value assigned
```

### Template Literals

JavaScript's equivalent of Python's f-strings — use backticks instead of quotes:

```python
# Python
print(f"Hello, {name}! You are {age} years old.")
```

```javascript
// JavaScript
console.log(`Hello, ${name}! You are ${age} years old.`);
```

The pattern: backtick `` ` `` to open the string, `${}` to insert a variable.

### Comparisons

```javascript
// Always use === (strict equality) — checks value AND type
5 === 5       // true
5 === "5"     // false — different types

// == (loose equality) — avoid it, causes subtle bugs
5 == "5"      // true — JavaScript converts types silently
```

> **Rule of thumb:** always use `===` and `!==`. Never use `==` or `!=`.

### Comments

```javascript
// single line comment

/*
  multi-line
  comment
*/
```

### Printing to Console

```javascript
console.log("Hello");          // like Python's print()
console.log(name, age);        // can pass multiple values
```

---

## Section 2 — Control Flow

The logic is identical to Python — only the syntax differs.

### if / else if / else

```python
# Python
if score > 90:
    print("A")
elif score > 70:
    print("B")
else:
    print("C")
```

```javascript
// JavaScript
if (score > 90) {
    console.log("A");
} else if (score > 70) {
    console.log("B");
} else {
    console.log("C");
}
```

Key differences from Python:
- Condition goes inside `()` parentheses
- Body goes inside `{}` curly braces instead of indentation
- `elif` becomes `else if` (two words)

### for Loop

```python
# Python
for i in range(5):
    print(i)
```

```javascript
// JavaScript
for (let i = 0; i < 5; i++) {
    console.log(i);
}
```

The three parts inside `()`: start, condition, increment.

### for...of — Looping Over Arrays

```python
# Python
for item in my_list:
    print(item)
```

```javascript
// JavaScript
for (const item of myArray) {
    console.log(item);
}
```

`for...of` is the closest equivalent to Python's `for x in list`.

### while Loop

```python
# Python
while count < 5:
    count += 1
```

```javascript
// JavaScript
while (count < 5) {
    count++;    // count++ is shorthand for count += 1
}
```

---

## Section 3 — Functions

### Regular Functions

```python
# Python
def greet(name):
    return f"Hello, {name}!"
```

```javascript
// JavaScript
function greet(name) {
    return `Hello, ${name}!`;
}
```

### Arrow Functions

Arrow functions are a shorter syntax — used heavily in modern JavaScript:

```javascript
// regular function
function greet(name) {
    return `Hello, ${name}!`;
}

// arrow function — same thing, shorter syntax
const greet = (name) => {
    return `Hello, ${name}!`;
};

// even shorter — when the body is just one return statement
const greet = (name) => `Hello, ${name}!`;
```

You'll see arrow functions constantly in JavaScript. They behave like regular functions for most purposes.

### Default Parameters

```python
# Python
def greet(name="stranger"):
    return f"Hello, {name}!"
```

```javascript
// JavaScript
const greet = (name = "stranger") => `Hello, ${name}!`;
```

### Scope

`const` and `let` are **block-scoped** — they only exist inside the `{}` where they were defined:

```javascript
if (true) {
    const x = 5;    // only exists inside this if block
}
console.log(x);     // ReferenceError — x doesn't exist here
```

---

## Section 4 — Arrays and Objects

### Arrays

Arrays are like Python lists:

```javascript
const fruits = ["apple", "banana", "cherry"];

fruits[0]              // "apple" — indexing works the same
fruits.length          // 3 — like Python's len()
fruits.push("mango")   // add to end — like Python's .append()
fruits.pop()           // remove from end
```

### Useful Array Methods

```javascript
const numbers = [1, 2, 3, 4, 5];

// map — transform every item (like Python's list comprehension)
const doubled = numbers.map(n => n * 2);    // [2, 4, 6, 8, 10]

// filter — keep items that pass a test
const evens = numbers.filter(n => n % 2 === 0);   // [2, 4]

// find — return the first match
const found = numbers.find(n => n > 3);    // 4

// includes — check if value exists (like Python's `in`)
numbers.includes(3)    // true
```

### Objects

Objects are like Python dictionaries — key-value pairs:

```python
# Python
person = {"name": "Ken", "age": 30}
print(person["name"])
```

```javascript
// JavaScript
const person = { name: "Ken", age: 30 };
console.log(person.name);     // dot notation — most common
console.log(person["name"]);  // bracket notation — also works
```

> Note: JavaScript object keys don't need quotes (unless they contain spaces or special characters).

### Destructuring

A shortcut to pull values out of an object or array:

```javascript
const person = { name: "Ken", age: 30, city: "Trois-Rivières" };

// without destructuring
const name = person.name;
const age = person.age;

// with destructuring — same result, one line
const { name, age } = person;
```

---

## Section 5 — The DOM

The DOM (Document Object Model) is how JavaScript sees and controls your HTML page. Every element on the page is a node in a tree that JavaScript can read and modify.

### Selecting Elements

```javascript
// by id — returns one element
const btn = document.getElementById("my-button");

// by CSS selector — returns first match
const btn = document.querySelector("#my-button");
const input = document.querySelector("input");
const box = document.querySelector(".converter-box");

// by CSS selector — returns all matches
const links = document.querySelectorAll("a");
```

### Reading and Changing Content

```javascript
const status = document.getElementById("status");

status.textContent             // read the text
status.textContent = "Done!";  // change the text

status.innerHTML               // read raw HTML inside
status.innerHTML = "<b>Done!</b>";  // change with HTML
```

### Changing Styles

```javascript
const box = document.getElementById("box");
box.style.color = "red";
box.style.display = "none";    // hide an element
box.style.display = "block";   // show it again
```

### Handling Events

```javascript
const btn = document.getElementById("my-button");

// addEventListener — preferred approach
btn.addEventListener("click", function() {
    console.log("Button clicked!");
});

// arrow function version
btn.addEventListener("click", () => {
    console.log("Button clicked!");
});
```

You've already used the inline version in your converter page:
```html
<button onclick="convertVideo()">Download MP3</button>
```

Both approaches work — `addEventListener` keeps your JavaScript separate from your HTML.

### Built-in Event Names

`click` is not something you define — it's a word the browser already knows. There are many built-in event names:

| Event | Triggers when... |
|---|---|
| `click` | user clicks an element |
| `dblclick` | user double clicks |
| `mouseover` | mouse hovers over element |
| `mouseout` | mouse leaves element |
| `keydown` | user presses a key |
| `keyup` | user releases a key |
| `input` | value of an input changes |
| `change` | input loses focus after changing |
| `submit` | a form is submitted |
| `load` | page finishes loading |

```javascript
// run something when user types in an input
input.addEventListener("input", () => {
    console.log(input.value);
});

// run something when page finishes loading
window.addEventListener("load", () => {
    console.log("Page is ready!");
});
```

---

## Section 6 — Fetch and Async

This is where JavaScript connects to your Flask backend — exactly what you did in the converter page.

### What async/await means

Some operations take time — fetching data from a server, for example. JavaScript handles this with `async/await`:

```javascript
// without async/await — harder to read
fetch("/convert").then(response => response.json()).then(data => console.log(data));

// with async/await — reads like normal code
async function getData() {
    const response = await fetch("/convert");
    const data = await response.json();
    console.log(data);
}
```

`async` marks a function as asynchronous — it can use `await` inside it.
`await` pauses the function until the operation finishes, then continues.

### fetch() — Calling a Flask Route

```javascript
// GET request
async function loadData() {
    const response = await fetch("/some-route");
    const data = await response.json();
    console.log(data);
}

// POST request with form data
async function sendData() {
    const formData = new FormData();
    formData.append("url", "https://youtube.com/...");

    const response = await fetch("/convert", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        console.log("Success!");
    }
}
```

You wrote both of these patterns already in your converter page.

### Error Handling

```javascript
async function getData() {
    try {
        const response = await fetch("/some-route");
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.log("Something went wrong:", error);
    }
}
```

`try/catch` in JavaScript works exactly like Python's `try/except`.

### Checking the Response

```javascript
response.ok             // true if status is 200-299
response.status         // the status code (200, 404, 500, etc.)
response.json()         // parse JSON body — returns a promise, use await
response.text()         // get body as plain text
```

---

## Section 7 — Practical Project

Tie everything together by adding two features to your YouTube converter page.

### Feature 1 — Format Selector (mp3 / mp4)

Add a dropdown to let you choose between mp3 and mp4 before downloading.

**In `converter.html`:**
```html
<label>Format</label>
<select id="format">
    <option value="mp3">MP3 (audio only)</option>
    <option value="mp4">MP4 (video)</option>
</select>
```

**In the `convertVideo()` function:**
```javascript
const format = document.getElementById("format").value;
formData.append("format", format);
```

**In `app.py`:**
```python
format = request.form.get("format", "mp3")

if format == "mp4":
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
    }
else:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
```

### Feature 2 — Download History

Show a live list of recently downloaded files, updated without reloading the page.

**In `app.py`** — add a history list and update the `/convert` route:
```python
download_history = []

@app.route("/convert", methods=["POST"])
@login_required
def convert():
    url = request.form.get("url")
    folder = download_folder["path"]
    # ... ydl_opts as before ...

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Unknown")

    download_history.append(title)
    return jsonify({"status": "ok", "title": title})

@app.route("/history")
@login_required
def get_history():
    return jsonify({"history": download_history})
```

**In `converter.html`** — add a history section and load it on page start:
```html
<h3>Download History</h3>
<ul id="history-list"></ul>

<script>
async function loadHistory() {
    const res = await fetch("/history");
    const data = await res.json();
    const list = document.getElementById("history-list");
    list.innerHTML = "";
    for (const title of data.history) {
        const li = document.createElement("li");
        li.textContent = title;
        list.appendChild(li);
    }
}

// load history when page opens
loadHistory();
</script>
```

This project uses every concept from sections 1–6:
- Variables and template literals (Section 1)
- Loops to build the history list (Section 2)
- Arrow functions (Section 3)
- Working with arrays from the server response (Section 4)
- Selecting and updating DOM elements (Section 5)
- fetch() and async/await to talk to Flask (Section 6)

---

## Section 8 — CSS Basics

CSS (Cascading Style Sheets) controls how HTML elements look — colors, fonts, spacing, layout. You've already been writing CSS in `darkstyle.css` throughout your Flask project. This section formalizes what you've been doing.

### How CSS works

CSS rules have two parts — a selector and declarations:

```css
selector {
    property: value;
    property: value;
}
```

For example:
```css
h1 {
    color: #e6edf3;
    font-size: 32px;
}
```

This targets every `h1` on the page and sets its color and size.

---

### Selectors

#### Single element — targets every instance of that tag:
```css
h1 { }        /* every h1 */
p { }         /* every paragraph */
a { }         /* every link */
button { }    /* every button */
input { }     /* every input */
```

#### Class (dot) — targets elements with a specific class:
```css
.link-item { }        /* <div class="link-item"> */
.back-link { }        /* <a class="back-link"> */
```

#### ID (hash) — targets one specific element:
```css
#title { }            /* <h1 id="title"> */
#status { }           /* <div id="status"> */
```

#### Descendant (space) — targets elements inside other elements:
```css
nav a { }             /* links inside nav */
.link-item small { }  /* small tags inside .link-item */
form button { }       /* buttons inside a form */
```

Read right to left: "style `a` elements that are inside `nav` elements."

#### Multiple targets (comma) — style several things at once:
```css
h1, h2, h3 { }               /* all three headings */
input, select, textarea { }   /* all form inputs */
```

#### State (colon) — style elements in a specific state:
```css
a:hover { }           /* link when mouse hovers */
button:hover { }      /* button on hover */
input:focus { }       /* input when active/clicked */
```

#### Direct child (>) — only immediate children, not deeper nested elements:
```css
nav > a { }           /* links directly inside nav only */
```

### Selector summary

| Selector | Example | Targets |
|---|---|---|
| Element | `h1 { }` | Every h1 |
| Class | `.link-item { }` | Elements with that class |
| ID | `#title { }` | One specific element |
| Descendant | `nav a { }` | Links inside nav |
| Multiple | `h1, h2 { }` | Both h1 and h2 |
| Hover | `a:hover { }` | Link on hover |
| Child | `nav > a { }` | Direct children only |

---

### The Box Model

Every HTML element is a box. The box model describes the space around it:

```
┌─────────────────────────────┐
│           margin            │  ← space outside the element
│  ┌───────────────────────┐  │
│  │        border         │  │  ← visible border
│  │  ┌─────────────────┐  │  │
│  │  │     padding     │  │  │  ← space inside, between border and content
│  │  │  ┌───────────┐  │  │  │
│  │  │  │  content  │  │  │  │  ← the actual text/image
│  │  │  └───────────┘  │  │  │
│  │  └─────────────────┘  │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

```css
.box {
    margin: 20px;          /* space outside */
    border: 1px solid red; /* visible line */
    padding: 10px;         /* space inside */
}
```

Shorthand — top, right, bottom, left (clockwise):
```css
margin: 10px 20px 10px 20px;   /* top right bottom left */
margin: 10px 20px;              /* top/bottom  left/right */
margin: 10px;                   /* all four sides */
```

---

### Common Properties

#### Text and color:
```css
color: #c9d1d9;              /* text color */
background-color: #0d1117;   /* background */
font-size: 18px;             /* text size */
font-weight: bold;           /* bold text */
font-family: Calibri, sans-serif;
text-align: center;          /* left, center, right */
text-decoration: none;       /* remove underline from links */
line-height: 1.6;            /* space between lines */
```

#### Sizing:
```css
width: 200px;
height: 50px;
max-width: 1000px;           /* won't grow beyond this */
min-width: 100px;            /* won't shrink below this */
```

#### Border:
```css
border: 1px solid #30363d;   /* width style color */
border-radius: 4px;          /* rounded corners */
border-bottom: 1px solid #30363d;  /* one side only */
```

#### Spacing:
```css
padding: 10px 20px;
margin: 8px 0;
gap: 10px;                   /* space between flex/grid items */
```

---

### Flexbox

Flexbox arranges items in a row or column. You've used this throughout `darkstyle.css`.

```css
.container {
    display: flex;
    flex-direction: row;      /* row (default) or column */
    align-items: center;      /* cross axis — vertical in row */
    justify-content: space-between;  /* main axis — horizontal in row */
    gap: 10px;
}
```

| Property | Values | Effect |
|---|---|---|
| `flex-direction` | `row`, `column` | Direction items flow |
| `align-items` | `center`, `flex-start`, `flex-end` | Cross axis alignment |
| `justify-content` | `center`, `space-between`, `flex-start` | Main axis alignment |
| `flex-wrap` | `wrap`, `nowrap` | Whether items wrap to next line |
| `gap` | `10px` | Space between items |

`margin-left: auto` on an item pushes it to the far right — used in your nav for the site title.

---

### CSS Grid

Grid arranges items in rows and columns. You're using this in your nav.

```css
.container {
    display: grid;
    grid-template-columns: repeat(3, 200px);  /* 3 columns, 200px each */
    grid-auto-flow: column;                    /* fill column by column */
    grid-template-rows: repeat(8, auto);       /* 8 rows per column */
    gap: 4px 16px;                             /* row-gap column-gap */
}
```

Common column patterns:
```css
grid-template-columns: repeat(3, 200px);    /* 3 fixed columns */
grid-template-columns: repeat(3, 1fr);      /* 3 equal flexible columns */
grid-template-columns: repeat(auto-fill, 150px);  /* as many as fit */
grid-template-columns: 200px 1fr 150px;    /* mixed fixed and flexible */
```

`1fr` means "one fraction of available space" — similar to `flex: 1`.

---

### Flexbox vs Grid

| | Flexbox | Grid |
|---|---|---|
| Best for | One direction (row OR column) | Two dimensions (rows AND columns) |
| Use when | Aligning items in a line | Creating a structured layout |
| Example in your app | `.link-item`, `.filter-dropdowns` | `nav` |

---

### CSS Variables

You can define reusable values at the top of your CSS:

```css
:root {
    --bg-primary: #0d1117;
    --text-primary: #c9d1d9;
    --border-color: #30363d;
    --link-color: #58a6ff;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

a {
    color: var(--link-color);
}
```

You don't currently use CSS variables in `darkstyle.css` but they're useful when a color appears in many places — change it once in `:root` and it updates everywhere.

---

### How `darkstyle.css` maps to these concepts

| CSS in your file | Concept |
|---|---|
| `body { max-width: 1000px; margin: 40px auto; }` | Box model, centering |
| `h1 { color: #e6edf3; font-size: 32px; }` | Element selector, text properties |
| `a:hover { text-decoration: underline; }` | State selector |
| `.link-item { display: flex; justify-content: space-between; }` | Flexbox |
| `nav { display: grid; grid-template-columns: repeat(3, 200px); }` | CSS Grid |
| `input[type="text"] { background-color: #161b22; }` | Attribute selector |
| `nav a { color: #58a6ff; }` | Descendant selector |
| `.dropdown.open { display: block; }` | Combined class selector |
