# Git Push Commands

## The Basic Sequence

Run these every time you want to save and push changes:

```bash
git add .
git commit -m "your message here"
git push
```

---

## What Each Does

```bash
git add .                        # stage all changed files
git add specific_file.py         # stage one specific file

git commit -m "your message"     # save staged changes with a message

git push                         # push to remote (GitHub)
git push origin main             # explicit version - push main branch to origin
```

---

## First Time Pushing a New Repo

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

The `-u` sets the upstream so future pushes just need `git push`.

---

## Other Useful Commands

```bash
git status                       # see what's changed / staged
git log --oneline                # see recent commits
git diff                         # see unstaged changes
git pull                         # pull latest from remote before pushing
```

---

## The Safe Habit

```bash
git pull          # get any remote changes first
git add .
git commit -m "description of what you changed"
git push
```

Pulling before pushing avoids conflicts, especially if you work across multiple machines or Render makes any automatic commits.