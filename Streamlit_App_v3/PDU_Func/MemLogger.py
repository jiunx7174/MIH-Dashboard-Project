"""
Memory / request logger for the PDU FastAPI service.

Purpose: find out which request (and which stage inside a request) grows the
process memory, and whether requests overlap.

What it writes
--------------
One JSON object per line to  <Streamlit_App_v3>/Logs/memlog.jsonl  (rotating,
5 x 20 MB) and a short human-readable line to stdout (visible in
`docker logs pdu-fastapi`).

Event types ("ev" field):
  request    one per HTTP request: RSS before / after / peak during, duration,
             status, how many other requests were running at the start.
  stage      checkpoints inside heavy code paths (MemLogger.checkpoint(...)).
  heartbeat  every PDU_MEMLOG_HEARTBEAT seconds (default 30): RSS, thread
             count, in-flight requests, number of live DataFrames.
  gc         result of GET /memlog/gc (forced gc + malloc_trim).
  start      once at install time (pid, versions, settings).

Environment variables (all optional)
------------------------------------
  PDU_MEMLOG_DIR          directory for the log file (default: ../Logs)
  PDU_MEMLOG_HEARTBEAT    heartbeat interval in seconds (default 30, 0 = off)
  PDU_MEMLOG_SAMPLE       RSS sampling interval in seconds (default 0.5)
  PDU_MEMLOG_DF_SCAN      1/0 count live DataFrames in each heartbeat (default 1)
  PDU_MEMLOG_TRACEMALLOC  1 to enable tracemalloc (slower, more memory, but
                          /memlog/gc then reports the top allocation sites)

Extra endpoints added to the app
--------------------------------
  GET /memlog/status   current RSS, threads, in-flight requests
  GET /memlog/gc       run gc.collect() + malloc_trim(0), report RSS before/after
                       (tells "real leak" apart from allocator fragmentation)

Usage
-----
  from PDU_Func import MemLogger
  MemLogger.install(app)                      # once, next to app = FastAPI()
  MemLogger.checkpoint("realtime_downloaded", df=RTSensor_DF, wid=429)

checkpoint() is a no-op when install() was never called (e.g. inside the
Streamlit process), so IO_Data / Activity can call it unconditionally.
"""
import contextvars
import gc
import itertools
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

try:
    import psutil
    _PROC = psutil.Process()
except Exception:  # pragma: no cover
    psutil = None
    _PROC = None

_INSTALLED = False
_LOG = logging.getLogger("pdu.memlog")
_LOG.propagate = False
_PID = os.getpid()
_REQ_COUNTER = itertools.count(1)
_LOCK = threading.Lock()
_INFLIGHT = {}            # request_id -> dict(path, query, t0, rss0, peak)
_GLOBAL_PEAK = [0.0]
_CURRENT_REQ = contextvars.ContextVar("pdu_memlog_req", default=None)
_TRACEMALLOC = False
_SETTINGS = {}


# --------------------------------------------------------------------------- #
# low level probes
# --------------------------------------------------------------------------- #
def rss_mb():
    """Resident set size of this process in MB."""
    if _PROC is not None:
        try:
            return round(_PROC.memory_info().rss / 1048576.0, 1)
        except Exception:
            pass
    try:  # Linux fallback
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return round(int(line.split()[1]) / 1024.0, 1)
    except Exception:
        pass
    return -1.0


def _vms_mb():
    if _PROC is not None:
        try:
            return round(_PROC.memory_info().vms / 1048576.0, 1)
        except Exception:
            pass
    return -1.0


def _arrow_mb():
    """Bytes currently held by the pyarrow memory pool (parquet reads)."""
    try:
        import pyarrow as pa
        return round(pa.total_allocated_bytes() / 1048576.0, 1)
    except Exception:
        return -1.0


def _threads():
    return threading.active_count()


def df_info(df):
    """Rows / columns / MB of a pandas DataFrame (shallow, cheap)."""
    try:
        return {
            "rows": int(len(df)),
            "cols": int(df.shape[1]) if hasattr(df, "shape") and len(df.shape) > 1 else 1,
            "mb": round(float(df.memory_usage(index=True, deep=False).sum()) / 1048576.0, 1),
        }
    except Exception:
        return {"rows": -1, "cols": -1, "mb": -1}


def _scan_dataframes():
    """Count live DataFrames and their shallow memory. Costly-ish (walks gc)."""
    t0 = time.time()
    try:
        import pandas as pd
    except Exception:
        return {}
    n = 0
    mb = 0.0
    biggest = 0.0
    for obj in gc.get_objects():
        try:
            if isinstance(obj, pd.DataFrame):
                n += 1
                m = float(obj.memory_usage(index=True, deep=False).sum()) / 1048576.0
                mb += m
                if m > biggest:
                    biggest = m
        except Exception:
            continue
    return {
        "df_count": n,
        "df_mb": round(mb, 1),
        "df_biggest_mb": round(biggest, 1),
        "df_scan_ms": int((time.time() - t0) * 1000),
    }


def malloc_trim():
    """Ask glibc to return free heap pages to the OS. Linux only."""
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        return int(libc.malloc_trim(0))
    except Exception:
        return -1


# --------------------------------------------------------------------------- #
# emitting
# --------------------------------------------------------------------------- #
def _emit(ev, human, **fields):
    rec = {"ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], "pid": _PID, "ev": ev}
    rec.update(fields)
    try:
        _LOG.info(json.dumps(rec, default=str), extra={"human": human})
    except Exception:
        pass


class _HumanFormatter(logging.Formatter):
    def format(self, record):
        human = getattr(record, "human", None)
        return f"[memlog] {human}" if human else record.getMessage()


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()


# --------------------------------------------------------------------------- #
# sampler / heartbeat thread
# --------------------------------------------------------------------------- #
def _sampler(sample_s, heartbeat_s, df_scan):
    last_hb = 0.0
    while True:
        try:
            r = rss_mb()
            with _LOCK:
                if r > _GLOBAL_PEAK[0]:
                    _GLOBAL_PEAK[0] = r
                for info in _INFLIGHT.values():
                    if r > info["peak"]:
                        info["peak"] = r
                inflight = [
                    {"id": k, "path": v["path"], "query": v["query"],
                     "elapsed_s": round(time.time() - v["t0"], 1)}
                    for k, v in _INFLIGHT.items()
                ]
            now = time.time()
            if heartbeat_s and (now - last_hb) >= heartbeat_s:
                last_hb = now
                extra = _scan_dataframes() if df_scan else {}
                _emit(
                    "heartbeat",
                    f"heartbeat rss={r}MB vms={_vms_mb()}MB arrow={_arrow_mb()}MB "
                    f"threads={_threads()} inflight={len(inflight)} "
                    f"dfs={extra.get('df_count', '-')} ({extra.get('df_mb', '-')}MB) "
                    f"peak_since_start={_GLOBAL_PEAK[0]}MB",
                    rss_mb=r, vms_mb=_vms_mb(), arrow_mb=_arrow_mb(),
                    threads=_threads(), gc_counts=gc.get_count(),
                    inflight=inflight, peak_rss_mb=_GLOBAL_PEAK[0], **extra,
                )
        except Exception:
            pass
        time.sleep(sample_s)


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def checkpoint(stage, **fields):
    """Log a stage inside the current request. DataFrame kwargs are summarised.

    Example: checkpoint("realtime_downloaded", df=RTSensor_DF, wid=429)
    """
    if not _INSTALLED:
        return
    try:
        req = _CURRENT_REQ.get()
        out = {}
        for k, v in fields.items():
            if hasattr(v, "memory_usage") and hasattr(v, "shape"):
                out[k] = df_info(v)
            else:
                out[k] = v
        r = rss_mb()
        elapsed = None
        path = "-"
        if req is not None:
            with _LOCK:
                info = _INFLIGHT.get(req)
            if info:
                elapsed = round(time.time() - info["t0"], 1)
                path = info["path"]
        dfs = " ".join(
            f"{k}={v['rows']}rows/{v['mb']}MB" for k, v in out.items() if isinstance(v, dict) and "rows" in v
        )
        others = " ".join(f"{k}={v}" for k, v in out.items() if not (isinstance(v, dict) and "rows" in v))
        _emit(
            "stage",
            f"stage req={req} {path} '{stage}' rss={r}MB arrow={_arrow_mb()}MB t+{elapsed}s {dfs} {others}".strip(),
            req=req, stage=stage, rss_mb=r, arrow_mb=_arrow_mb(), elapsed_s=elapsed, **out,
        )
    except Exception:
        pass


def install(app, log_dir=None):
    """Attach middleware, diagnostic endpoints and the sampler thread to `app`."""
    global _INSTALLED, _TRACEMALLOC
    if _INSTALLED or getattr(app.state, "memlog_installed", False):
        return
    _INSTALLED = True
    app.state.memlog_installed = True

    # ---- settings
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = log_dir or os.environ.get("PDU_MEMLOG_DIR") or os.path.join(base_dir, "Logs")
    heartbeat_s = float(os.environ.get("PDU_MEMLOG_HEARTBEAT", "30"))
    sample_s = float(os.environ.get("PDU_MEMLOG_SAMPLE", "0.5"))
    df_scan = os.environ.get("PDU_MEMLOG_DF_SCAN", "1") == "1"
    _TRACEMALLOC = os.environ.get("PDU_MEMLOG_TRACEMALLOC", "0") == "1"
    _SETTINGS.update(log_dir=log_dir, heartbeat_s=heartbeat_s, sample_s=sample_s,
                     df_scan=df_scan, tracemalloc=_TRACEMALLOC)

    # ---- logging handlers
    os.makedirs(log_dir, exist_ok=True)
    _LOG.setLevel(logging.INFO)
    if not _LOG.handlers:
        fh = RotatingFileHandler(os.path.join(log_dir, "memlog.jsonl"),
                                 maxBytes=20 * 1024 * 1024, backupCount=5, encoding="utf-8")
        fh.setFormatter(_JsonFormatter())
        _LOG.addHandler(fh)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(_HumanFormatter())
        _LOG.addHandler(sh)

    if _TRACEMALLOC:
        import tracemalloc
        tracemalloc.start(10)

    # ---- middleware
    @app.middleware("http")
    async def _memlog_middleware(request, call_next):
        rid = f"{_PID}-{next(_REQ_COUNTER)}"
        path = request.url.path
        query = str(request.url.query)
        if path.startswith("/memlog/"):
            return await call_next(request)
        t0 = time.time()
        r0 = rss_mb()
        with _LOCK:
            inflight_at_start = [
                f"{k}:{v['path']}" for k, v in _INFLIGHT.items()
            ]
            _INFLIGHT[rid] = {"path": path, "query": query, "t0": t0, "rss0": r0, "peak": r0}
        token = _CURRENT_REQ.set(rid)
        if _TRACEMALLOC:
            import tracemalloc
            tracemalloc.reset_peak()
        status = "EXC"
        body_bytes = None
        try:
            response = await call_next(request)
            status = response.status_code
            body_bytes = response.headers.get("content-length")
            return response
        finally:
            r1 = rss_mb()
            with _LOCK:
                info = _INFLIGHT.pop(rid, None)
            peak = max(info["peak"], r0, r1) if info else max(r0, r1)
            _CURRENT_REQ.reset(token)
            dur = round(time.time() - t0, 1)
            extra = {}
            if _TRACEMALLOC:
                import tracemalloc
                cur, pk = tracemalloc.get_traced_memory()
                extra = {"py_traced_mb": round(cur / 1048576.0, 1),
                         "py_traced_peak_mb": round(pk / 1048576.0, 1)}
            _emit(
                "request",
                f"request id={rid} {request.method} {path}?{query} status={status} dur={dur}s "
                f"rss {r0}->{r1}MB (delta {round(r1 - r0, 1):+}, peak {peak}) "
                f"inflight_at_start={len(inflight_at_start)} threads={_threads()}",
                id=rid, method=request.method, path=path, query=query, status=status,
                duration_s=dur, rss_before_mb=r0, rss_after_mb=r1,
                rss_delta_mb=round(r1 - r0, 1), rss_peak_mb=peak,
                arrow_mb=_arrow_mb(), threads=_threads(),
                inflight_at_start=inflight_at_start, response_bytes=body_bytes, **extra,
            )

    # ---- diagnostic endpoints
    @app.get("/memlog/status")
    def _memlog_status():
        with _LOCK:
            inflight = [
                {"id": k, "path": v["path"], "query": v["query"],
                 "elapsed_s": round(time.time() - v["t0"], 1),
                 "rss_at_start_mb": v["rss0"], "peak_mb": v["peak"]}
                for k, v in _INFLIGHT.items()
            ]
        return {
            "pid": _PID, "rss_mb": rss_mb(), "vms_mb": _vms_mb(), "arrow_mb": _arrow_mb(),
            "threads": _threads(), "peak_rss_since_start_mb": _GLOBAL_PEAK[0],
            "inflight": inflight, "settings": _SETTINGS,
            "log_file": os.path.join(log_dir, "memlog.jsonl"),
        }

    @app.get("/memlog/gc")
    def _memlog_gc(top: int = 15):
        r0 = rss_mb()
        a0 = _arrow_mb()
        collected = gc.collect()
        r1 = rss_mb()
        try:
            import pyarrow as pa
            pa.default_memory_pool().release_unused()
        except Exception:
            pass
        trim = malloc_trim()
        r2 = rss_mb()
        out = {
            "pid": _PID, "rss_before_mb": r0, "rss_after_gc_mb": r1, "rss_after_trim_mb": r2,
            "freed_by_gc_mb": round(r0 - r1, 1), "freed_by_trim_mb": round(r1 - r2, 1),
            "gc_collected_objects": collected, "malloc_trim_result": trim,
            "arrow_before_mb": a0, "arrow_after_mb": _arrow_mb(),
        }
        out.update(_scan_dataframes())
        if _TRACEMALLOC:
            import tracemalloc
            snap = tracemalloc.take_snapshot()
            stats = snap.statistics("lineno")[:top]
            out["top_python_allocations"] = [
                {"where": str(s.traceback[0]), "size_mb": round(s.size / 1048576.0, 2), "count": s.count}
                for s in stats
            ]
        _emit("gc", f"gc rss {r0}->{r1}->{r2}MB (gc freed {round(r0 - r1, 1)}, trim freed {round(r1 - r2, 1)}) "
                    f"dfs={out.get('df_count')}", **out)
        return out

    # ---- sampler thread
    t = threading.Thread(target=_sampler, args=(sample_s, heartbeat_s, df_scan),
                         name="pdu-memlog-sampler", daemon=True)
    t.start()

    versions = {}
    for mod in ("pandas", "numpy", "pyarrow", "fastapi", "starlette", "uvicorn", "streamlit"):
        try:
            versions[mod] = __import__(mod).__version__
        except Exception:
            versions[mod] = None
    _emit("start", f"start pid={_PID} rss={rss_mb()}MB log={os.path.join(log_dir, 'memlog.jsonl')} "
                   f"settings={_SETTINGS}",
          rss_mb=rss_mb(), python=sys.version.split()[0], versions=versions, settings=_SETTINGS,
          malloc_arena_max=os.environ.get("MALLOC_ARENA_MAX"))
