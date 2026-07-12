#!/usr/bin/env bash
# 查看服务状态
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

echo "======== 极车服务状态 ========"
echo "JICHE_HOME : $JICHE_HOME"
echo "Backend    : $BACKEND_DIR"
echo "Frontend   : $FRONTEND_DIR"
echo "Bind       : $GUNICORN_BIND"
echo ""

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  PID="$(cat "$PID_FILE")"
  echo "Gunicorn   : 运行中 (PID=$PID)"
  ps -p "$PID" -o pid,etime,cmd 2>/dev/null || true
else
  echo "Gunicorn   : 未运行"
fi

echo ""
if [[ -d "$FRONTEND_DIR/dist" ]]; then
  echo "前端 dist  : 已构建"
else
  echo "前端 dist  : 未构建（执行 bash deploy/build-frontend.sh）"
fi

if [[ -f "$BACKEND_DIR/.env" ]]; then
  echo ".env       : 存在"
else
  echo ".env       : 缺失（执行 bash deploy/setup.sh）"
fi

echo ""
echo "探测 API..."
if curl -fsS -m 3 "http://127.0.0.1:8000/api/brands/" >/dev/null 2>&1; then
  echo_ok "http://127.0.0.1:8000/api/brands/ 可达"
else
  echo_warn "API 暂不可达（服务未启动或绑定地址不同）"
fi

echo ""
echo "最近错误日志（末尾 15 行）:"
if [[ -f "$ERROR_LOG" ]]; then
  tail -n 15 "$ERROR_LOG"
else
  echo "(无日志文件)"
fi
