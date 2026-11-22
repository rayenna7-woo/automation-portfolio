"""Tests for day03_json.load. Files go in pytest's tmp_path, never in data/."""

import codecs
import csv
import sqlite3
from contextlib import closing

from day03_json.load import save_sqlite, write_csv
from day03_json.transform import CONTACT_FIELDS


def make_row(contact_id: int, **overrides) -> dict:
    """Return a valid contact row; keyword arguments replace single fields."""
    row = {
        "id": contact_id,
        "full_name": f"Contact {contact_id}",
        "email": f"contact{contact_id}@example.com",
        "phone": "+216 71 000 000",
        "city": "Tunis",
        "company": "Acme",
        "website": "example.com",
        "lat": 36.8065,
        "lng": 10.1815,
    }
    row.update(overrides)
    return row


def read_contact(db_path, contact_id: int) -> dict:
    """Read one row back from the contacts table as a dict."""
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM contacts WHERE id = ?", (contact_id,)
        ).fetchone()
    return dict(row)


# --- write_csv ---


def test_write_csv_round_trip(tmp_path):
    path = tmp_path / "nested" / "contacts.csv"  # Parent folder does not exist yet.
    rows = [
        make_row(1, full_name="توفيق بلقيث"),
        make_row(2, company="Romaguera, Crona and Sons"),
    ]

    write_csv(rows, path)

    assert path.read_bytes().startswith(codecs.BOM_UTF8)  # utf-8-sig, for Excel.
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        read_back = list(reader)
    assert reader.fieldnames == list(CONTACT_FIELDS)
    assert len(read_back) == 2
    assert read_back[0]["full_name"] == "توفيق بلقيث"
    assert read_back[1]["company"] == "Romaguera, Crona and Sons"


def test_write_csv_none_becomes_empty_cell(tmp_path):
    path = tmp_path / "contacts.csv"

    write_csv([make_row(1, phone=None)], path)

    with path.open(encoding="utf-8-sig", newline="") as file:
        assert next(csv.DictReader(file))["phone"] == ""


# --- save_sqlite ---


def test_save_sqlite_twice_does_not_duplicate(tmp_path):
    db_path = tmp_path / "contacts.db"
    rows = [make_row(1), make_row(2)]

    assert save_sqlite(rows, db_path) == 2
    assert save_sqlite(rows, db_path) == 2


def test_save_sqlite_updates_changed_email(tmp_path):
    db_path = tmp_path / "contacts.db"
    save_sqlite([make_row(1, email="old@example.com")], db_path)

    count = save_sqlite([make_row(1, email="new@example.com")], db_path)

    assert count == 1
    assert read_contact(db_path, 1)["email"] == "new@example.com"


def test_save_sqlite_quote_in_name(tmp_path):
    db_path = tmp_path / "contacts.db"

    save_sqlite([make_row(1, full_name="O'Brien")], db_path)

    assert read_contact(db_path, 1)["full_name"] == "O'Brien"


def test_save_sqlite_stores_none_as_null_and_floats_as_real(tmp_path):
    db_path = tmp_path / "contacts.db"

    save_sqlite([make_row(1, phone=None, lat=None)], db_path)

    stored = read_contact(db_path, 1)
    assert stored["phone"] is None
    assert stored["lat"] is None
    assert stored["lng"] == 10.1815
