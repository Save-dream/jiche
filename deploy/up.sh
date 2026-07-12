#!/usr/bin/env bash
# 一键：若未初始化则 setup，然后启动
# 用法: bash deploy/up.sh [--seed]
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/common.sh"

ARGS=()
for arg in "$@"; do
  ARGS+=("$arg")
done

require_backend
if [[ ! -x "$PYTHON" ]] || [[ ! -f "$BACKEND_DIR/.env" ]]; then
  echo_info "检测到未初始化，先执行 setup..."
  bash "$DIR/setup.sh" "${ARGS[@]}"
fi

bash "$DIR/start.sh"
bash "$DIR/status.sh"
