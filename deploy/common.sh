#!/usr/bin/env bash
# 公共变量：可被其他脚本 source
# 用法：在任意 deploy/*.sh 开头 source "$(dirname "$0")/common.sh"

set -euo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录：默认 deploy 的上一级；也可用环境变量 JICHE_HOME 覆盖
JICHE_HOME="${JICHE_HOME:-$(cd "$DEPLOY_DIR/.." && pwd)}"

BACKEND_DIR="$JICHE_HOME/jiche-backend"
FRONTEND_DIR="$JICHE_HOME/jiche-frontend"
VENV_DIR="$BACKEND_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
GUNICORN="$VENV_DIR/bin/gunicorn"

RUN_DIR="$DEPLOY_DIR/run"
LOG_DIR="$DEPLOY_DIR/logs"
PID_FILE="$RUN_DIR/gunicorn.pid"
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"

# Gunicorn 监听（Nginx 反代时用 127.0.0.1；直连调试可改 0.0.0.0）
GUNICORN_BIND="${GUNICORN_BIND:-127.0.0.1:8000}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-3}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-60}"

mkdir -p "$RUN_DIR" "$LOG_DIR"

require_backend() {
  if [[ ! -d "$BACKEND_DIR" ]]; then
    echo "错误：找不到后端目录 $BACKEND_DIR"
    echo "请确认代码在 $JICHE_HOME 下，结构为 jiche-backend / jiche-frontend"
    exit 1
  fi
}

require_venv() {
  require_backend
  if [[ ! -x "$PYTHON" ]]; then
    echo "错误：未找到虚拟环境 $VENV_DIR"
    echo "请先执行：bash $DEPLOY_DIR/setup.sh"
    exit 1
  fi
}

echo_info() { echo "[INFO] $*"; }
echo_ok() { echo "[ OK ] $*"; }
echo_warn() { echo "[WARN] $*"; }
echo_err() { echo "[ERR ] $*" >&2; }
