#!/usr/bin/env bash
# 按公网 IP/域名快速写入生产 .env 关键项并重启后端
# 用法:
#   bash deploy/set-public-host.sh 120.27.150.71
#   bash deploy/set-public-host.sh your.domain.com
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

HOST="${1:-}"
if [[ -z "$HOST" ]]; then
  echo_err "请传入公网 IP 或域名，例如: bash deploy/set-public-host.sh 120.27.150.71"
  exit 1
fi

ENV_FILE="$BACKEND_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$BACKEND_DIR/.env.example" "$ENV_FILE"
  echo_info "已从 .env.example 生成 .env"
fi

SCHEME="${PUBLIC_SCHEME:-http}"
ORIGIN="${SCHEME}://${HOST}"

set_kv() {
  local key="$1"
  local val="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

set_kv "DJANGO_DEBUG" "false"
set_kv "DJANGO_ALLOWED_HOSTS" "localhost,127.0.0.1,${HOST}"
set_kv "CORS_ALLOWED_ORIGINS" "${ORIGIN}"
set_kv "SHARE_WEB_BASE_URL" "${ORIGIN}"
rm -f "${ENV_FILE}.bak"

echo_ok "已更新 .env："
echo "  DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,${HOST}"
echo "  CORS_ALLOWED_ORIGINS=${ORIGIN}"
echo "  SHARE_WEB_BASE_URL=${ORIGIN}"

if [[ -x "$GUNICORN" ]]; then
  bash "$DEPLOY_DIR/restart.sh"
else
  echo_warn "后端尚未初始化，请先执行 setup 后再 restart"
fi
