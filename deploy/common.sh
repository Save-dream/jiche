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

# Django 4.2 官方支持 3.8–3.12；优先选用系统中的 3.12/3.11/3.10
resolve_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
      command -v "$PYTHON_BIN"
      return 0
    fi
    echo_err "指定的 PYTHON_BIN=$PYTHON_BIN 不存在"
    exit 1
  fi
  local cand
  for cand in python3.12 python3.11 python3.10 python3; do
    if command -v "$cand" >/dev/null 2>&1; then
      command -v "$cand"
      return 0
    fi
  done
  echo_err "未找到 python3，请先安装 Python 3.10–3.12"
  exit 1
}

python_major_minor() {
  "$1" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
}

assert_supported_python() {
  local py="$1"
  local ver
  ver="$(python_major_minor "$py")"
  case "$ver" in
    3.10|3.11|3.12)
      echo_ok "使用 Python $ver ($py)"
      ;;
    3.8|3.9)
      echo_warn "Python $ver 可用，建议升级到 3.11/3.12"
      ;;
    *)
      echo_err "当前 Python $ver 不受支持（检测到路径: $py）"
      echo_err "Django 4.2 + Pillow 需要 Python 3.10–3.12，请勿使用 3.13/3.14"
      echo ""
      echo "Ubuntu/Debian 安装示例："
      echo "  sudo apt update"
      echo "  sudo apt install -y python3.12 python3.12-venv python3.12-dev \\"
      echo "    libjpeg-dev zlib1g-dev libpng-dev"
      echo ""
      echo "然后删除旧虚拟环境并重跑："
      echo "  rm -rf $VENV_DIR"
      echo "  PYTHON_BIN=python3.12 bash $DEPLOY_DIR/setup.sh --seed"
      exit 1
      ;;
  esac
}

echo_info() { echo "[INFO] $*"; }
echo_ok() { echo "[ OK ] $*"; }
echo_warn() { echo "[WARN] $*"; }
echo_err() { echo "[ERR ] $*" >&2; }
