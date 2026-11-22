"""Tests for day03_json.transform. Pure functions: no network, no files."""

import pytest

from day03_json.transform import (
    CONTACT_FIELDS,
    get_nested,
    map_user,
    map_users,
    to_float,
)


def make_raw() -> dict:
    """Return a fresh copy of JSONPlaceholder user 1, safe to modify in a test."""
    return {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {"lat": "-37.3159", "lng": "81.1496"},
        },
        "phone": "1-770-736-8031 x56442",
        "website": "hildegard.org",
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets",
        },
    }


# --- get_nested ---


def test_get_nested_normal_path():
    assert get_nested(make_raw(), "address.geo.lat") == "-37.3159"


def test_get_nested_missing_middle_level():
    data = {"address": {"city": "Tunis"}}  # No "geo" level.

    assert get_nested(data, "address.geo.lat") is None
    assert get_nested(data, "address.geo.lat", default="n/a") == "n/a"


def test_get_nested_middle_level_is_a_string():
    data = {"address": "12 Rue de Marseille, Tunis"}

    assert get_nested(data, "address.city") is None


def test_get_nested_top_level_not_a_dict_does_not_raise():
    assert get_nested(None, "address.city", default="n/a") == "n/a"


def test_get_nested_empty_segment_is_a_literal_empty_key():
    # Documented behaviour: "" segments are not skipped, they look up the key "".
    data = {"address": {"geo": {"lat": "1"}}}

    assert get_nested(data, "address..geo") is None
    assert get_nested(data, "") is None
    assert get_nested({"": "found"}, "") == "found"


# --- to_float ---


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12.5", 12.5),
        ("-37.3159", -37.3159),
        ("abc", None),
        ("", None),
        (None, None),
        (7, 7.0),
        ("nan", None),  # Not a real coordinate.
        (True, None),  # bool is an int subclass, but not a number here.
    ],
)
def test_to_float(value, expected):
    assert to_float(value) == expected


def test_to_float_int_becomes_float_type():
    assert type(to_float(7)) is float


# --- map_user ---


def test_map_user_full_record():
    assert map_user(make_raw()) == {
        "id": 1,
        "full_name": "Leanne Graham",
        "email": "sincere@april.biz",
        "phone": "1-770-736-8031 x56442",
        "city": "Gwenborough",
        "company": "Romaguera-Crona",
        "website": "hildegard.org",
        "lat": -37.3159,
        "lng": 81.1496,
    }


def test_map_user_returns_exactly_the_schema_keys():
    assert tuple(map_user(make_raw())) == CONTACT_FIELDS


def test_map_user_without_address():
    raw = make_raw()
    del raw["address"]

    contact = map_user(raw)

    assert contact["city"] is None
    assert contact["lat"] is None
    assert contact["lng"] is None


def test_map_user_lat_not_a_number():
    raw = make_raw()
    raw["address"]["geo"]["lat"] = "not-a-number"

    contact = map_user(raw)

    assert contact["lat"] is None
    assert contact["lng"] == 81.1496  # The other coordinate is unaffected.


def test_map_user_email_is_stripped_and_lowercased():
    raw = make_raw()
    raw["email"] = "  Sincere@April.BIZ "

    assert map_user(raw)["email"] == "sincere@april.biz"


def test_map_user_strips_full_name():
    raw = make_raw()
    raw["name"] = "  Leanne Graham  "

    assert map_user(raw)["full_name"] == "Leanne Graham"


def test_map_user_missing_id():
    raw = make_raw()
    del raw["id"]

    with pytest.raises(ValueError, match="missing id"):
        map_user(raw)


def test_map_user_missing_email():
    raw = make_raw()
    del raw["email"]

    with pytest.raises(ValueError, match="missing email"):
        map_user(raw)


def test_map_user_blank_email():
    raw = make_raw()
    raw["email"] = "   "

    with pytest.raises(ValueError, match="missing email"):
        map_user(raw)


def test_map_user_email_without_at_sign():
    raw = make_raw()
    raw["email"] = "noatsign"

    with pytest.raises(ValueError, match="invalid email"):
        map_user(raw)


# --- map_users ---


def test_map_users_bad_middle_record_does_not_stop_the_others():
    first = make_raw()
    bad = make_raw()
    bad["id"] = 2
    bad["email"] = "noatsign"
    last = make_raw()
    last["id"] = 3

    good_rows, errors = map_users([first, bad, last])

    assert [row["id"] for row in good_rows] == [1, 3]
    assert errors == [
        {"index": 1, "raw_id": 2, "reason": "invalid email 'noatsign'"}
    ]


def test_map_users_non_dict_record_becomes_an_error():
    good_rows, errors = map_users([make_raw(), "not a record"])

    assert len(good_rows) == 1
    assert errors[0]["index"] == 1
    assert errors[0]["raw_id"] is None
