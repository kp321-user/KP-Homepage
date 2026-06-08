import os
import sqlite3
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SQLITE_PATH = r"C:\Users\Ken\Python files\Link-DB\instance\kp_db_2026.db"
POSTGRES_URL = os.getenv("RENDER_DATABASE_URL")
if not POSTGRES_URL:
    raise EnvironmentError("RENDER_DATABASE_URL is not set in the environment.")


def parse_dt(val):
    if val is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(val, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.min.replace(tzinfo=timezone.utc)


# ── Links ──────────────────────────────────────────────


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


# ── History Pages ──────────────────────────────────────


def get_sqlite_history():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history_page")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_postgres_history():
    conn = psycopg2.connect(POSTGRES_URL)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, slug, era, period, phase, start_year, date_added, last_modified, content FROM history_page"
    )
    cols = [desc[0] for desc in cursor.description]
    rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    conn.close()
    return rows


# ── Sync Logic ─────────────────────────────────────────


def sync_table(sqlite_records, postgres_records, sqlite_cur, pg_cur, table, columns):
    sqlite_dict = {r["id"]: r for r in sqlite_records}
    postgres_dict = {r["id"]: r for r in postgres_records}
    all_ids = set(sqlite_dict.keys()) | set(postgres_dict.keys())

    col_list = ", ".join(columns)
    sqlite_placeholders = ", ".join(["?" for _ in columns])
    pg_placeholders = ", ".join(["%s" for _ in columns])

    for id in all_ids:
        in_sqlite = id in sqlite_dict
        in_postgres = id in postgres_dict

        if in_sqlite and not in_postgres:
            r = sqlite_dict[id]
            print(f"  Pushing to Render: {r.get('title', r.get('url', id))}")
            values = [r.get(c) for c in columns]
            pg_cur.execute(
                f"INSERT INTO {table} ({col_list}) VALUES ({pg_placeholders})", values
            )
            pg_cur.execute(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), MAX(id)) FROM {table}"
            )

        elif in_postgres and not in_sqlite:
            r = postgres_dict[id]
            print(f"  Pulling to local: {r.get('title', r.get('url', id))}")
            values = [r.get(c) for c in columns]
            sqlite_cur.execute(
                f"INSERT INTO {table} ({col_list}) VALUES ({sqlite_placeholders})",
                values,
            )

        else:
            s = sqlite_dict[id]
            p = postgres_dict[id]
            s_modified = parse_dt(s.get("last_modified") or s.get("date_added"))
            p_modified = parse_dt(p.get("last_modified") or p.get("date_added"))

            update_cols = [c for c in columns if c != "id"]

            if s_modified > p_modified:
                print(f"  Local newer, pushing: {s.get('title', s.get('url', id))}")
                set_clause = ", ".join([f"{c} = %s" for c in update_cols])
                values = [s.get(c) for c in update_cols] + [id]
                pg_cur.execute(f"UPDATE {table} SET {set_clause} WHERE id = %s", values)

            elif p_modified > s_modified:
                print(f"  Render newer, pulling: {p.get('title', p.get('url', id))}")
                set_clause = ", ".join([f"{c} = ?" for c in update_cols])
                values = [p.get(c) for c in update_cols] + [id]
                sqlite_cur.execute(
                    f"UPDATE {table} SET {set_clause} WHERE id = ?", values
                )


# ── Main ───────────────────────────────────────────────


def sync():
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cur = sqlite_conn.cursor()
    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_cur = pg_conn.cursor()

    try:
        print("Syncing links...")
        sync_table(
            get_sqlite_links(),
            get_postgres_links(),
            sqlite_cur,
            pg_cur,
            "link",
            [
                "id",
                "url",
                "title",
                "thumbnail",
                "category",
                "type",
                "date_added",
                "last_modified",
            ],
        )

        print("Syncing history pages...")
        sync_table(
            get_sqlite_history(),
            get_postgres_history(),
            sqlite_cur,
            pg_cur,
            "history_page",
            [
                "id",
                "title",
                "slug",
                "era",
                "period",
                "phase",
                "start_year",
                "date_added",
                "last_modified",
                "content",
            ],
        )

        sqlite_conn.commit()
        pg_conn.commit()
        print("Sync complete!")

    except Exception as e:
        sqlite_conn.rollback()
        pg_conn.rollback()
        print(f"Sync failed: {e}")
        raise

    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    sync()
