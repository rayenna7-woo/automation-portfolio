"""Day 3 transform step: map raw JSONPlaceholder users to my contact schema.

Pure functions only: no network, no files.
"""

import math

# Column order for the contact schema. load.py uses it for CSV and SQLite.
CONTACT_FIELDS = (
    "id",
    "full_name",
    "email",
    "phone",
    "city",
    "company",
    "website",
    "lat",
    "lng",
)


def get_nested(data: dict, path: str, default=None):
    """Return the value at a dotted path like "address.geo.lat", or `default`.

    Each segment is used as a literal dict key. If any level is missing or is
    not a dict, `default` is returned; it never raises.

    Empty segments are not skipped: "address..lat" looks up the key "" inside
    "address", and path "" looks up the key "" at the top. Real records have no
    "" key, so both normally return `default`.
    """
    current = data
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def to_float(value) -> float | None:
    """Convert value to a finite float, or return None if that is not possible.

    "12.5" -> 12.5, 7 -> 7.0, "abc" / "" / None -> None.
    Booleans and "nan"/"inf" also give None: they are not real coordinates.
    """
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def map_user(raw: dict) -> dict:
    """Map one raw JSONPlaceholder user to a dict with the CONTACT_FIELDS keys.

    Raises ValueError if the record is not a dict, the id is missing or not an
    int, or the email is missing, empty or has no "@".
    """
    if not isinstance(raw, dict):
        raise ValueError(f"record is not a dict: {raw!r}")

    user_id = raw.get("id")
    if user_id is None:
        raise ValueError("missing id")
    # bool is a subclass of int, so True would otherwise pass as id 1.
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise ValueError(f"id must be an int, got {user_id!r}")

    email = _optional_str(raw.get("email"))
    if email is None:
        raise ValueError("missing email")
    if "@" not in email:
        raise ValueError(f"invalid email {email!r}")

    return {
        "id": user_id,
        "full_name": _optional_str(raw.get("name")) or "",
        "email": email.lower(),
        "phone": _optional_str(raw.get("phone")),
        "city": _optional_str(get_nested(raw, "address.city")),
        "company": _optional_str(get_nested(raw, "company.name")),
        "website": _optional_str(raw.get("website")),
        "lat": to_float(get_nested(raw, "address.geo.lat")),
        "lng": to_float(get_nested(raw, "address.geo.lng")),
    }


def map_users(raws: list[dict]) -> tuple[list[dict], list[dict]]:
    """Map every raw record and return (good_rows, errors).

    A bad record becomes {"index", "raw_id", "reason"} in errors and the
    remaining records are still mapped.
    """
    good_rows = []
    errors = []
    for index, raw in enumerate(raws):
        try:
            good_rows.append(map_user(raw))
        except ValueError as exc:
            raw_id = raw.get("id") if isinstance(raw, dict) else None
            errors.append({"index": index, "raw_id": raw_id, "reason": str(exc)})
    return good_rows, errors


def _optional_str(value) -> str | None:
    """Return the stripped string, or None if value is not a string or is blank."""
    if not isinstance(value, str):
        return None
    return value.strip() or None
