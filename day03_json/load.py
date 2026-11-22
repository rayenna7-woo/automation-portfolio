"""Day 3 load step: save contact rows to CSV and to SQLite."""

import csv
import sqlite3
from contextlib import closing
from pathlib import Path

from day03_json.transform import CONTACT_FIELDS

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS contacts (
    id        INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email     TEXT NOT NULL,
    phone     TEXT,
    city      TEXT,
    company   TEXT,
    website   TEXT,
    lat       REAL,
    lng       REAL
)
"""

# Named placeholders (:id, ...) are filled from each row dict by sqlite3.
# If the id already exists, the existing row is updated instead of duplicated.
# "excluded" is SQLite's name for the new row we tried to insert.
UPSERT_SQL = """
INSERT INTO contacts (id, full_name, email, phone, city, company, website, lat, lng)
VALUES (:id, :full_name, :email, :phone, :city, :company, :website, :lat, :lng)
ON CONFLICT(id) DO UPDATE SET
    full_name = excluded.full_name,
    email     = excluded.email,
    phone     = excluded.phone,
    city      = excluded.city,
    company   = excluded.company,
    website   = excluded.website,
    lat       = excluded.lat,
    lng       = excluded.lng
"""

COUNT_SQL = "SELECT COUNT(*) FROM contacts"


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to a CSV file with a header row, creating the folder if needed.

    utf-8-sig adds a BOM so Excel opens Arabic text correctly.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CONTACT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def save_sqlite(rows: list[dict], db_path: Path) -> int:
    """Upsert rows into the contacts table and return the table's total row count."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # "with sqlite3.connect()" alone does NOT close the connection: it only
    # commits on success or rolls back on an exception. closing() closes it.
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(CREATE_TABLE_SQL)
            conn.executemany(UPSERT_SQL, rows)
        (count,) = conn.execute(COUNT_SQL).fetchone()
    return count
