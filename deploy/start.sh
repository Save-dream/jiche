#!/usr/bin/env bash
# 启动后端 Gunicorn
# 环境变量（可选）:
#   GUNICORN_BIND=0.0.0.0:8000   # 无 Nginx 时对外直接访问
#   GUNICORN_WORKERS=3
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_venv

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo_warn "服务已在运行 (PID=$(cat "$PID_FILE"))"
  echo "如需重启: bash $DEPLOY_DIR/restart.sh"
  exit 0
fi

cd "$BACKEND_DIR"
echo_info "启动 Gunicorn -> $GUNICORN_BIND (workers=$GUNICORN_WORKERS)"
"$GUNICORN" config.wsgi:application \
  --bind "$GUNICORN_BIND" \
  --workers "$GUNICORN_WORKERS" \
  --timeout "$GUNICORN_TIMEOUT" \
  --pid "$PID_FILE" \
  --access-logfile "$ACCESS_LOG" \
  --error-logfile "$ERROR_LOG" \
  --capture-output \
  --daemon

sleep 1
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo_ok "后端已启动 PID=$(cat "$PID_FILE")"
  echo "  访问日志: $ACCESS_LOG"
  echo "  错误日志: $ERROR_LOG"
  echo "  健康检查: curl -s http://127.0.0.1:8000/api/brands/"
else
  echo_err "启动失败，请查看: $ERROR_LOG"
  tail -n 40 "$ERROR_LOG" 2>/dev/null || true
  exit 1
fi
