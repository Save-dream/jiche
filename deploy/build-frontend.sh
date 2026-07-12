#!/usr/bin/env bash
# 构建前端静态资源到 jiche-frontend/dist
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ ! -d "$FRONTEND_DIR" ]]; then
  echo_err "找不到前端目录: $FRONTEND_DIR"
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo_err "未安装 npm，请先安装 Node.js 20+"
  exit 1
fi

cd "$FRONTEND_DIR"
if [[ ! -f .env.production ]]; then
  echo 'VITE_API_BASE_URL=/api' > .env.production
  echo_info "已生成 .env.production (VITE_API_BASE_URL=/api)"
fi

echo_info "npm install..."
npm install
echo_info "npm run build..."
npm run build
echo_ok "前端构建完成: $FRONTEND_DIR/dist"
