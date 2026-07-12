#!/usr/bin/env bash
# 停止后端 Gunicorn
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ ! -f "$PID_FILE" ]]; then
  echo_warn "未找到 PID 文件，尝试按进程名结束..."
  pkill -f "gunicorn config.wsgi:application" 2>/dev/null || true
  echo_ok "已尝试停止"
  exit 0
fi

PID="$(cat "$PID_FILE")"
if kill -0 "$PID" 2>/dev/null; then
  echo_info "停止 PID=$PID ..."
  kill "$PID" 2>/dev/null || true
  # 等待优雅退出
  for _ in $(seq 1 20); do
    if ! kill -0 "$PID" 2>/dev/null; then
      break
    fi
    sleep 0.3
  done
  if kill -0 "$PID" 2>/dev/null; then
    echo_warn "进程未退出，强制 kill -9"
    kill -9 "$PID" 2>/dev/null || true
  fi
  echo_ok "已停止"
else
  echo_warn "进程 $PID 不存在"
fi
rm -f "$PID_FILE"
