"""Day 1: send HTTP requests to httpbin.org and print the anatomy of each response."""

import json
import sys

import requests

BODY_PREVIEW_CHARS = 500


def inspect_request(
    method: str,
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float = 10.0,
) -> dict:
    """Send one HTTP request and return the key parts of the response.

    Returns a dict with: final_url, status_code, response_headers, body, elapsed_ms.
    The body is parsed JSON when the Content-Type is JSON, otherwise the
    first 500 characters of the text.

    Error-handling choice: this function does NOT catch exceptions. Timeouts,
    connection errors and invalid URLs are re-raised to the caller, so the
    return value always has the same shape. run_demo() is the place that
    catches them and prints a one-line message.

    Non-2xx status codes are NOT treated as errors here; they are just reported.
    """
    # Call requests.request through the module (not "from requests import request")
    # so tests can replace it with monkeypatch.
    response = requests.request(
        method, url, params=params, headers=headers, timeout=timeout
    )
    return {
        "final_url": response.url,
        "status_code": response.status_code,
        "response_headers": dict(response.headers),
        "body": _parse_body(response),
        "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 1),
    }


def _parse_body(response: requests.Response) -> dict | list | str:
    """Return parsed JSON for JSON responses, else the first 500 chars of text."""
    content_type = response.headers.get("Content-Type", "")
    if "json" in content_type.lower():
        try:
            return response.json()
        except ValueError:
            pass  # Server said JSON but sent something else: fall back to text.
    return response.text[:BODY_PREVIEW_CHARS]


def run_demo(title: str, method: str, url: str, **kwargs) -> dict | None:
    """Run inspect_request, print the result, and turn known errors into one line.

    Returns the result dict, or None if the request failed.
    """
    print(f"\n=== {title} ===")
    try:
        result = inspect_request(method, url, **kwargs)
    # Timeout must come before ConnectionError: a ConnectTimeout is both.
    except requests.Timeout:
        print(f"ERROR: request to {url} timed out")
        return None
    except requests.ConnectionError:
        print(f"ERROR: could not connect to {url}")
        return None
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL):
        print(f"ERROR: invalid URL {url!r} (did you forget https://?)")
        return None

    # ensure_ascii=False keeps Arabic text readable instead of \u escapes.
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> None:
    """Run the three Day 1 demos."""
    # On Windows, redirected/piped output defaults to cp1252, which cannot
    # print Arabic. Force UTF-8 so the output works everywhere.
    sys.stdout.reconfigure(encoding="utf-8")
    run_demo(
        "a) GET with query params and a custom header",
        "GET",
        "https://httpbin.org/get",
        params={"city": "Sfax", "q": "prix pc"},
        headers={"X-Student": "Tawfik"},
    )
    run_demo(
        "b) GET with an Arabic param (watch final_url get percent-encoded)",
        "GET",
        "https://httpbin.org/get",
        params={"name": "توفيق"},
    )
    run_demo(
        "c) GET an HTML page (non-JSON body)",
        "GET",
        "https://httpbin.org/html",
    )


if __name__ == "__main__":
    main()
