#!/usr/bin/env bash
# 创建 Docker 宿主机数据/日志目录
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p \
  "$ROOT/data/mysql" \
  "$ROOT/data/media" \
  "$ROOT/logs/mysql" \
  "$ROOT/logs/backend" \
  "$ROOT/logs/nginx"

# 预先建空日志文件，避免挂载空目录导致 nginx 缺少默认文件
touch \
  "$ROOT/logs/backend/access.log" \
  "$ROOT/logs/backend/error.log" \
  "$ROOT/logs/nginx/access.log" \
  "$ROOT/logs/nginx/error.log" \
  "$ROOT/logs/mysql/error.log" \
  "$ROOT/logs/mysql/slow.log"

# MySQL 容器通常以 uid=999 写数据目录；放宽便于首次初始化
chmod -R a+rwX "$ROOT/data/mysql" "$ROOT/logs/mysql" || true
chmod -R a+rwX "$ROOT/data/media" "$ROOT/logs/backend" "$ROOT/logs/nginx" || true

echo "已创建数据目录："
echo "  $ROOT/data/mysql"
echo "  $ROOT/data/media"
echo "已创建日志："
echo "  $ROOT/logs/backend/access.log"
echo "  $ROOT/logs/backend/error.log"
echo "  $ROOT/logs/nginx/access.log"
echo "  $ROOT/logs/nginx/error.log"
echo "  $ROOT/logs/mysql/error.log"
echo "  $ROOT/logs/mysql/slow.log"
