#!/usr/bin/env bash
# 将宿主机部署从 SQLite 切换为 MySQL（非 Docker 场景）
# Docker 部署请改用：见 deploy/DOCKER.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

require_backend

ENV_FILE="$BACKEND_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo_err "缺少 $ENV_FILE"
  exit 1
fi

DB_NAME="${DB_NAME:-jiche}"
DB_USER="${DB_USER:-jiche}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-}"

if [[ -z "$DB_PASSWORD" ]]; then
  echo_err "请设置环境变量 DB_PASSWORD（及可选 DB_USER/DB_NAME）后再执行"
  echo_info "示例："
  echo "  DB_PASSWORD='强密码' MYSQL_ROOT_PASSWORD='root强密码' bash deploy/switch-to-mysql.sh"
  exit 1
fi

echo_info "1) 安装 MySQL 客户端/服务（若已安装会跳过失败）"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server mysql-client || true
  sudo systemctl enable --now mysql || true
fi

echo_info "2) 创建库与用户"
SQL=$(cat <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
ALTER USER '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
ALTER USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'%';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
)

if [[ -n "$MYSQL_ROOT_PASSWORD" ]]; then
  mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "$SQL"
elif sudo mysql -e "SELECT 1" >/dev/null 2>&1; then
  sudo mysql -e "$SQL"
else
  mysql -uroot -e "$SQL"
fi

echo_info "3) 更新 .env 为 MySQL"
python3 - <<'PY' "$ENV_FILE" "$DB_NAME" "$DB_USER" "$DB_PASSWORD" "$DB_HOST" "$DB_PORT"
import re, sys
path, name, user, password, host, port = sys.argv[1:7]
text = open(path, encoding='utf-8').read()
pairs = {
    'DB_ENGINE': 'mysql',
    'DB_NAME': name,
    'DB_USER': user,
    'DB_PASSWORD': password,
    'DB_HOST': host,
    'DB_PORT': port,
}
for key, val in pairs.items():
    pattern = re.compile(rf'^{key}=.*$', re.M)
    line = f'{key}={val}'
    if pattern.search(text):
        text = pattern.sub(line, text)
    else:
        text = text.rstrip() + '\n' + line + '\n'
open(path, 'w', encoding='utf-8').write(text)
print('updated', path)
PY

echo_info "4) 导出 SQLite（若存在）"
DUMP="/tmp/jiche_sqlite_dump.json"
require_venv
cd "$BACKEND_DIR"
if [[ -f db.sqlite3 ]]; then
  # 临时用 sqlite 导出
  DB_ENGINE=sqlite "$PYTHON" manage.py dumpdata \
    --natural-foreign --natural-primary \
    -e contenttypes -e auth.permission \
    -o "$DUMP" || true
  echo_ok "已导出 $DUMP"
else
  echo_warn "未找到 db.sqlite3，跳过导出"
  DUMP=""
fi

echo_info "5) migrate MySQL"
export DB_ENGINE=mysql
"$PYTHON" manage.py migrate --noinput

if [[ -n "$DUMP" && -f "$DUMP" ]]; then
  echo_info "6) 导入旧数据"
  "$PYTHON" manage.py loaddata "$DUMP" || echo_warn "loaddata 失败，可手工排查后重试"
fi

"$PYTHON" manage.py create_init_accounts --reset-password || true

echo_ok "已切换到 MySQL。请执行: bash deploy/restart.sh"
echo_info "连接信息：host=$DB_HOST port=$DB_PORT db=$DB_NAME user=$DB_USER"
