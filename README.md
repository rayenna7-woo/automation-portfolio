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

## Day 3: nested JSON, mapping to my own schema, CSV and SQLite

`day03_json/` is a small ETL pipeline: fetch users from JSONPlaceholder, map
each one to my own "contact" schema, save the result to CSV and SQLite.

- `extract.py`: `fetch_users(url, timeout)` GETs the users, calls
  `raise_for_status()` and raises `ValueError` if the JSON is not a list.
- `transform.py` (pure functions, no network or files):
  - `get_nested(data, "address.geo.lat", default)` walks nested dicts and
    returns `default` if a level is missing or is not a dict. It never raises.
  - `to_float(value)` gives a float or `None` (`"abc"`, `""`, `None`).
  - `map_user(raw)` returns exactly the keys `id, full_name, email, phone,
    city, company, website, lat, lng`. The email is stripped and lowercased.
    A missing id or a missing/invalid email raises `ValueError`.
  - `map_users(raws)` returns `(good_rows, errors)`. One bad record becomes
    `{"index", "raw_id", "reason"}` and the others are still mapped.
- `load.py`:
  - `write_csv(rows, path)` writes UTF-8 with a BOM (`utf-8-sig`) so Excel
    shows Arabic names correctly.
  - `save_sqlite(rows, db_path)` upserts with `ON CONFLICT(id) DO UPDATE`, so
    re-running updates existing rows instead of duplicating them. Values are
    always passed as SQL parameters, never put into the SQL string.
- `pipeline.py`: extract -> transform -> load, then prints the counts.

Output goes to `data/contacts.csv` and `data/contacts.db`. `data/` is in
`.gitignore` because these files are generated.

Run the pipeline (run it twice: the DB still has 10 rows):

```powershell
python -m day03_json.pipeline
```

Run the tests (no network needed):

```powershell
python -m pytest -v
```
