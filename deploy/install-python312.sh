#!/usr/bin/env bash
# Ubuntu 26.04 等仅有 Python 3.14 的系统：用 uv 安装 3.12 并跑 setup
# 用法: bash deploy/install-python312.sh [--seed]
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

DO_SEED=0
for arg in "$@"; do
  case "$arg" in
    --seed) DO_SEED=1 ;;
  esac
done

echo_info "系统: $(. /etc/os-release 2>/dev/null; echo "${PRETTY_NAME:-unknown}")"
echo_info "当前 python3: $(python3 --version 2>/dev/null || echo none)"

# 图片相关系统库（Pillow wheel 一般不需要，保险起见装上）
if command -v apt-get >/dev/null 2>&1; then
  echo_info "安装编译/图片依赖..."
  apt-get update -y
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl ca-certificates \
    libjpeg-dev zlib1g-dev libpng-dev \
    build-essential || true
fi

# 安装 uv
if ! command -v uv >/dev/null 2>&1; then
  echo_info "安装 uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1090
  source "$HOME/.local/bin/env" 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
fi
# 再确认 PATH
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo_err "uv 安装失败，请检查网络后重试"
  exit 1
fi

echo_info "用 uv 安装 Python 3.12..."
uv python install 3.12
PY312="$(uv python find 3.12)"
echo_ok "Python 3.12 路径: $PY312"

rm -rf "$VENV_DIR"
if [[ "$DO_SEED" -eq 1 ]]; then
  PYTHON_BIN="$PY312" bash "$DEPLOY_DIR/setup.sh" --seed
else
  PYTHON_BIN="$PY312" bash "$DEPLOY_DIR/setup.sh"
fi
