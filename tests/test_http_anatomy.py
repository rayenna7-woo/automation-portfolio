"""Tests for day01_http.http_anatomy. No real network calls are made."""

from datetime import timedelta

import pytest
import requests

from day01_http import http_anatomy


class FakeResponse:
    """The minimal subset of requests.Response that inspect_request uses."""

    def __init__(self, status_code: int, headers: dict, text: str, json_data=None):
        self.status_code = status_code
        self.headers = headers
        self.text = text
        self.url = "https://example.test/fake"
        self.elapsed = timedelta(milliseconds=42)
        self._json_data = json_data

    def json(self):
        return self._json_data


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


def test_json_response_gives_dict_body_and_status(monkeypatch):
    fake = FakeResponse(
        status_code=201,
        headers={"Content-Type": "application/json"},
        text='{"ok": true}',
        json_data={"ok": True},
    )
    monkeypatch.setattr(requests, "request", fake_request_returning(fake))

    result = http_anatomy.inspect_request("GET", "https://example.test/fake")

    assert result["status_code"] == 201
    assert result["body"] == {"ok": True}
    assert result["final_url"] == "https://example.test/fake"
    assert result["elapsed_ms"] == 42.0


def test_html_response_gives_string_body_truncated_to_500(monkeypatch):
    long_html = "<p>" + "x" * 1000 + "</p>"
    fake = FakeResponse(
        status_code=200,
        headers={"Content-Type": "text/html; charset=utf-8"},
        text=long_html,
    )
    monkeypatch.setattr(requests, "request", fake_request_returning(fake))

    result = http_anatomy.inspect_request("GET", "https://example.test/fake")

    assert isinstance(result["body"], str)
    assert len(result["body"]) == 500
    assert result["body"] == long_html[:500]


def test_timeout_is_reraised_by_inspect_request(monkeypatch):
    monkeypatch.setattr(requests, "request", fake_request_raising(requests.Timeout()))

    with pytest.raises(requests.Timeout):
        http_anatomy.inspect_request("GET", "https://example.test/fake")


def test_timeout_is_reported_by_run_demo_without_crashing(monkeypatch, capsys):
    monkeypatch.setattr(requests, "request", fake_request_raising(requests.Timeout()))

    result = http_anatomy.run_demo("t", "GET", "https://example.test/fake")

    assert result is None
    assert "timed out" in capsys.readouterr().out


def test_invalid_url_without_scheme_is_handled_cleanly(monkeypatch, capsys):
    # Real requests raises MissingSchema while building the URL, before any
    # network I/O. The fake does the same so the test never touches the network.
    monkeypatch.setattr(
        requests,
        "request",
        fake_request_raising(requests.exceptions.MissingSchema("no scheme")),
    )

    result = http_anatomy.run_demo("bad", "GET", "httpbin.org/get")

    assert result is None
    assert "invalid URL 'httpbin.org/get'" in capsys.readouterr().out
