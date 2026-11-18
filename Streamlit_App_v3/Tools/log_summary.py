#!/usr/bin/env python3
"""Summarise the PDU application logs (Logs/app_*.jsonl, errors_*.jsonl,
memlog.jsonl) into a short text report: restarts, error groups, failed syncs
per well, slow requests and pages. Standard library only, so it runs on the
host or inside either container.

usage: python3 log_summary.py [--hours 168] <log_dir_or_files>...
"""
import argparse
import glob
import json
import os
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))


def parse_ts(s, tz=None):
    try:
        t = datetime.fromisoformat(s)
    except Exception:
        try:
            t = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None
    if t.tzinfo is None:            # memlog: local clock; "tz" gives its offset, older lines assume UTC (containers)
        try:
            t = t.replace(tzinfo=datetime.strptime(tz, "%z").tzinfo) if tz else t.replace(tzinfo=timezone.utc)
        except Exception:
            t = t.replace(tzinfo=timezone.utc)
    return t


def fmt(t):
    return t.astimezone(WIB).strftime("%Y-%m-%d %H:%M:%S") if t else "-"


def files_from(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for pat in ("app_*.jsonl*", "errors_*.jsonl*", "memlog.jsonl*"):
                out += glob.glob(os.path.join(p, pat))
        else:
            out += glob.glob(p)
    return sorted(set(out))


def read(files, since):
    recs, seen, mem = [], set(), []
    for f in files:
        is_mem = os.path.basename(f).startswith("memlog")
        try:
            fh = open(f, encoding="utf-8", errors="replace")
        except Exception:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                t = parse_ts(r.get("ts", ""), r.get("tz"))
                if t is None or t < since:
                    continue
                r["_t"] = t
                if is_mem:
                    if r.get("ev") in ("start", "heartbeat"):
                        mem.append(r)
                    continue
                key = (r.get("ts"), r.get("pid"), r.get("event"), r.get("run_id"), r.get("msg"), r.get("stage"))
                if key in seen:          # errors_*.jsonl repeats lines of app_*.jsonl
                    continue
                seen.add(key)
                recs.append(r)
    recs.sort(key=lambda r: r["_t"])
    mem.sort(key=lambda r: r["_t"])
    return recs, mem


def short(s, n=160):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n] + "..."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--hours", type=float, default=168)
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=a.hours)
    files = files_from(a.paths)
    recs, mem = read(files, since)
    P = print

    P(f"PDU log summary - generated {fmt(now)} WIB, window last {a.hours:g} h (since {fmt(since)} WIB)")
    P(f"files: {', '.join(os.path.basename(f) for f in files) or 'none'}")
    if recs:
        P(f"events: {len(recs)}  from {fmt(recs[0]['_t'])} to {fmt(recs[-1]['_t'])} WIB")
    P("All times WIB (UTC+7). Find everything about one run:  grep '\"run_id\": \"<code>\"' logs/app_*.jsonl")

    # 1. process starts
    P("\n== 1. Process starts (restarts)")
    starts = [r for r in recs if r.get("event") == "process_start"]
    for r in starts[-20:]:
        P(f"  {fmt(r['_t'])}  {r.get('app'):9} pid={r.get('pid')} commit={r.get('git_commit')} host={r.get('host')}")
    mstarts = [r for r in mem if r.get("ev") == "start"]
    for r in mstarts[-10:]:
        P(f"  {fmt(r['_t'])}  memlog    pid={r.get('pid')} (FastAPI memory logger start)")
    if not starts and not mstarts:
        P("  none in window")

    # 2. counts
    P("\n== 2. Events by app and level")
    c = Counter((r.get("app"), r.get("level")) for r in recs)
    for (app, lvl), n in sorted(c.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        P(f"  {str(app):9} {str(lvl):8} {n}")

    # 3. error groups
    P("\n== 3. Errors grouped by fingerprint (same type + same code location)")
    groups = defaultdict(list)
    for r in recs:
        if r.get("level") in ("ERROR", "CRITICAL") and r.get("fingerprint"):
            groups[r["fingerprint"]].append(r)
    if not groups:
        P("  none")
    for fp, rs in sorted(groups.items(), key=lambda x: -len(x[1])):
        r0 = rs[-1]
        wells = sorted({f"wid {r.get('wid')} cid {r.get('cid')} {r.get('well') or ''}".strip() for r in rs if r.get("wid")})
        users = sorted({f"{r.get('user_name')} ({r.get('user_id')})" for r in rs if r.get("user_name")})
        P(f"  [{fp}] x{len(rs)}  {r0.get('app')} {r0.get('event')}  first {fmt(rs[0]['_t'])}  last {fmt(rs[-1]['_t'])}")
        P(f"      {r0.get('error_type')}: {short(r0.get('error'), 200)}")
        P(f"      at {r0.get('where')}   step={r0.get('step') or r0.get('stage') or '-'}  page={r0.get('page') or '-'}  endpoint={r0.get('endpoint') or '-'}")
        if wells:
            P(f"      wells: {', '.join(wells[:10])}")
        if users:
            P(f"      users: {', '.join(users[:10])}")
        P(f"      run_ids: {', '.join(sorted({str(r.get('run_id')) for r in rs})[-5:])}")

    # 4. warnings
    P("\n== 4. Warnings (grouped; prints that look like errors are WARNING)")
    w = Counter()
    wlast = {}
    for r in recs:
        if r.get("level") != "WARNING":
            continue
        key = (r.get("app"), r.get("event"), re.sub(r"\d+", "#", short(r.get("msg") or r.get("error") or r.get("detail") or r.get("stage") or "", 140)))
        w[key] += 1 + int(r.get("repeated") or 0)
        wlast[key] = r
    if not w:
        P("  none")
    for key, n in w.most_common(25):
        r = wlast[key]
        P(f"  x{n:<5} {key[0]} {key[1]}: {key[2]}   (last {fmt(r['_t'])}, wid={r.get('wid')}, run_id={r.get('run_id')})")

    # 5. syncs per well
    P("\n== 5. Syncs per well (FastAPI, scheduler every 15 min)")
    sy = defaultdict(lambda: {"start": 0, "done": 0, "failed": 0, "rejected": 0, "dur": [], "last_ok": None,
                              "last_fail": None, "well": None, "http": Counter()})
    for r in recs:
        ev = r.get("event")
        if not str(ev).startswith("sync_") or r.get("wid") is None:
            continue
        s = sy[r["wid"]]
        s["well"] = s["well"] or r.get("well")
        if ev == "sync_start":
            s["start"] += 1
        elif ev == "sync_done":
            s["done"] += 1
            s["http"][r.get("status")] += 1
            if r.get("duration_ms") is not None:
                s["dur"].append(r["duration_ms"] / 1000)
            if r.get("status") in (200, None):
                s["last_ok"] = r["_t"]
        elif ev == "sync_failed":
            s["failed"] += 1
            s["last_fail"] = r
        elif ev == "sync_rejected":
            s["rejected"] += 1
    if not sy:
        P("  none")
    for wid, s in sorted(sy.items(), key=lambda x: str(x[0])):
        d = s["dur"]
        dtxt = f"median {statistics.median(d):.0f}s max {max(d):.0f}s" if d else "-"
        P(f"  wid {wid} {s['well'] or ''}: start {s['start']} done {s['done']} failed {s['failed']} rejected(409) {s['rejected']}"
          f"  {dtxt}  http {dict(s['http'])}  last ok {fmt(s['last_ok'])}")
        if s["last_fail"]:
            f = s["last_fail"]
            P(f"      last failure {fmt(f['_t'])}: {f.get('error_type')}: {short(f.get('error'), 150)} at {f.get('where')} (run_id {f.get('run_id')})")
        started_not_finished = s["start"] - s["done"] - s["failed"]
        if started_not_finished > 1:
            P(f"      {started_not_finished} syncs started but never finished (hung, or process restarted)")

    # 6. requests
    P("\n== 6. FastAPI requests: 5xx and slow (>= 30 s)")
    req = [r for r in recs if r.get("event") == "request"]
    bad = [r for r in req if (r.get("status") or 0) >= 500 or r.get("slow")]
    by_ep = Counter((r.get("endpoint"), r.get("status")) for r in req)
    P(f"  {len(req)} requests logged; top endpoints: " + ", ".join(f"{ep} {st} x{n}" for (ep, st), n in by_ep.most_common(6)))
    for r in bad[-20:]:
        P(f"  {fmt(r['_t'])} {r.get('method')} {r.get('endpoint')} status={r.get('status')} {r.get('duration_ms', 0)/1000:.1f}s wid={r.get('wid')} run_id={r.get('run_id')}")

    # 7. streamlit pages
    P("\n== 7. Streamlit pages")
    pr = [r for r in recs if r.get("event") == "page_run"]
    pc = Counter((r.get("page"), r.get("well"), r.get("outcome")) for r in pr)
    for (page, well, outc), n in pc.most_common(15):
        P(f"  {page} / {well}: {outc} x{n}")
    slow = sorted((r for r in pr if (r.get("duration_ms") or 0) > 60000), key=lambda r: -r["duration_ms"])[:10]
    for r in slow:
        P(f"  slow {fmt(r['_t'])} {r.get('page')} / {r.get('well')} {r['duration_ms']/1000:.0f}s run_id={r.get('run_id')}")
    steps = Counter(r.get("step") for r in recs if r.get("event") == "step_failed")
    for step, n in steps.most_common(10):
        P(f"  step failed x{n}: {step}")
    if not pr and not steps:
        P("  none")

    # 7b. who used which well
    P("\n== 7b. Users per well (Streamlit page runs)")
    uw = defaultdict(lambda: {"runs": 0, "errors": 0, "pages": Counter(), "last": None})
    for r in recs:
        if r.get("app") != "streamlit" or not r.get("user_name"):
            continue
        k = (r.get("user_name"), r.get("user_id"), r.get("user_company"), r.get("well"), r.get("wid"), r.get("cid"))
        if r.get("event") == "page_run":
            uw[k]["runs"] += 1
            uw[k]["pages"][r.get("page")] += 1
            uw[k]["last"] = r["_t"]
        elif r.get("level") in ("ERROR", "CRITICAL"):
            uw[k]["errors"] += 1
    if not uw:
        P("  none")
    for (name, uid, comp, well, wid, cid), s in sorted(uw.items(), key=lambda x: -x[1]["runs"])[:30]:
        pages = ", ".join(f"{p} x{n}" for p, n in s["pages"].most_common(4))
        P(f"  {name} ({uid}, {comp}) - well {well or '-'} wid {wid} cid {cid}: {s['runs']} runs, {s['errors']} errors,"
          f" last {fmt(s['last'])} [{pages}]")

    # 8. memory
    P("\n== 8. FastAPI memory (memlog heartbeat)")
    hb = [r for r in mem if r.get("ev") == "heartbeat"]
    if hb:
        peak = max(hb, key=lambda r: r.get("rss_mb") or 0)
        last = hb[-1]
        P(f"  last {fmt(last['_t'])}: rss {last.get('rss_mb')} MB, threads {last.get('threads')}, in-flight {len(last.get('inflight') or [])}")
        P(f"  peak {fmt(peak['_t'])}: rss {peak.get('rss_mb')} MB")
        stuck = [i for i in (last.get("inflight") or []) if (i.get("elapsed_s") or 0) > 1800]
        for i in stuck[:10]:
            P(f"  in flight > 30 min: {i.get('path')}?{short(i.get('query'), 60)} {i.get('elapsed_s')}s")
    else:
        P("  no memlog heartbeat in window")


if __name__ == "__main__":
    main()
