"""Day 2 demo: call httpbin.org with different methods and status codes."""

from day02_methods.send import send


def summarize(method: str, url: str, result: dict) -> str:
    """Return a one-line summary of a send() result."""
    if result["ok"]:
        outcome = f"ok {result['status']} redirects={result['redirects']}"
    else:
        outcome = (
            f"FAIL {result['error_type']} status={result['status']} "
            f"retryable={result['retryable']} ({result['detail']})"
        )
    return f"{method:<6} {url:<36} -> {outcome}"


def main() -> None:
    """Send each demo request and print one line per call."""
    calls = [
        ("POST", "https://httpbin.org/post", {"json": {"name": "Ali", "email": "ali@example.com"}}),
        ("PUT", "https://httpbin.org/put", {"json": {"status": "qualified"}}),
        ("PATCH", "https://httpbin.org/patch", {"json": {"score": 80}}),
        ("DELETE", "https://httpbin.org/delete", {}),
        ("GET", "https://httpbin.org/status/204", {}),
        ("GET", "https://httpbin.org/status/404", {}),
        ("GET", "https://httpbin.org/status/422", {}),
        ("GET", "https://httpbin.org/status/429", {}),
        ("GET", "https://httpbin.org/status/503", {}),
        ("GET", "https://httpbin.org/redirect/2", {}),
        ("GET", "https://httpbin.org/delay/5", {"timeout": 2}),
    ]
    for method, url, kwargs in calls:
        result = send(method, url, **kwargs)
        print(summarize(method, url, result))

        # httpbin echoes the request back: prove json= sent a JSON body
        # and set the Content-Type header for us.
        if method == "POST" and result["ok"]:
            print(f"       echoed json:  {result['body']['json']}")
            print(f"       Content-Type: {result['body']['headers']['Content-Type']}")


if __name__ == "__main__":
    main()
