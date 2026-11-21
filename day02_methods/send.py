"""Day 2: send any HTTP method and return a structured ok/failure result."""

import requests

BODY_PREVIEW_CHARS = 300
RETRYABLE_STATUSES = frozenset({408, 429, 500, 502, 503, 504})


def classify_status(code: int) -> str:
    """Return the family of an HTTP status code, e.g. 404 -> "client_error"."""
    if 200 <= code < 300:
        return "success"
    if 300 <= code < 400:
        return "redirect"
    if 400 <= code < 500:
        return "client_error"
    if 500 <= code < 600:
        return "server_error"
    return "unknown"


def is_retryable(code: int) -> bool:
    """Return True if sending the same request again could succeed.

    408 (request timeout) and 429 (too many requests) are 4xx codes that are
    still worth retrying; other 4xx mean the request itself is wrong.
    """
    return code in RETRYABLE_STATUSES


def send(
    method: str,
    url: str,
    *,
    json: dict | None = None,
    params: dict | None = None,
    timeout: float = 10.0,
) -> dict:
    """Send one HTTP request and return a result dict instead of raising.

    Success: {"ok": True, "status", "body", "redirects"}
    Failure: {"ok": False, "error_type", "status", "retryable", "detail"}

    Only the exceptions listed below are caught. Anything else (for example
    TooManyRedirects) is a bug or an unexpected case and is re-raised.
    """
    try:
        # Call requests.request through the module so tests can monkeypatch it.
        response = requests.request(
            method, url, json=json, params=params, timeout=timeout
        )
        response.raise_for_status()  # Raises HTTPError for 4xx and 5xx.
    except requests.HTTPError as exc:
        status = exc.response.status_code
        return _failure(
            classify_status(status),
            status,
            is_retryable(status),
            f"HTTP {status} {exc.response.reason}",
        )
    # Timeout must come before ConnectionError: a ConnectTimeout is both.
    except requests.Timeout:
        return _failure("timeout", None, True, f"no response within {timeout}s")
    except requests.ConnectionError:
        return _failure("connection", None, True, "could not connect to the server")
    except (
        requests.exceptions.MissingSchema,
        requests.exceptions.InvalidSchema,
        requests.exceptions.InvalidURL,
    ):
        return _failure("invalid_url", None, False, f"invalid URL {url!r}")

    return {
        "ok": True,
        "status": response.status_code,
        "body": _parse_body(response),
        "redirects": len(response.history),
    }


def _failure(error_type: str, status: int | None, retryable: bool, detail: str) -> dict:
    """Build the failure result dict so every failure has the same shape."""
    return {
        "ok": False,
        "error_type": error_type,
        "status": status,
        "retryable": retryable,
        "detail": detail,
    }


def _parse_body(response: requests.Response) -> dict | list | str | None:
    """Return None for 204/empty, parsed JSON for JSON, else the first 300 chars."""
    if response.status_code == 204 or not response.text:
        return None
    content_type = response.headers.get("Content-Type", "")
    if "json" in content_type.lower():
        try:
            return response.json()
        except ValueError:
            pass  # Server said JSON but sent something else: fall back to text.
    return response.text[:BODY_PREVIEW_CHARS]
