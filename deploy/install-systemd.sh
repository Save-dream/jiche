#!/usr/bin/env bash
# 安装并启用 systemd 服务（开机自启）
# 用法: sudo bash deploy/install-systemd.sh
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ "$(id -u)" -ne 0 ]]; then
  echo_err "请使用 root 或 sudo 执行: sudo bash $DEPLOY_DIR/install-systemd.sh"
  exit 1
fi

mkdir -p "$LOG_DIR"
UNIT_SRC="$DEPLOY_DIR/jiche.service"
UNIT_DST="/etc/systemd/system/jiche.service"

# 按实际 JICHE_HOME 重写路径
sed "s|/home/jiche|$JICHE_HOME|g" "$UNIT_SRC" > "$UNIT_DST"

systemctl daemon-reload
systemctl enable jiche
systemctl restart jiche
systemctl status jiche --no-pager
echo_ok "systemd 服务已安装并启动: systemctl status jiche"
