"""
Structured application log for the PDU RTDC Streamlit app and FastAPI service.

Goal: when something breaks on the server, one archive (Tools/collect_logs.sh)
holds everything needed to see what happened, for which well, user page or
sync, without guessing. Format and fields: Tools/LOGGING.md.

Files (in PDU_LOG_DIR, default <Streamlit_App_v3>/Logs; one set per process
type so two containers never write the same rotating file):
  app_<app>.jsonl     every event, INFO and up        (daily files, 14 days)
  errors_<app>.jsonl  WARNING and up only, read first (daily files, 30 days)
  <app> is "streamlit" or "fastapi". Rotated files get a .YYYY-MM-DD suffix.

Each line is one JSON object:
  {"ts": "2026-11-18T10:05:17.599+07:00", "level": "ERROR", "app": "fastapi",
   "event": "sync_failed", "run_id": "a1b2c3d4", "wid": 506, "well": "AKP-004",
   "endpoint": "/update-activity-summary-data/", "duration_ms": 8123,
   "error_type": "KeyError", "error": "'StartDateTime'", "where": "PDU_Func/IO_Data.py:1386 in getLastConnectionDateTime",
   "fingerprint": "3f2a9c1e", "traceback": "..."}

Context fields (run_id, wid, well, page, endpoint, user, ...) are set once with
bind() and then added to every event of that request / page run / sync,
including print() lines, which are captured as event "print".

Usage
  from PDU_Func import AppLog
  AppLog.setup("fastapi")                       # once per process
  AppLog.bind(run_id=AppLog.new_id(), wid=506)  # per request / page run
  AppLog.event("sync_start", window="...")
  code = AppLog.exception("page_error", e)      # returns the error code to show
  AppLog.stage("realtime_downloaded", df=RTSensor_DF)   # DataFrames -> rows/cols

Everything is a no-op until setup() is called, so library code (IO_Data,
Activity, notebooks, offline scripts) can call it unconditionally.

Environment variables (optional)
  PDU_LOG_DIR            log directory
  PDU_LOG_TZ_HOURS       UTC offset for "ts" (default 7 = WIB; containers run in UTC)
  PDU_LOG_CAPTURE_PRINT  1/0 capture print() lines as events (default 1)
  PDU_LOG_DEDUPE_S       repeat window for identical warnings (default 600 s)
"""
import contextvars
import hashlib
import json
import logging
import os
import re
import socket
import sys
import threading
import time
import traceback
import uuid
from datetime import date, datetime, timedelta, timezone
from logging.handlers import TimedRotatingFileHandler

_APP_DAYS = int(os.environ.get("PDU_LOG_KEEP_DAYS", "14"))         # app_*.jsonl
_ERR_DAYS = int(os.environ.get("PDU_LOG_KEEP_ERROR_DAYS", "30"))   # errors_*.jsonl
_APP = None
_LOG = logging.getLogger("pdu.app")
_LOG.propagate = False
_PID = os.getpid()
_TZ = timezone(timedelta(hours=float(os.environ.get("PDU_LOG_TZ_HOURS", "7"))))
_CTX = contextvars.ContextVar("pdu_applog_ctx", default={})
_DEDUPE_S = float(os.environ.get("PDU_LOG_DEDUPE_S", "600"))
_DEDUPE = {}                      # key -> [last_emit_epoch, suppressed_count]
_DEDUPE_LOCK = threading.Lock()
_IN_EMIT = threading.local()      # guards print-capture recursion
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Streamlit_App_v3
_SETTINGS = {}

_LEVELS = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
           "error": logging.ERROR, "critical": logging.CRITICAL}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def new_id():
    """Short id for a request / page run / sync. Shown to users as the error code."""
    return uuid.uuid4().hex[:8]


def hash_id(value):
    """Stable short hash for user identifiers (login tokens and emails are never logged)."""
    if value in (None, ""):
        return None
    return hashlib.sha1(str(value).encode("utf-8")).hexdigest()[:10]


def _now():
    return datetime.now(_TZ).isoformat(timespec="milliseconds")


def _jsonable(v):
    if hasattr(v, "shape") and hasattr(v, "columns"):          # DataFrame
        try:
            return {"rows": int(v.shape[0]), "cols": int(v.shape[1])}
        except Exception:
            return "<DataFrame>"
    if hasattr(v, "shape") and hasattr(v, "dtype"):              # Series / ndarray
        try:
            return {"rows": int(v.shape[0])}
        except Exception:
            return "<array>"
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)) and len(v) <= 50:
        return [_jsonable(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    s = str(v)
    return s if len(s) <= 500 else s[:500] + "..."


def _where(tb_list):
    """Deepest frame that belongs to this project (not site-packages)."""
    for fr in reversed(tb_list):
        fn = fr.filename.replace("\\", "/")
        if "site-packages" in fn or "/lib/python" in fn or "\\lib\\" in fr.filename:
            continue
        rel = fn.split("Streamlit_App_v3/")[-1] if "Streamlit_App_v3/" in fn else os.path.basename(fn)
        return f"{rel}:{fr.lineno} in {fr.name}"
    if tb_list:
        fr = tb_list[-1]
        return f"{os.path.basename(fr.filename)}:{fr.lineno} in {fr.name}"
    return None


def _git_commit():
    """Commit of the deployed code, if a .git folder is reachable (Streamlit
    container mounts the project root; FastAPI only Streamlit_App_v3)."""
    if os.environ.get("PDU_GIT_COMMIT"):
        return os.environ["PDU_GIT_COMMIT"]
    d = _BASE_DIR
    for _ in range(3):
        head = os.path.join(d, ".git", "HEAD")
        if os.path.isfile(head):
            try:
                ref = open(head).read().strip()
                if ref.startswith("ref:"):
                    p = os.path.join(d, ".git", ref.split(" ", 1)[1])
                    if os.path.isfile(p):
                        return open(p).read().strip()[:10]
                    packed = os.path.join(d, ".git", "packed-refs")
                    if os.path.isfile(packed):
                        for line in open(packed):
                            if line.strip().endswith(ref.split(" ", 1)[1]):
                                return line.split()[0][:10]
                return ref[:10]
            except Exception:
                return None
        d = os.path.dirname(d)
    return None


# --------------------------------------------------------------------------- #
# context
# --------------------------------------------------------------------------- #
def bind(**fields):
    """Add fields to the context of the current request / page run / thread.
    Returns a token for unbind(). None values remove the field."""
    ctx = dict(_CTX.get())
    for k, v in fields.items():
        if v is None:
            ctx.pop(k, None)
        else:
            ctx[k] = _jsonable(v)
    return _CTX.set(ctx)


def unbind(token):
    try:
        _CTX.reset(token)
    except Exception:
        pass


def reset_context(**fields):
    """Start a fresh context (e.g. at the top of every Streamlit script run)."""
    _CTX.set({})
    return bind(**fields)


def get_context():
    return dict(_CTX.get())


# --------------------------------------------------------------------------- #
# emitting
# --------------------------------------------------------------------------- #
class _JsonFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()


class _ConsoleFormatter(logging.Formatter):
    def format(self, record):
        return getattr(record, "human", record.getMessage())


def _emit(level, name, fields):
    if _APP is None:
        return None
    rec = {"ts": _now(), "level": logging.getLevelName(level), "app": _APP, "pid": _PID, "event": name}
    rec.update(_CTX.get())
    for k, v in fields.items():
        if v is not None:
            rec[k] = _jsonable(v)
    ctx_txt = " ".join(f"{k}={rec[k]}" for k in ("run_id", "wid", "well", "page", "endpoint") if k in rec)
    msg = rec.get("error") or rec.get("msg") or ""
    human = f"[applog] {rec['level']} {name} {ctx_txt} {rec.get('error_type', '')} {str(msg)[:300]}".rstrip()
    _IN_EMIT.on = True
    try:
        _LOG.log(level, json.dumps(rec, default=str, ensure_ascii=False), extra={"human": human})
    except Exception:
        pass
    finally:
        _IN_EMIT.on = False
    return rec


def _dedupe(key):
    """(skip, repeated). Within the dedupe window an identical key is only
    counted; the 10th, 100th, 1000th... repeat is still logged (repeated=n), so
    a burst shows up with its size instead of as a single line."""
    now = time.time()
    with _DEDUPE_LOCK:
        st = _DEDUPE.get(key)
        if st and now - st[0] < _DEDUPE_S:
            st[1] += 1
            if st[1] in (9, 99, 999, 9999, 99999):
                n, st[1] = st[1], 0
                return False, n
            return True, 0
        suppressed = st[1] if st else 0
        _DEDUPE[key] = [now, 0]
        return False, suppressed


def event(name, level="info", dedupe_key=None, **fields):
    """Log one event. dedupe_key: identical keys are logged at most once per
    PDU_LOG_DEDUPE_S seconds; the next one carries repeated=<n suppressed>."""
    if _APP is None:
        return None
    if dedupe_key is not None:
        skip, suppressed = _dedupe(dedupe_key)
        if skip:
            return None
        if suppressed:
            fields["repeated"] = suppressed
    return _emit(_LEVELS.get(level, logging.INFO), name, fields)


def stage(stage_name, **fields):
    """A step inside a sync / recalculation (forwarded from MemLogger.checkpoint)."""
    return event("stage", stage=stage_name, **fields)


def exception(name, exc=None, level="error", **fields):
    """Log an exception with traceback, where it happened and a fingerprint that
    groups identical errors. Returns the error code (run_id) to show the user."""
    if exc is None:
        exc = sys.exc_info()[1]
    code = _CTX.get().get("run_id") or new_id()
    if _APP is None:
        return code
    if exc is not None and getattr(exc, "_applog_logged", False):
        return code             # already logged deeper in the stack (same traceback)
    try:
        exc._applog_logged = True
    except Exception:
        pass
    tb_list = traceback.extract_tb(exc.__traceback__) if exc is not None else []
    where = _where(tb_list)
    etype = type(exc).__name__ if exc is not None else None
    tb_txt = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)) if exc is not None else None
    if tb_txt and len(tb_txt) > 12000:
        tb_txt = tb_txt[:3000] + "\n...\n" + tb_txt[-9000:]
    fp = hashlib.sha1(f"{etype}|{where}".encode()).hexdigest()[:8]
    if "run_id" not in _CTX.get():
        fields["run_id"] = code
    _emit(_LEVELS.get(level, logging.ERROR), name, dict(
        fields, error_type=etype, error=str(exc)[:2000] if exc is not None else None,
        where=where, fingerprint=fp, traceback=tb_txt))
    return code


# --------------------------------------------------------------------------- #
# print() capture
# --------------------------------------------------------------------------- #
_WARN_RE = re.compile(r"\w*Error\b|\b(error|exception|traceback|failed|failure|gagal|timed? ?out|timeout|"
                      r"refused|invalid|corrupt(ed)?|not found)\b", re.I)
_SKIP_PREFIX = ("[memlog]", "[applog]")


class _StdoutTee:
    """Writes to the real stdout (docker logs) and logs each complete line as an
    event "print" with the current context. Lines that look like errors are
    WARNING, so they also land in errors_<app>.jsonl."""

    def __init__(self, stream):
        self._stream = stream
        self._buf = threading.local()

    def write(self, s):
        n = self._stream.write(s)
        if getattr(_IN_EMIT, "on", False) or _APP is None:
            return n
        try:
            buf = getattr(self._buf, "v", "") + s
            if "\n" in buf:
                *lines, rest = buf.split("\n")
                self._buf.v = rest
                for line in lines:
                    line = line.rstrip()
                    if not line.strip() or line.startswith(_SKIP_PREFIX):
                        continue
                    if _WARN_RE.search(line):
                        key = re.sub(r"\d+", "#", line)[:200]
                        event("print", level="warning", dedupe_key=("print", key), msg=line[:2000])
                    else:
                        event("print", msg=line[:2000])
            else:
                self._buf.v = buf if len(buf) < 20000 else ""
        except Exception:
            pass
        return n

    def flush(self):
        return self._stream.flush()

    def __getattr__(self, name):
        return getattr(self._stream, name)


# --------------------------------------------------------------------------- #
# setup
# --------------------------------------------------------------------------- #
def setup(app_name, log_dir=None):
    """Create the log files and hooks for this process. Safe to call repeatedly
    (Streamlit re-executes Main.py on every rerun)."""
    global _APP
    if _APP is not None:
        return
    log_dir = log_dir or os.environ.get("PDU_LOG_DIR") or os.path.join(_BASE_DIR, "Logs")
    capture = os.environ.get("PDU_LOG_CAPTURE_PRINT", "1") == "1"
    try:
        os.makedirs(log_dir, exist_ok=True)
        _LOG.setLevel(logging.INFO)
        if not _LOG.handlers:
            # one file per day (container clock, UTC midnight = 07:00 WIB):
            # app_<app>.jsonl.YYYY-MM-DD, kept _APP_DAYS / _ERR_DAYS days
            fh = TimedRotatingFileHandler(os.path.join(log_dir, f"app_{app_name}.jsonl"), when="midnight",
                                          backupCount=_APP_DAYS, encoding="utf-8")
            fh.setLevel(logging.INFO)
            fh.setFormatter(_JsonFormatter())
            _LOG.addHandler(fh)
            eh = TimedRotatingFileHandler(os.path.join(log_dir, f"errors_{app_name}.jsonl"), when="midnight",
                                          backupCount=_ERR_DAYS, encoding="utf-8")
            eh.setLevel(logging.WARNING)
            eh.setFormatter(_JsonFormatter())
            _LOG.addHandler(eh)
            # short line in `docker logs` for warnings and errors only
            ch = logging.StreamHandler(sys.__stdout__ or sys.stdout)
            ch.setLevel(logging.WARNING)
            ch.setFormatter(_ConsoleFormatter())
            _LOG.addHandler(ch)
    except Exception as e:  # never break the app because of logging
        print(f"[applog] setup failed, logging disabled: {e}")
        return
    _APP = app_name
    _SETTINGS.update(log_dir=log_dir, capture_print=capture, tz_hours=_TZ.utcoffset(None).total_seconds() / 3600,
                     dedupe_s=_DEDUPE_S)

    if capture and not isinstance(sys.stdout, _StdoutTee):
        sys.stdout = _StdoutTee(sys.stdout)

    def _excepthook(etype, value, tb):
        try:
            exception("uncaught_exception", value, level="critical")
        finally:
            sys.__excepthook__(etype, value, tb)
    sys.excepthook = _excepthook

    def _thread_hook(args):
        if args.exc_type is SystemExit:
            return
        try:
            exception("thread_exception", args.exc_value, thread=getattr(args.thread, "name", None))
        except Exception:
            pass
    threading.excepthook = _thread_hook

    versions = {}
    for mod in ("pandas", "numpy", "pyarrow", "requests", "fastapi", "uvicorn", "streamlit"):
        try:
            versions[mod] = __import__(mod).__version__
        except Exception:
            pass
    event("process_start", host=socket.gethostname(), python=sys.version.split()[0],
          git_commit=_git_commit(), versions=versions, settings=_SETTINGS, cwd=os.getcwd())
