# Flask + Tkinter folder picker — subprocess workaround

**Project:** KP-Homepage (YouTube-to-MP3 feature)  
**Date written:** June 2026  
**Topic:** Why and how a Flask route opens a GUI dialog using a subprocess

---

## The problem

Flask runs your Python code inside a server thread. Tkinter — Python's built-in GUI toolkit — cannot open windows from a background thread. If you call `tkinter.filedialog.askdirectory()` directly inside a Flask route, it either crashes, freezes, or silently does nothing.

This is not a bug you can fix. It is a fundamental constraint of how tkinter works: it must run on the main thread of a process, and Flask's request handler is not that thread.

---

## The solution

Launch a brand new Python process whose *only job* is to open the folder picker dialog. That new process has its own main thread, so tkinter works fine. Flask then reads the result back via standard output (stdout).

The flow looks like this:

```
Browser clicks "Pick Folder"
  → Flask route /pick-folder is called
    → subprocess.run() spawns a new Python process
      → that process opens the tkinter dialog
        → user picks a folder (or cancels)
          → chosen path is printed to stdout
            → Flask reads stdout
              → path is stored in download_folder dict
                → JSON response returned to browser
```


## The code

```python
@app.route("/pick-folder")
@login_required
def pick_folder():
    import subprocess, sys

    script = (
        "import tkinter as tk; from tkinter import filedialog; "
        "root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1); "
        "path = filedialog.askdirectory(); print(path, end='')"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    selected = result.stdout.strip()

    if selected:
        download_folder["path"] = selected

    return jsonify({"folder": download_folder["path"]})
```

---

## Line by line

### The route and login guard

```python
@app.route("/pick-folder")
@login_required
def pick_folder():
```

A protected Flask route. Only authenticated users can trigger it. The browser hits this URL when the user clicks the folder picker button.

---

### The script string

```python
script = (
    "import tkinter as tk; from tkinter import filedialog; "
    "root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1); "
    "path = filedialog.askdirectory(); print(path, end='')"
)
```

This is a complete Python program written as a single string. It will be passed to a new Python process via the `-c` flag (same as running `python -c "..."`).

What each line does inside the subprocess:

| Line | Purpose |
|---|---|
| `import tkinter as tk` | Load the GUI toolkit |
| `from tkinter import filedialog` | Load the dialog module |
| `root = tk.Tk()` | Create a hidden root window (required by tkinter) |
| `root.withdraw()` | Hide the root window — only the dialog should appear |
| `root.wm_attributes('-topmost', 1)` | Force the dialog on top of other windows |
| `path = filedialog.askdirectory()` | Open the "choose a folder" dialog, wait for user |
| `print(path, end='')` | Print the result with no trailing newline (clean output) |

If the user cancels the dialog, `path` is an empty string and nothing is printed.

---

### Running the subprocess

```python
result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
```

| Argument | Meaning |
|---|---|
| `sys.executable` | The same Python interpreter currently running Flask — ensures version consistency |
| `"-c", script` | Tells Python to run the string as a program |
| `capture_output=True` | Captures stdout and stderr instead of printing to terminal |
| `text=True` | Returns output as a string instead of raw bytes |

`subprocess.run()` **blocks** — Flask waits here until the user closes the dialog before continuing.

---

### Reading the result

```python
selected = result.stdout.strip()

if selected:
    download_folder["path"] = selected
```

`result.stdout` contains whatever the subprocess printed. `.strip()` removes any accidental whitespace.

`download_folder` is a plain dictionary defined elsewhere in `app.py`, used as simple in-memory storage:

```python
download_folder = {"path": str(Path.home() / "Downloads")}
```

It defaults to the user's Downloads folder. Only updates if the user actually chose a folder — cancelling the dialog leaves the previous value intact.

---

### Returning the result

```python
return jsonify({"folder": download_folder["path"]})
```

Returns the current folder path as JSON. The frontend JavaScript reads this and updates the displayed path on the page.

---

## Why not use a global variable instead of a dict?

A plain variable like `selected_folder = ""` can be reassigned inside a function with the `global` keyword, but using a dict avoids needing `global`. Mutating a dict value (`download_folder["path"] = ...`) works without declaring anything — Python finds the dict in the outer scope and modifies it in place.

---

## Key concepts used

- **`subprocess.run()`** — runs an external process and waits for it to finish
- **`sys.executable`** — the path to the current Python interpreter
- **`-c` flag** — lets Python run a string as a script
- **`capture_output=True`** — redirects stdout/stderr into the result object
- **tkinter threading constraint** — tkinter must run on a process main thread
- **`root.withdraw()`** — hides the blank root window tkinter always creates

---

## Where this pattern applies more broadly

Any time you need a GUI dialog (file picker, colour picker, message box) from inside a Flask route or any threaded context, this same subprocess pattern works. You write the tkinter logic as a string, run it in a subprocess, and read back the result via stdout.

It is also useful for running any short Python snippet that must execute in isolation — for example, code that modifies global interpreter state or imports modules with thread-safety issues.
