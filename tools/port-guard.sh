#!/usr/bin/env bash
set -euo pipefail

# Port Guard (Windows / Git Bash) — Python-only, no PowerShell, no WMIC
# Usage:
#   ./port-guard.sh             # baseline if none; then show NEW python listeners & confirm per-PID kills
#   ./port-guard.sh diff        # list NEW python listeners (no kill)
#   ./port-guard.sh kill-new    # recompute NEW & confirm per-PID kills (python only)
#   ./port-guard.sh rebaseline  # set current listeners as baseline (backs up old one)
#   ./port-guard.sh baseline    # alias for rebaseline
#   ./port-guard.sh kill-port 8000   # kill python listeners bound to port 8000 (bypass baseline)
#   ./port-guard.sh reset       # delete baseline & diff
#
# Env:
#   COMPARE_KEY=addr            # compare by proto|address (ignores PID churn)
#   COMPARE_KEY=full            # compare by proto|address|PID (default)
#   HARD_KILL=1                 # auto force kill (/F /T) if normal kill fails
#   ASK_REBASELINE=0            # don't prompt to rebaseline after kill-new (default 1)
#   VERBOSE=1                   # extra debug logs

BASE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/port-guard"
mkdir -p "$BASE_DIR"
BASELINE="$BASE_DIR/baseline.txt"
NEW_FILE="$BASE_DIR/new_since_baseline.txt"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SNAPSHOT="$BASE_DIR/snapshot-$TIMESTAMP.txt"

COMPARE_KEY="${COMPARE_KEY:-full}"
HARD_KILL="${HARD_KILL:-0}"
ASK_REBASELINE="${ASK_REBASELINE:-1}"
VERBOSE="${VERBOSE:-0}"

logv(){ [ "$VERBOSE" = "1" ] && echo "[DEBUG] $*" >&2 || true; }

on_windows(){ case "$(uname -s | tr '[:upper:]' '[:lower:]')" in msys*|mingw*|cygwin*) return 0;; *) return 1;; esac; }

require_windows_tools(){
  if ! on_windows; then echo "This script targets Git Bash on Windows." >&2; exit 1; fi
  for bin in netstat.exe taskkill.exe tasklist.exe; do
    command -v "$bin" >/dev/null 2>&1 || { echo "Error: $bin not found." >&2; exit 1; }
  done
  command -v comm >/dev/null 2>&1 || logv "coreutils 'comm' not found; using grep fallback"
}

has_comm(){ command -v comm >/dev/null 2>&1; }

# set difference: lines in $2 not in $1 -> NEW
setdiff(){
  local a="$1" b="$2"
  if has_comm; then
    comm -13 <(sort "$a") <(sort "$b")
  else
    grep -Fvx -f <(sort "$a") "$b" || true
  fi
}

# Snapshot Windows listeners -> normalized lines:
#   full: proto|local_address|pid
#   addr: proto|local_address
snapshot(){
  # TCP LISTENING
  netstat.exe -ano -p tcp 2>/dev/null \
  | tr -d '\r' \
  | awk -v cmp="$COMPARE_KEY" '
      BEGIN { IGNORECASE=1 }
      $1 ~ /^TCP$/ && toupper($4)=="LISTENING" {
        proto=tolower($1); addr=$2; pid=$5
        if (cmp=="addr") print proto "|" addr;
        else             print proto "|" addr "|" pid;
      }
    '
  # UDP (include all)
  netstat.exe -ano -p udp 2>/dev/null \
  | tr -d '\r' \
  | awk -v cmp="$COMPARE_KEY" '
      BEGIN { IGNORECASE=1 }
      $1 ~ /^UDP$/ {
        proto=tolower($1); addr=$2; pid=(NF>=4 ? $4 : "");
        if (cmp=="addr") print proto "|" addr;
        else             print proto "|" addr "|" pid;
      }
    ' \
  | sort -u
}

save_baseline(){
  snapshot | sort -u > "$BASELINE"
  cp "$BASELINE" "$SNAPSHOT"
  echo "✅ Baseline saved: $BASELINE"
}

rebaseline(){
  [ -f "$BASELINE" ] && cp "$BASELINE" "$BASE_DIR/baseline.$(date +%Y%m%d-%H%M%S).bak"
  snapshot | sort -u > "$BASELINE"
  cp "$BASELINE" "$SNAPSHOT"
  echo "🔁 Rebaselined (old baseline backed up if existed)."
}

diff_new(){
  local cur_file; cur_file="$(mktemp)"
  snapshot | sort -u > "$cur_file"
  cp "$cur_file" "$SNAPSHOT"

  if [ ! -f "$BASELINE" ]; then
    echo "No baseline exists. Creating one now…"
    mv "$cur_file" "$BASELINE"
    echo "✅ Baseline recorded at $BASELINE"
    return 0
  fi

  echo "📋 Current listening (normalized):"; cat "$cur_file"; echo
  echo "🔎 NEW listeners since baseline:"
  setdiff "$BASELINE" "$cur_file" | tee "$NEW_FILE"
  rm -f "$cur_file"
}

# ---------- Python-only helpers (no PS/WMIC) ----------
is_python_pid(){
  local pid="$1"
  tasklist.exe /FI "PID eq $pid" 2>/dev/null \
    | tr -d '\r' \
    | awk 'NR>3 && $2 ~ /^[0-9]+$/ {print tolower($1)}' \
    | grep -Eiq '^python(w)?\.exe$'
}

pid_alive(){
  local pid="$1"
  tasklist.exe /FI "PID eq $pid" 2>/dev/null \
    | tr -d '\r' | awk 'NR>3 {print}' | grep -q "[[:space:]]$pid[[:space:]]"
}

proc_name(){
  local pid="$1"
  tasklist.exe /FI "PID eq $pid" 2>/dev/null \
    | tr -d '\r' \
    | awk 'NR>3 && $2 ~ /^[0-9]+$/ {print $1; exit}'
}

extract_port(){ echo "${1##*:}"; }  # works with IPv6 like [::]:8000

print_one_header(){
  local pid="$1" proto="$2" addr="$3"
  local port; port="$(extract_port "$addr")"
  local name; name="$(proc_name "$pid" || true)"
  echo "────────────────────────────────────────────────────────"
  echo "PID  : $pid"
  echo "Proto: $proto"
  echo "Addr : $addr"
  echo "Port : $port"
  [ -n "$name" ] && echo "Image: $name"
}

kill_cascade(){
  local pid="$1"
  logv "taskkill /PID $pid /T"
  taskkill.exe /PID "$pid" /T >/dev/null 2>&1 || true
  sleep 1
  if pid_alive "$pid"; then
    if [ "$HARD_KILL" = "1" ]; then
      logv "taskkill /F /PID $pid /T"
      taskkill.exe /F /PID "$pid" /T >/dev/null 2>&1 || true
      sleep 1
    else
      read -r -p "Still running. Force kill (taskkill /F /T)? [y/N] " ans2
      [[ "$ans2" =~ ^[Yy]$ ]] && taskkill.exe /F /PID "$pid" /T >/dev/null 2>&1 || true
      sleep 1
    fi
  fi
}

kill_one(){
  local pid="$1" proto="$2" addr="$3"
  print_one_header "$pid" "$proto" "$addr"

  if ! is_python_pid "$pid"; then
    echo "⏭️  Skipping (not a Python process)."
    return 0
  fi
  read -r -p "Kill this NEW Python listener? [y/N] " ans
  if [[ ! "$ans" =~ ^[Yy]$ ]]; then
    echo "↩️  Skipped PID $pid"
    return 0
  fi

  kill_cascade "$pid"
  if pid_alive "$pid"; then
    echo "❌ PID $pid still running. Try Git Bash as **Administrator**."
  else
    echo "✅ PID $pid terminated."
  fi
}

kill_new(){
  if [ ! -f "$NEW_FILE" ]; then
    echo "No diff results yet. Computing…"; diff_new >/dev/null
  fi

  local cur_file; cur_file="$(mktemp)"
  snapshot | sort -u > "$cur_file"

  # Iterate NEW lines, preserving proto/addr/port, and confirm per-PID
  # full: proto|addr|pid ; addr: proto|addr -> map to current proto|addr|pid
  declare -A seen=()
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    if [ "$COMPARE_KEY" = "addr" ]; then
      while IFS= read -r cur; do
        [ -z "$cur" ] && continue
        proto="${cur%%|*}"; rest="${cur#*|}"; addr="${rest%%|*}"; pid="${cur##*|}"
        [[ "$pid" =~ ^[0-9]+$ ]] || continue
        key="$pid|$proto|$addr"
        if [ -z "${seen[$key]+x}" ]; then seen[$key]=1; kill_one "$pid" "$proto" "$addr"; fi
      done < <(grep -F "^${line}|" "$cur_file" || true)
    else
      proto="${line%%|*}"; rest="${line#*|}"; addr="${rest%%|*}"; pid="${line##*|}"
      [[ "$pid" =~ ^[0-9]+$ ]] || continue
      key="$pid|$proto|$addr"
      if [ -z "${seen[$key]+x}" ]; then seen[$key]=1; kill_one "$pid" "$proto" "$addr"; fi
    fi
  done < "$NEW_FILE"
  rm -f "$cur_file"

  if [ "$ASK_REBASELINE" = "1" ]; then
    echo; read -r -p "Rebaseline now (treat current state as normal)? [y/N] " rb
    [[ "$rb" =~ ^[Yy]$ ]] && rebaseline
  fi
}

kill_port(){
  local port="${1:-}"
  if ! [[ "$port" =~ ^[0-9]+$ ]]; then echo "Usage: $0 kill-port <port>"; exit 2; fi

  # Current TCP listeners on this port -> proto|addr|pid
  tmp="$(mktemp)"
  netstat.exe -ano -p tcp 2>/dev/null \
  | tr -d '\r' \
  | awk -v p="$port" '
      BEGIN { IGNORECASE=1 }
      $1 ~ /^TCP$/ && toupper($4)=="LISTENING" {
        # $2 = local address like 0.0.0.0:8000 or [::]:8000
        la=$2; pid=$5; proto="tcp"
        # extract port after last colon
        n=split(la, a, ":"); lp=a[n]
        if (lp == p) printf "%s|%s|%s\n", proto, la, pid
      }
    ' | sort -u > "$tmp"

  if [ ! -s "$tmp" ]; then
    echo "No TCP listeners found on port $port."
    rm -f "$tmp"; return 0
  fi

  echo "🔎 Python listeners on port $port:"
  while IFS='|' read -r proto addr pid; do
    [[ "$pid" =~ ^[0-9]+$ ]] || continue
    if is_python_pid "$pid"; then
      kill_one "$pid" "$proto" "$addr"
    else
      echo "⏭️  PID $pid on $addr is not Python; skipping."
    fi
  done < "$tmp"
  rm -f "$tmp"
}

main(){
  require_windows_tools
  case "${1:-}" in
    diff)        diff_new ;;
    kill-new)    kill_new ;;
    rebaseline)  rebaseline ;;
    baseline)    rebaseline ;;
    kill-port)   shift; kill_port "${1:-}";;
    reset)       rm -f "$BASELINE" "$NEW_FILE"; echo "🧹 Baseline and diff cleared." ;;
    *)
      if [ ! -f "$BASELINE" ]; then
        echo "📌 No baseline found; capturing one now…"; save_baseline
        echo "Run again to detect and kill NEW Python listeners."
      fi
      if [ -f "$BASELINE" ]; then diff_new; kill_new; fi
      ;;
  esac
}
main "$@"

