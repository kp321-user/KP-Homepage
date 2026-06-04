import os
import sqlite3
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SQLITE_PATH = r"C:\Users\Ken\Python files\Link-DB\instance\links.db"
POSTGRES_URL = os.getenv("RENDER_DATABASE_URL")


def get_sqlite_links():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM link")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_postgres_links():
    conn = psycopg2.connect(POSTGRES_URL)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, url, title, thumbnail, category, type, date_added, last_modified FROM link"
    )
    cols = [desc[0] for desc in cursor.description]
    rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    conn.close()
    return rows


def sync():
    print("Fetching records...")
    sqlite_links = {r["id"]: r for r in get_sqlite_links()}
    postgres_links = {r["id"]: r for r in get_postgres_links()}

    all_ids = set(sqlite_links.keys()) | set(postgres_links.keys())

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cur = sqlite_conn.cursor()
    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_cur = pg_conn.cursor()

    for id in all_ids:
        in_sqlite = id in sqlite_links
        in_postgres = id in postgres_links

        if in_sqlite and not in_postgres:
            # exists locally, missing on Render — push to Render
            r = sqlite_links[id]
            print(f"Pushing to Render: {r['title']}")
            pg_cur.execute(
                """
                INSERT INTO link (id, url, title, thumbnail, category, type, date_added, last_modified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    r["id"],
                    r["url"],
                    r["title"],
                    r["thumbnail"],
                    r["category"],
                    r["type"],
                    r["date_added"],
                    r["last_modified"],
                ),
            )

        elif in_postgres and not in_sqlite:
            # exists on Render, missing locally — pull to local
            r = postgres_links[id]
            print(f"Pulling to local: {r['title']}")
            sqlite_cur.execute(
                """
                INSERT INTO link (id, url, title, thumbnail, category, type, date_added, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    r["id"],
                    r["url"],
                    r["title"],
                    r["thumbnail"],
                    r["category"],
                    r["type"],
                    r["date_added"],
                    r["last_modified"],
                ),
            )

        else:
            # exists in both — compare last_modified, newer wins
            s = sqlite_links[id]
            p = postgres_links[id]

            s_modified = s["last_modified"] or s["date_added"]
            p_modified = p["last_modified"] or p["date_added"]

            if s_modified and p_modified and str(s_modified) > str(p_modified):
                print(f"Local is newer, pushing: {s['title']}")
                pg_cur.execute(
                    """
                    UPDATE link SET url=%s, title=%s, thumbnail=%s,
                    category=%s, type=%s, last_modified=%s WHERE id=%s
                """,
                    (
                        s["url"],
                        s["title"],
                        s["thumbnail"],
                        s["category"],
                        s["type"],
                        s["last_modified"],
                        id,
                    ),
                )

            elif s_modified and p_modified and str(p_modified) > str(s_modified):
                print(f"Render is newer, pulling: {p['title']}")
                sqlite_cur.execute(
                    """
                    UPDATE link SET url=?, title=?, thumbnail=?,
                    category=?, type=?, last_modified=? WHERE id=?
                """,
                    (
                        p["url"],
                        p["title"],
                        p["thumbnail"],
                        p["category"],
                        p["type"],
                        p["last_modified"],
                        id,
                    ),
                )

    sqlite_conn.commit()
    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print("Sync complete!")


if __name__ == "__main__":
    sync()
