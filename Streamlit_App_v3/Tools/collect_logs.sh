#!/usr/bin/env bash
# collect_logs.sh - pack everything needed to troubleshoot the PDU RTDC apps
# into one .tgz you can download and hand over (e.g. to Claude).
#
# Read-only: copies log files, reads `docker logs/inspect/stats`, and makes two
# GET requests to the local FastAPI status endpoints. It changes nothing.
#
# usage (on the server):
#   bash Streamlit_App_v3/Tools/collect_logs.sh            # last 7 days (168 h)
#   bash Streamlit_App_v3/Tools/collect_logs.sh 24         # last 24 h only
#   sudo bash ...                                          # if docker needs root
# env overrides: APP_DIR (Streamlit_App_v3 folder), OUT_DIR (default: current folder)
#
# Output: pdu_logs_<YYYYmmdd_HHMMSS>.tgz with
#   SUMMARY.txt        start here: restarts, error groups, syncs per well, slow pages
#   logs/              app_*.jsonl, errors_*.jsonl, memlog.jsonl (files touched in the window)
#   docker/            docker logs (stdout/stderr with timestamps), state, ps, stats
#   system/            uptime, memory, disk, git commit, FastAPI /sync-status/ and /memlog/status
#   LOGGING.md         field reference

set -uo pipefail
HOURS="${1:-168}"          # default: last 7 days
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${APP_DIR:-$(dirname "$SCRIPT_DIR")}"
LOG_DIR="$APP_DIR/Logs"
OUT_DIR="${OUT_DIR:-$PWD}"
NAME="pdu_logs_$(date +%Y%m%d_%H%M%S)"
W="$OUT_DIR/$NAME"
mkdir -p "$W/logs" "$W/docker" "$W/system" || exit 1
MIN=$(( ${HOURS%.*} * 60 + 60 ))

echo "== app logs ($LOG_DIR, last ${HOURS} h)"
if [ -d "$LOG_DIR" ]; then
  find "$LOG_DIR" -maxdepth 1 -type f \( -name 'app_*.jsonl*' -o -name 'errors_*.jsonl*' -o -name 'memlog.jsonl*' \) \
       -mmin "-$MIN" -exec cp -p {} "$W/logs/" \;
  ls -lh "$W/logs" | tail -n +2
else
  echo "   WARN: $LOG_DIR not found (set APP_DIR=...)" | tee "$W/logs/MISSING.txt"
fi

echo "== docker"
if command -v docker >/dev/null 2>&1; then
  docker ps -a > "$W/docker/ps.txt" 2>&1
  docker stats --no-stream > "$W/docker/stats.txt" 2>&1
  for c in $(docker ps -a --format '{{.Names}}' | grep -Ei 'streamlit|fastapi|pdu'); do
    # capped at the last 300k lines: a week of Streamlit output can be very large
    docker logs --since "${HOURS}h" --timestamps "$c" 2>&1 | tail -n 300000 > "$W/docker/$c.log"
    docker inspect --format \
      'name={{.Name}} status={{.State.Status}} started={{.State.StartedAt}} finished={{.State.FinishedAt}} exit={{.State.ExitCode}} oom_killed={{.State.OOMKilled}} restarts={{.RestartCount}} image={{.Config.Image}} mem_limit={{.HostConfig.Memory}}' \
      "$c" > "$W/docker/$c.state.txt" 2>&1
    echo "   $c: $(cat "$W/docker/$c.state.txt")"
  done
else
  echo "   docker not available" | tee "$W/docker/MISSING.txt"
fi

echo "== system"
{ date; echo; uptime; echo; free -m; echo; df -h "$APP_DIR"; } > "$W/system/host.txt" 2>&1
{ git -C "$APP_DIR" log -3 --format='%h %ad %s' --date=iso 2>&1; echo; git -C "$APP_DIR" status --short 2>&1 | head -50; } > "$W/system/git.txt"
curl -s -m 15 http://localhost:8090/sync-status/   > "$W/system/sync-status.json"  2>&1 || echo "unreachable" > "$W/system/sync-status.json"
curl -s -m 15 http://localhost:8090/memlog/status  > "$W/system/memlog-status.json" 2>&1 || echo "unreachable" > "$W/system/memlog-status.json"

echo "== summary"
cp "$SCRIPT_DIR/LOGGING.md" "$W/" 2>/dev/null
PY="${PYTHON:-}"
for p in python3 python; do
  [ -z "$PY" ] && "$p" -c 'import sys; sys.exit(sys.version_info < (3, 7))' >/dev/null 2>&1 && PY="$p"
done
if [ -n "$PY" ]; then
  "$PY" "$SCRIPT_DIR/log_summary.py" --hours "$HOURS" "$W/logs" > "$W/SUMMARY.txt" 2>&1
else
  # no python on the host: run it inside the FastAPI container (it mounts Streamlit_App_v3 at /streamlit-app)
  c=$(docker ps --format '{{.Names}}' | grep -i fastapi | head -1)
  docker exec "$c" python /streamlit-app/Tools/log_summary.py --hours "$HOURS" /streamlit-app/Logs > "$W/SUMMARY.txt" 2>&1 \
    || echo "summary failed: no python3 on host and no fastapi container" > "$W/SUMMARY.txt"
fi
head -40 "$W/SUMMARY.txt"

tar -C "$OUT_DIR" -czf "$OUT_DIR/$NAME.tgz" "$NAME" && rm -rf "$W"
echo
ls -lh "$OUT_DIR/$NAME.tgz"
echo "Download this file and share it. Start with SUMMARY.txt inside."
