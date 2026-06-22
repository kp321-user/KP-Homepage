import os
import sqlite3

MD_SOURCE = "md_files"
SQLITE_PATH = r"C:/Users/Ken/CODE/Link-DB/instance/kp_db_2026.db"


def filename_to_slug(filename):
    name = filename[3:]  # strip first 3 chars (e.g. "01_")
    name = name.replace(".md", "")  # strip extension
    name = name.replace("_", "-")  # underscores to hyphens
    name = name.lower()
    return name


def run():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, slug FROM history_page")
    pages = {row["slug"]: row for row in cursor.fetchall()}

    matched = []
    unmatched = []

    for root, dirs, files in os.walk(MD_SOURCE):
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue

            slug = filename_to_slug(fname)
            filepath = os.path.join(root, fname)

            if slug in pages:
                matched.append((filepath, slug, pages[slug]["id"]))
            elif slug + "-overview" in pages:
                full_slug = slug + "-overview"
                matched.append((filepath, full_slug, pages[full_slug]["id"]))
            else:
                unmatched.append((filepath, slug))

    print(f"\n{'='*60}")
    print(f"MATCHED ({len(matched)}):")
    for filepath, slug, page_id in matched:
        print(f"  {os.path.basename(filepath)} -> slug '{slug}' (ID {page_id})")

    if unmatched:
        print(f"\nUNMATCHED ({len(unmatched)}) — skipped:")
        for filepath, slug in unmatched:
            print(
                f"  {os.path.basename(filepath)} -> derived slug '{slug}' (no DB match)"
            )

    confirm = input(f"\nWrite content for {len(matched)} pages? (y/n): ")
    if confirm.lower() != "y":
        print("Aborted.")
        conn.close()
        return

    updated = 0
    for filepath, slug, page_id in matched:
        with open(filepath, "r", encoding="utf-8") as f:
            md_content = f.read()
        cursor.execute(
            "UPDATE history_page SET content = ? WHERE id = ?", (md_content, page_id)
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"\nDone — {updated} pages updated with markdown content.")


if __name__ == "__main__":
    run()
