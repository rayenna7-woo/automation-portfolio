"""Day 3 pipeline: extract users -> transform to contacts -> load to CSV and SQLite."""

from pathlib import Path

import requests

from day03_json.extract import fetch_users
from day03_json.load import save_sqlite, write_csv
from day03_json.transform import map_users


def main() -> int:
    """Run the ETL pipeline once and print a summary. Return the exit code."""
    # data/ sits next to day03_json/, whatever folder the script is run from.
    data_dir = Path(__file__).resolve().parent.parent / "data"

    try:
        raws = fetch_users()
    except (requests.RequestException, ValueError) as exc:
        print(f"fetch failed: {exc}")
        return 1
    print(f"fetched {len(raws)}")

    rows, errors = map_users(raws)
    print(f"mapped {len(rows)}")
    print(f"errors {len(errors)}")
    for error in errors:
        print(f"  index={error['index']} raw_id={error['raw_id']}: {error['reason']}")

    write_csv(rows, data_dir / "contacts.csv")
    total = save_sqlite(rows, data_dir / "contacts.db")
    print(f"rows in DB {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
