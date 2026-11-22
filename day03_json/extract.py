"""Day 3 extract step: fetch raw users from JSONPlaceholder."""

import requests

USERS_URL = "https://jsonplaceholder.typicode.com/users"


def fetch_users(url: str = USERS_URL, timeout: float = 10.0) -> list[dict]:
    """GET `url` and return the parsed JSON list of user records.

    Raises requests.HTTPError for 4xx/5xx, other requests exceptions for
    network problems, and ValueError if the body is not a JSON list.
    """
    # Call requests.get through the module so tests can monkeypatch it.
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()  # Raises a ValueError subclass if the body is not JSON.
    if not isinstance(data, list):
        raise ValueError(f"expected a JSON list, got {type(data).__name__}")
    return data
