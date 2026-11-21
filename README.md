# automation-portfolio

Daily exercises while learning HTTP and API automation in Python.
Each day lives in its own folder (`day01_http/`, `day02_.../`, ...) with tests in `tests/`.

## Setup (once)

Requires Python 3.12 or newer (developed on 3.15). Windows PowerShell, from this folder:

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Day 1: HTTP anatomy

`day01_http/http_anatomy.py` sends requests to httpbin.org and prints each
response's final URL, status code, headers, body and elapsed time.

Demos:

- a) GET with query params and a custom `X-Student` header
- b) GET with an Arabic param, so you can see percent-encoding in `final_url`
- c) GET an HTML page (non-JSON body, truncated to 500 chars)

Timeouts, connection errors and invalid URLs print a one-line error and the
next demo still runs. Non-2xx status codes are reported, not raised (that's Day 2).

Run the script:

```powershell
python -m day01_http.http_anatomy
```

Run the tests (no network needed):

```powershell
python -m pytest -v
```

## Day 2: HTTP methods, status codes and retryable failures

`day02_methods/send.py` sends any HTTP method and returns a result dict
instead of raising, so the caller can decide what to do next:

- `classify_status(code)` gives the status family: `success`, `redirect`,
  `client_error`, `server_error` or `unknown`.
- `is_retryable(code)` is True only for 408, 429, 500, 502, 503 and 504.
- `send(method, url, *, json=None, params=None, timeout=10.0)` calls
  `raise_for_status()` and returns either
  `{"ok": True, "status", "body", "redirects"}` or
  `{"ok": False, "error_type", "status", "retryable", "detail"}`.
  `error_type` is `client_error`, `server_error`, `timeout`, `connection`
  or `invalid_url`. Timeouts and connection errors are retryable; an invalid
  URL is not. There is no retry loop yet (that's Day 5).

`day02_methods/demo.py` runs POST, PUT, PATCH and DELETE against httpbin.org,
then GETs a 204, 404, 422, 429, 503, a double redirect and a timeout, printing
one line per call. For the POST it also prints what httpbin echoed back, to
show that `json=` sent a JSON body and set `Content-Type: application/json`.

Run the demo:

```powershell
python -m day02_methods.demo
```

Run the tests (no network needed):

```powershell
python -m pytest -v
```
