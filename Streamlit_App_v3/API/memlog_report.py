"""
Summarise the memory log written by PDU_Func/MemLogger.py.

Usage:
    python API/memlog_report.py                 # reads Logs/memlog.jsonl
    python API/memlog_report.py path/to/memlog.jsonl --top 10

Pure standard library, so it runs anywhere (server, laptop, inside the container).
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

TS = "%Y-%m-%d %H:%M:%S.%f"


def load(path):
    events = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue
    return events


def fmt(v, w=8):
    if isinstance(v, float):
        return f"{v:>{w}.1f}"
    return f"{str(v):>{w}}"


def section(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    top = 10
    if "--top" in sys.argv:
        top = int(sys.argv[sys.argv.index("--top") + 1])
    here = os.path.dirname(os.path.abspath(__file__))
    path = args[0] if args else os.path.join(os.path.dirname(here), "Logs", "memlog.jsonl")
    ev = load(path)
    if not ev:
        print(f"no events found in {path}")
        return
    reqs = [e for e in ev if e.get("ev") == "request"]
    stages = [e for e in ev if e.get("ev") == "stage"]
    hbs = [e for e in ev if e.get("ev") == "heartbeat"]
    gcs = [e for e in ev if e.get("ev") == "gc"]
    starts = [e for e in ev if e.get("ev") == "start"]

    section(f"Overview  ({path})")
    print(f"events: {len(ev)}  requests: {len(reqs)}  stages: {len(stages)}  heartbeats: {len(hbs)}  gc: {len(gcs)}")
    print(f"time span: {ev[0].get('ts')}  ->  {ev[-1].get('ts')}")
    pids = sorted({e.get("pid") for e in ev})
    print(f"process ids seen: {pids}   (more than one = uvicorn restarted / --reload spawned new worker)")
    for s in starts:
        print(f"  start pid={s.get('pid')} rss={s.get('rss_mb')}MB python={s.get('python')} "
              f"MALLOC_ARENA_MAX={s.get('malloc_arena_max')} versions={s.get('versions')}")

    # ------------------------------------------------------------------ per endpoint
    section("Per endpoint (sorted by total RSS growth)")
    agg = defaultdict(lambda: {"n": 0, "err": 0, "dur": [], "delta": [], "peak": [], "overlap": 0})
    for r in reqs:
        k = f"{r.get('method')} {r.get('path')}"
        a = agg[k]
        a["n"] += 1
        st = r.get("status")
        if st == "EXC" or (isinstance(st, int) and st >= 500):
            a["err"] += 1
        a["dur"].append(float(r.get("duration_s") or 0))
        a["delta"].append(float(r.get("rss_delta_mb") or 0))
        a["peak"].append(float(r.get("rss_peak_mb") or 0))
        if r.get("inflight_at_start"):
            a["overlap"] += 1
    print(f"{'endpoint':45s} {'n':>5} {'err':>4} {'dur_avg':>8} {'dur_max':>8} {'d_avg':>8} {'d_max':>8} {'d_sum':>8} {'peak':>8} {'ovlp':>5}")
    for k, a in sorted(agg.items(), key=lambda kv: -sum(kv[1]["delta"])):
        print(f"{k[:45]:45s} {a['n']:>5} {a['err']:>4} {fmt(sum(a['dur'])/a['n'])} {fmt(max(a['dur']))} "
              f"{fmt(sum(a['delta'])/a['n'])} {fmt(max(a['delta']))} {fmt(sum(a['delta']))} {fmt(max(a['peak']))} {a['overlap']:>5}")
    print("d_* = RSS delta (after - before) in MB, peak = highest RSS seen while the request ran, "
          "ovlp = requests that started while another request was still running")

    # ------------------------------------------------------------------ top requests
    def show_top(key, title):
        section(title)
        print(f"{'ts':23s} {'id':>10} {'dur':>7} {'before':>8} {'after':>8} {'delta':>8} {'peak':>8} {'st':>4} {'ifl':>3}  path?query")
        for r in sorted(reqs, key=lambda r: -float(r.get(key) or 0))[:top]:
            print(f"{r.get('ts'):23s} {str(r.get('id')):>10} {fmt(float(r.get('duration_s') or 0), 7)} "
                  f"{fmt(r.get('rss_before_mb'))} {fmt(r.get('rss_after_mb'))} {fmt(r.get('rss_delta_mb'))} "
                  f"{fmt(r.get('rss_peak_mb'))} {str(r.get('status')):>4} {len(r.get('inflight_at_start') or []):>3}  "
                  f"{r.get('path')}?{r.get('query')}")

    show_top("rss_delta_mb", f"Top {top} requests by RSS growth (memory kept after the request finished)")
    show_top("rss_peak_mb", f"Top {top} requests by peak RSS (memory needed while running)")

    # ------------------------------------------------------------------ overlap
    section("Overlapping requests")
    ivals = []
    for r in reqs:
        try:
            t1 = datetime.strptime(r["ts"], TS)
            t0 = t1 - timedelta(seconds=float(r.get("duration_s") or 0))
            ivals.append((t0, t1, r))
        except Exception:
            continue
    ivals.sort(key=lambda x: x[0])
    max_conc, max_at = 0, None
    pts = []
    for t0, t1, r in ivals:
        pts.append((t0, 1)); pts.append((t1, -1))
    pts.sort()
    cur = 0
    for t, d in pts:
        cur += d
        if cur > max_conc:
            max_conc, max_at = cur, t
    print(f"max concurrent requests: {max_conc}  at {max_at}")
    overl = [r for r in reqs if r.get("inflight_at_start")]
    print(f"requests that started while others were running: {len(overl)}")
    for r in overl[:top]:
        print(f"  {r.get('ts')} {r.get('path')}?{r.get('query')}  started while: {r.get('inflight_at_start')}")

    # ------------------------------------------------------------------ stages of the worst requests
    section(f"Stage breakdown for the top {min(top, 5)} requests by RSS growth")
    by_req = defaultdict(list)
    for s in stages:
        by_req[s.get("req")].append(s)
    for r in sorted(reqs, key=lambda r: -float(r.get("rss_delta_mb") or 0))[:min(top, 5)]:
        rid = r.get("id")
        print(f"\n-- {rid} {r.get('path')}?{r.get('query')}  rss {r.get('rss_before_mb')} -> {r.get('rss_after_mb')} MB "
              f"(peak {r.get('rss_peak_mb')}), {r.get('duration_s')}s")
        prev = r.get("rss_before_mb")
        for s in by_req.get(rid, []):
            dfs = " ".join(f"{k}={v['rows']}r/{v['mb']}MB" for k, v in s.items() if isinstance(v, dict) and "rows" in v)
            other = " ".join(f"{k}={v}" for k, v in s.items()
                             if k not in ("ts", "pid", "ev", "req", "stage", "rss_mb", "arrow_mb", "elapsed_s")
                             and not (isinstance(v, dict) and "rows" in v))
            step = ""
            try:
                step = f"({float(s['rss_mb']) - float(prev):+.1f})"
                prev = s["rss_mb"]
            except Exception:
                pass
            print(f"   t+{fmt(s.get('elapsed_s'), 7)}s  rss={fmt(s.get('rss_mb'))}MB {step:>10}  {s.get('stage'):24s} {dfs} {other}")

    # ------------------------------------------------------------------ heartbeat trend
    section("Process trend (heartbeats)")
    if hbs:
        first, last = hbs[0], hbs[-1]
        mx = max(hbs, key=lambda h: float(h.get("rss_mb") or 0))
        print(f"rss first={first.get('rss_mb')}MB  last={last.get('rss_mb')}MB  max={mx.get('rss_mb')}MB at {mx.get('ts')}")
        dfc = [h.get("df_count") for h in hbs if h.get("df_count") is not None]
        if dfc:
            print(f"live DataFrames first={dfc[0]} last={dfc[-1]} max={max(dfc)}   "
                  "(rising while idle = something is holding DataFrames)")
        idle = [h for h in hbs if not h.get("inflight")]
        if len(idle) >= 2:
            print(f"idle rss: first idle={idle[0].get('rss_mb')}MB  last idle={idle[-1].get('rss_mb')}MB   "
                  "(rising = leak or fragmentation; flat = high-water mark only)")
        print(f"threads max={max(int(h.get('threads') or 0) for h in hbs)}")
        step = max(1, len(hbs) // 25)
        print("\n  ts                      rss_MB   arrow_MB  thr  inflight  dfs")
        for h in hbs[::step]:
            print(f"  {h.get('ts')} {fmt(h.get('rss_mb'))} {fmt(h.get('arrow_mb'), 9)} {fmt(h.get('threads'), 4)} "
                  f"{fmt(len(h.get('inflight') or []), 9)} {fmt(h.get('df_count'), 5)}")
    else:
        print("no heartbeats")

    # ------------------------------------------------------------------ gc
    if gcs:
        section("Forced GC / malloc_trim results (GET /memlog/gc)")
        for g in gcs:
            print(f"{g.get('ts')} rss {g.get('rss_before_mb')} -> {g.get('rss_after_gc_mb')} (gc) -> "
                  f"{g.get('rss_after_trim_mb')} (trim)  dfs={g.get('df_count')} ({g.get('df_mb')}MB)")
            for a in g.get("top_python_allocations") or []:
                print(f"     {a['size_mb']:>8.2f} MB  x{a['count']:<7} {a['where']}")
        print("large 'trim' drop = allocator fragmentation, large 'gc' drop = reference cycles, "
              "no drop but many DataFrames = real leak")


if __name__ == "__main__":
    main()
