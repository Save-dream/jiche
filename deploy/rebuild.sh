#!/usr/bin/env bash
# 强制拉取最新代码并无缓存重建前后端镜像（解决「代码已 push 但页面/接口仍是旧的」）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

cd "$JICHE_HOME"

echo_info "1) git pull"
git fetch origin
git checkout main
git pull origin main
git log -1 --oneline

echo_info "2) 确认关键源文件已更新"
grep -n "平台管理员不可封禁" jiche-frontend/src/views/admin/AdminUsers.vue | head -2 || {
  echo_err "AdminUsers.vue 仍是旧内容，pull 可能失败"
  exit 1
}
grep -n "审核失败" jiche-backend/apps/shops/views.py | head -2 || {
  echo_err "shops/views.py 仍是旧内容"
  exit 1
}

echo_info "3) 准备宿主机目录"
bash "$DEPLOY_DIR/prepare-host-dirs.sh"

echo_info "4) 无缓存重建并启动（backend + nginx 必须重新 build）"
sudo docker compose build --no-cache backend nginx
sudo docker compose up -d --force-recreate

echo_info "5) 状态"
sudo docker compose ps
sudo docker compose logs --tail=30 backend | grep -E 'Listening|Error|Traceback|初始登录' || true

echo_ok "完成。请硬刷新浏览器（Ctrl+Shift+R）后再测审核通过与用户管理页。"
echo_info "用户管理页标题旁应出现「平台管理员不可封禁、不可删除」说明文字。"
