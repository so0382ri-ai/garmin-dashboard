#!/bin/bash
# Garmin のデータを取得して garmin.json を更新する(launchd から毎晩実行する想定)。
#
# 手動実行:  ./scripts/run.sh
# ログ:      logs/fetch.log(リポジトリ直下。*.log は .gitignore で除外済み)
#
# 使う Python の優先順位:
#   1. 環境変数 PYTHON
#   2. リポジトリ直下の .venv/bin/python
#   3. PATH 上の python3
set -euo pipefail

# このスクリプトの場所からリポジトリのルートを求める(どこから実行しても動くように)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# launchd の PATH は最小限なので、Homebrew などの場所を足しておく
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/fetch.log"
MAX_LOG_LINES=2000
mkdir -p "$LOG_DIR"

# ログが大きくなりすぎないよう、末尾 MAX_LOG_LINES 行だけ残す
if [[ -f "$LOG_FILE" ]] && (( $(wc -l < "$LOG_FILE") > MAX_LOG_LINES )); then
  tail -n "$MAX_LOG_LINES" "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

if [[ -n "${PYTHON:-}" ]]; then
  PY="$PYTHON"
elif [[ -x "$REPO_DIR/.venv/bin/python" ]]; then
  PY="$REPO_DIR/.venv/bin/python"
else
  PY="$(command -v python3 || true)"
fi

{
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') 開始 ====="
  if [[ -z "$PY" ]]; then
    echo "エラー: python3 が見つかりません。PYTHON 環境変数で指定してください。"
    exit 1
  fi
  echo "Python: $PY"
  status=0
  "$PY" "$REPO_DIR/scripts/garmin_fetch.py" "$@" || status=$?
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') 終了 (exit $status) ====="
  exit "$status"
} >> "$LOG_FILE" 2>&1
