#!/usr/bin/env bash
# MySQL 生产库初始化：创建数据库 + Django 迁移 + 预置账号
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "请先复制 .env.example 为 .env 并配置 MySQL 连接"
  exit 1
fi

# shellcheck disable=SC1091
source .env 2>/dev/null || true

MYSQL_HOST="${DB_HOST:-127.0.0.1}"
MYSQL_PORT="${DB_PORT:-3306}"
MYSQL_USER="${DB_USER:-root}"
MYSQL_PASSWORD="${DB_PASSWORD:-}"
MYSQL_DB="${DB_NAME:-jiche}"

echo "==> 1/3 创建 MySQL 数据库 ${MYSQL_DB}"
if [ -n "$MYSQL_PASSWORD" ]; then
  mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < scripts/init_mysql.sql
else
  mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" < scripts/init_mysql.sql
fi

echo "==> 2/3 执行 Django 迁移"
export DB_ENGINE=mysql
.venv/bin/python manage.py migrate --noinput

echo "==> 3/3 初始化预置账号与品牌字典"
.venv/bin/python manage.py create_init_accounts --reset-password || true
.venv/bin/python manage.py seed_catalog || true

if [[ "${SEED_DEMO:-0}" == "1" ]]; then
  echo "==> 可选：写入演示数据（SEED_DEMO=1）"
  .venv/bin/python manage.py seed_auth_demo || true
  .venv/bin/python manage.py seed_demo_data || true
fi

echo "完成。生产启动: bash deploy/restart.sh  或 Docker: 见 deploy/DOCKER.md"
