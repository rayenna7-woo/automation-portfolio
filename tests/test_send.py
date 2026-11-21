"""Tests for day02_methods.send. No real network calls are made."""

import pytest
import requests

from day02_methods import send as send_module


class FakeResponse:
    """The minimal subset of requests.Response that send() uses."""

    def __init__(
        self,
        status_code: int,
        headers: dict | None = None,
        text: str = "",
        json_data=None,
        history: list | None = None,
        reason: str = "FAKE REASON",
    ):
        self.status_code = status_code
        self.headers = headers or {}
        self.text = text
        self.history = history or []
        self.reason = reason
        self._json_data = json_data

    def json(self):
        if self._json_data is None:
            raise AssertionError("json() should not have been called")
        return self._json_data

    def raise_for_status(self):
        # Same contract as the real one: HTTPError carrying this response.
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)


def fake_request_returning(response: FakeResponse):
    """Build a stand-in for requests.request that always returns `response`."""

    def fake_request(method, url, **kwargs):
        return response

    return fake_request


def fake_request_raising(exc: Exception):
    """Build a stand-in for requests.request that always raises `exc`."""

    def fake_request(method, url, **kwargs):
        raise exc

    return fake_request


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (200, "success"),
        (201, "success"),
        (204, "success"),
        (301, "redirect"),
        (400, "client_error"),
        (404, "client_error"),
        (422, "client_error"),
        (429, "client_error"),
        (500, "server_error"),
        (503, "server_error"),
        (99, "unknown"),
        (600, "unknown"),
    ],
)
def test_classify_status(code, expected):
    assert send_module.classify_status(code) == expected


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (400, False),
        (401, False),
        (404, False),
        (422, False),
        (408, True),
        (429, True),
        (500, True),
        (502, True),
        (503, True),
        (504, True),
    ],
)
def test_is_retryable(code, expected):
    assert send_module.is_retryable(code) is expected


def test_success_with_json_body(monkeypatch):
    fake = FakeResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        text='{"id": 7}',
        json_data={"id": 7},
        history=[FakeResponse(302), FakeResponse(302)],
    )
    monkeypatch.setattr(requests, "request", fake_request_returning(fake))

    result = send_module.send("GET", "https://example.test/fake")

    assert result == {"ok": True, "status": 200, "body": {"id": 7}, "redirects": 2}


def test_204_gives_none_body_without_calling_json(monkeypatch):
    # The fake has no json_data, so its json() raises if send() calls it.
    fake = FakeResponse(status_code=204, headers={"Content-Type": "application/json"})
    monkeypatch.setattr(requests, "request", fake_request_returning(fake))

    result = send_module.send("GET", "https://example.test/fake")

    assert result["ok"] is True
    assert result["status"] == 204
    assert result["body"] is None


@pytest.mark.parametrize(
    ("status", "error_type", "retryable"),
    [
        (404, "client_error", False),
        (503, "server_error", True),
        (429, "client_error", True),  # A 4xx that is still worth retrying.
    ],
)
def test_http_error_statuses(monkeypatch, status, error_type, retryable):
    fake = FakeResponse(status_code=status, reason="SOME REASON")
    monkeypatch.setattr(requests, "request", fake_request_returning(fake))

    result = send_module.send("GET", "https://example.test/fake")

    assert result == {
        "ok": False,
        "error_type": error_type,
        "status": status,
        "retryable": retryable,
        "detail": f"HTTP {status} SOME REASON",
    }


@pytest.mark.parametrize(
    ("exc", "error_type", "retryable"),
    [
        (requests.Timeout(), "timeout", True),
        # ConnectTimeout is both a Timeout and a ConnectionError.
        (requests.exceptions.ConnectTimeout(), "timeout", True),
        (requests.ConnectionError(), "connection", True),
        (requests.exceptions.MissingSchema("no scheme"), "invalid_url", False),
    ],
)
def test_network_and_url_errors(monkeypatch, exc, error_type, retryable):
    monkeypatch.setattr(requests, "request", fake_request_raising(exc))

    result = send_module.send("GET", "https://example.test/fake")

    assert result["ok"] is False
    assert result["error_type"] == error_type
    assert result["status"] is None
    assert result["retryable"] is retryable


def test_post_passes_json_and_timeout_to_requests(monkeypatch):
    recorded = {}

    def fake_request(method, url, **kwargs):
        recorded["method"] = method
        recorded["url"] = url
        recorded["kwargs"] = kwargs
        return FakeResponse(status_code=201)

    monkeypatch.setattr(requests, "request", fake_request)

    send_module.send(
        "POST", "https://example.test/leads", json={"name": "Ali"}, timeout=3.5
    )

    assert recorded["method"] == "POST"
    assert recorded["url"] == "https://example.test/leads"
    assert recorded["kwargs"]["json"] == {"name": "Ali"}
    assert recorded["kwargs"]["timeout"] == 3.5
