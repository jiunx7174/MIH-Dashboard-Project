# PDU RTDC logging

## When something goes wrong on the server

```bash
cd /home/admin/streamlit/MIH-Dashboard-Project
bash Streamlit_App_v3/Tools/collect_logs.sh          # last 7 days; or e.g. `... 24` for 24 h; add sudo if docker needs it
```

Download the `pdu_logs_<date>.tgz` it prints and share it. It is read-only: it copies logs, reads Docker state and calls two GET status endpoints.

If a user saw an error on screen, also share the **error code** shown there (8 characters, e.g. `a1b2c3d4`). That code is the `run_id` of their page run, and every log line of that run carries it.

## What is in the archive

| Path | Content |
|---|---|
| `SUMMARY.txt` | **Read first.** Restarts, errors grouped by cause (with wells and users), syncs per well, slow requests and pages, users per well, memory. |
| `logs/errors_<app>.jsonl` | WARNING and above only. |
| `logs/app_<app>.jsonl` | Every event: requests, syncs and their stages, page runs, `print()` lines. |
| `logs/memlog.jsonl` | FastAPI memory: request RSS and heartbeats every 30 s. |
| `docker/<container>.log` | Raw stdout/stderr of each container, with timestamps. |
| `docker/<container>.state.txt` | Start time, exit code, `oom_killed` and restart count. |
| `system/` | Host uptime, memory and disk, the git commit, and FastAPI `/sync-status/` and `/memlog/status`. |

`<app>` is `streamlit` or `fastapi`. Each process writes its own files, one per day (rotated at 00:00 UTC = 07:00 WIB, suffix `.YYYY-MM-DD`). `app_*` is kept 14 days and `errors_*` 30 days. The files live in `Streamlit_App_v3/Logs/`, which is on the host through the existing bind mounts and is git-ignored.

## Line format (`app_*.jsonl`, `errors_*.jsonl`)

One JSON object per line.

| Field | Meaning |
|---|---|
| `ts` | Time in **WIB** with offset, e.g. `2026-11-18T10:05:17.599+07:00`. The containers run in UTC, and `memlog.jsonl` uses UTC without an offset. |
| `level` | `INFO`, `WARNING`, `ERROR` or `CRITICAL`. |
| `app`, `pid` | `streamlit` or `fastapi`, and the process id. A new pid means a restart. |
| `event` | What happened; see the next table. |
| `run_id` | One FastAPI request, or one Streamlit script run. It is also the error code shown to users and returned in the `X-Request-ID` header. |
| `wid`, `cid`, `well`, `company` | The well and company being worked on. |
| `page`, `session` | Streamlit page and hashed browser session. |
| `user_name`, `user_id`, `user_company` | Who used the page (Streamlit). The login token (`?ID=`) and the email are never logged. |
| `client` | Caller IP of a FastAPI request (e.g. the DOME scheduler). |
| `endpoint`, `method`, `status`, `duration_ms` | FastAPI request fields. |
| `kind` | Sync endpoint name, e.g. `update_realtime_data`. |
| `error_type`, `error`, `where`, `traceback` | Exception details. `where` is the deepest frame in this project's code. |
| `fingerprint` | Hash of the error type and `where`. The same bug always has the same fingerprint. |
| `repeated` | How many identical warnings were suppressed before this one. Repeats are logged once per 10 min. |

## Events

| Event | App | Meaning |
|---|---|---|
| `process_start` | both | Process started, with the git commit and package versions. |
| `request` | fastapi | One HTTP request. 5xx is ERROR and ≥ 30 s is WARNING. Scanner 404s are not logged. |
| `request_error` | fastapi | Unhandled exception in a request, with the traceback. |
| `sync_start` / `sync_done` / `sync_failed` / `sync_rejected` | fastapi | Per-well sync lifecycle. `rejected` is a 409 because a sync for that well was already running. |
| `stage` | both | A step inside a sync or Recalculate (`section_params`, `sync_range`, `realtime_downloaded`, `grouped`, `stand_labelled`, `actsum_deleted`, `actsum_inserted`, …). DataFrames are logged as `{rows, cols}`. |
| `page_run` | streamlit | One script run of a page. `outcome` is `ok`, `stopped` (st.stop/st.rerun) or `error`. Over 120 s is WARNING. |
| `page_error` | streamlit | Exception in a page. The user saw the error code. |
| `step_failed` | streamlit | A DOME/FastAPI call wrapped in `call_or_stop` failed. `step` names it. |
| `print` | both | A `print()` line with the current context. Lines that look like errors (error, failed, timeout, …) are WARNING. |
| `uncaught_exception`, `thread_exception` | both | Crash outside a request or page. |

## Quick queries

```bash
grep '"run_id": "a1b2c3d4"' logs/app_*.jsonl          # everything about one error code / request
grep '"fingerprint": "3f2a9c1e"' logs/errors_*.jsonl   # every occurrence of one bug
grep '"wid": 506' logs/app_fastapi.jsonl | grep '"event": "sync_'   # sync history of one well
grep '"user_name": "Admin(TEST)"' logs/app_streamlit.jsonl   # what one user did
python3 Tools/log_summary.py --hours 24 Logs/          # summary over a shorter window (default 168 h)
```

## Settings (environment variables, optional)

| Variable | Default | |
|---|---|---|
| `PDU_LOG_DIR` | `Streamlit_App_v3/Logs` | log folder |
| `PDU_LOG_TZ_HOURS` | `7` | UTC offset used for `ts` |
| `PDU_LOG_CAPTURE_PRINT` | `1` | log `print()` lines as events |
| `PDU_LOG_DEDUPE_S` | `600` | repeat window for identical warnings |
| `PDU_LOG_KEEP_DAYS` | `14` | days of `app_*.jsonl` kept |
| `PDU_LOG_KEEP_ERROR_DAYS` | `30` | days of `errors_*.jsonl` kept |
| `PDU_VERBOSE_LOG` | `0` | detailed per-chunk prints (existing) |

Code: `PDU_Func/AppLog.py`. The hooks are in `Main.py` (page runs), `API/main_API.py` (middleware and sync lock), `IO_Data.call_or_stop` / `getWellInfoDict` and `MemLogger.checkpoint` (stages).
