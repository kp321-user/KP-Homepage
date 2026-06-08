import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SQLITE_PATH = r"C:\Users\Ken\Python files\Link-DB\instance\kp_db_2026.db"
POSTGRES_URL = os.getenv("RENDER_DATABASE_URL")
if not POSTGRES_URL:
    raise EnvironmentError("RENDER_DATABASE_URL is not set in the environment.")


def get_sqlite_rows(table, columns):
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT {', '.join(columns)} FROM {table}")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def push_table(table, columns, label_col):
    rows = get_sqlite_rows(table, columns)

    col_list = ", ".join(columns)
    pg_placeholders = ", ".join(["%s"] * len(columns))
    update_cols = [c for c in columns if c != "id"]
    update_clause = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])

    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()

    try:
        for r in rows:
            values = [r[c] for c in columns]
            cur.execute(
                f"""
                INSERT INTO {table} ({col_list})
                VALUES ({pg_placeholders})
                ON CONFLICT (id) DO UPDATE SET {update_clause}
                """,
                values,
            )
            print(f"  Pushed: {r.get(label_col, r.get('id'))}")

        local_ids = [r["id"] for r in rows]
        if local_ids:
            cur.execute(
                f"DELETE FROM {table} WHERE id != ALL(%s)",
                (local_ids,),
            )
        else:
            cur.execute(f"DELETE FROM {table}")
        deleted = cur.rowcount
        if deleted:
            print(f"  Deleted {deleted} removed row(s) from Render.")

        cur.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), MAX(id)) FROM {table}"
        )
        conn.commit()
        print(f"{table}: {len(rows)} rows pushed.")
    except Exception as e:
        conn.rollback()
        print(f"Push failed for {table}: {e}")
        raise
    finally:
        conn.close()


def push():
    print("Pushing links...")
    push_table(
        "link",
        ["id", "url", "title", "thumbnail", "category", "type", "date_added", "last_modified"],
        "title",
    )

    print("Pushing history pages...")
    push_table(
        "history_page",
        ["id", "title", "slug", "era", "period", "phase", "start_year", "date_added", "last_modified", "content"],
        "title",
    )

    print("Push complete!")


if __name__ == "__main__":
    push()
