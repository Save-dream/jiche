#!/usr/bin/env bash
# 安装 Nginx 站点配置
# 用法: sudo bash deploy/install-nginx.sh
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ "$(id -u)" -ne 0 ]]; then
  echo_err "请使用 root 或 sudo 执行: sudo bash $DEPLOY_DIR/install-nginx.sh"
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  echo_info "安装 nginx..."
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update && apt-get install -y nginx
  elif command -v yum >/dev/null 2>&1; then
    yum install -y nginx
  else
    echo_err "请手动安装 nginx"
    exit 1
  fi
fi

CONF_SRC="$DEPLOY_DIR/nginx.jiche.conf"
TMP="$(mktemp)"
sed "s|/home/jiche|$JICHE_HOME|g" "$CONF_SRC" > "$TMP"

if [[ -d /etc/nginx/sites-available ]]; then
  cp "$TMP" /etc/nginx/sites-available/jiche
  ln -sf /etc/nginx/sites-available/jiche /etc/nginx/sites-enabled/jiche
  rm -f /etc/nginx/sites-enabled/default
else
  # CentOS / 部分发行版
  cp "$TMP" /etc/nginx/conf.d/jiche.conf
fi
rm -f "$TMP"

nginx -t
systemctl enable nginx
systemctl reload nginx || systemctl restart nginx
echo_ok "Nginx 已配置并重载"
echo_warn "请确认安全组已放行 80 端口；有域名时再改 server_name 并配置 HTTPS"
