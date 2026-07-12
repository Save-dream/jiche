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

# Django 4.2 官方支持 3.8–3.12；优先选用 3.12/3.11/3.10（含 uv/pyenv 安装路径）
resolve_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    if [[ -x "$PYTHON_BIN" ]]; then
      echo "$PYTHON_BIN"
      return 0
    fi
    if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
      command -v "$PYTHON_BIN"
      return 0
    fi
    echo_err "指定的 PYTHON_BIN=$PYTHON_BIN 不存在"
    exit 1
  fi

  local cand
  # 常见安装位置：系统 apt / uv / pyenv / 手动编译
  local -a candidates=(
    python3.12 python3.11 python3.10
    /usr/local/bin/python3.12 /usr/local/bin/python3.11 /usr/local/bin/python3.10
    "$HOME/.local/bin/python3.12" "$HOME/.local/bin/python3.11"
    "$HOME/.pyenv/versions/3.12.10/bin/python" "$HOME/.pyenv/versions/3.12.9/bin/python"
    "$HOME/.pyenv/versions/3.12.8/bin/python" "$HOME/.pyenv/versions/3.11.11/bin/python"
  )

  # uv 默认安装目录
  if [[ -d "$HOME/.local/share/uv/python" ]]; then
    local uv_py
    while IFS= read -r uv_py; do
      candidates+=("$uv_py")
    done < <(find "$HOME/.local/share/uv/python" -type f -path '*/bin/python3.*' 2>/dev/null | sort -r)
  fi

  for cand in "${candidates[@]}"; do
    if [[ -x "$cand" ]]; then
      echo "$cand"
      return 0
    fi
    if command -v "$cand" >/dev/null 2>&1; then
      command -v "$cand"
      return 0
    fi
  done

  # 最后才考虑系统 python3（可能是 3.14，后面 assert 会拦截）
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi

  echo_err "未找到可用 Python，请先安装 3.10–3.12（见下方提示）"
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
      echo_err "Ubuntu 26.04 默认只有 3.14，请额外安装 3.12 后再跑 setup"
      echo ""
      echo "推荐（uv，最快）："
      echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
      echo "  source \$HOME/.local/bin/env 2>/dev/null || export PATH=\"\$HOME/.local/bin:\$PATH\""
      echo "  uv python install 3.12"
      echo "  rm -rf $VENV_DIR"
      echo "  PYTHON_BIN=\$(uv python find 3.12) bash $DEPLOY_DIR/setup.sh --seed"
      echo ""
      echo "或用官方源码安装 3.12："
      echo "  sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \\"
      echo "    libreadline-dev libsqlite3-dev libffi-dev liblzma-dev \\"
      echo "    libjpeg-dev libpng-dev wget"
      echo "  cd /tmp && wget https://www.python.org/ftp/python/3.12.10/Python-3.12.10.tgz"
      echo "  tar xf Python-3.12.10.tgz && cd Python-3.12.10"
      echo "  ./configure --enable-optimizations --prefix=/usr/local"
      echo "  make -j\$(nproc) && sudo make altinstall"
      echo "  rm -rf $VENV_DIR"
      echo "  PYTHON_BIN=/usr/local/bin/python3.12 bash $DEPLOY_DIR/setup.sh --seed"
      exit 1
      ;;
  esac
}

echo_info() { echo "[INFO] $*"; }
echo_ok() { echo "[ OK ] $*"; }
echo_warn() { echo "[WARN] $*"; }
echo_err() { echo "[ERR ] $*" >&2; }
