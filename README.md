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
