#!/usr/bin/env bash
# 一键初始化：虚拟环境、依赖、.env、迁移、（可选）种子数据、前端构建
# 用法：
#   bash deploy/setup.sh
#   bash deploy/setup.sh --seed          # 额外写入演示账号/车源
#   bash deploy/setup.sh --skip-frontend # 跳过前端 npm build

set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

DO_SEED=0
SKIP_FRONTEND=0
for arg in "$@"; do
  case "$arg" in
    --seed) DO_SEED=1 ;;
    --skip-frontend) SKIP_FRONTEND=1 ;;
    -h|--help)
      echo "用法: bash deploy/setup.sh [--seed] [--skip-frontend]"
      exit 0
      ;;
  esac
done

require_backend
echo_info "JICHE_HOME=$JICHE_HOME"

PY_BIN="$(resolve_python)"
assert_supported_python "$PY_BIN"

# 若已有 venv 但版本不对，提示重建
if [[ -x "$PYTHON" ]]; then
  VENV_VER="$(python_major_minor "$PYTHON")"
  case "$VENV_VER" in
    3.10|3.11|3.12|3.8|3.9) ;;
    *)
      echo_warn "现有虚拟环境 Python=$VENV_VER，将删除并重建为 $PY_BIN"
      rm -rf "$VENV_DIR"
      ;;
  esac
fi

# —— Python 虚拟环境 ——
if [[ ! -x "$PYTHON" ]]; then
  echo_info "创建虚拟环境 ($PY_BIN)..."
  "$PY_BIN" -m venv "$VENV_DIR"
fi
echo_info "安装 Python 依赖..."
"$PIP" install -U pip setuptools wheel
"$PIP" install -r "$BACKEND_DIR/requirements.txt"

# —— .env ——
if [[ ! -f "$BACKEND_DIR/.env" ]]; then
  echo_info "生成 $BACKEND_DIR/.env（请按服务器实际情况修改）"
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  # 生成随机 SECRET_KEY
  if command -v openssl >/dev/null 2>&1; then
    SECRET="$(openssl rand -hex 32)"
    if grep -q '^DJANGO_SECRET_KEY=' "$BACKEND_DIR/.env"; then
      sed -i.bak "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$SECRET|" "$BACKEND_DIR/.env" && rm -f "$BACKEND_DIR/.env.bak"
    fi
  fi
  echo_warn "请编辑 .env：DJANGO_DEBUG / ALLOWED_HOSTS / MySQL / SHARE_WEB_BASE_URL / CORS"
else
  echo_ok ".env 已存在，跳过复制"
fi

# —— 媒体目录 ——
mkdir -p "$BACKEND_DIR/media/uploads"

# —— 数据库迁移 ——
echo_info "执行数据库迁移..."
cd "$BACKEND_DIR"
"$PYTHON" manage.py migrate --noinput

if [[ "$DO_SEED" -eq 1 ]]; then
  echo_info "写入演示数据..."
  "$PYTHON" manage.py seed_auth_demo || true
  "$PYTHON" manage.py seed_catalog || true
  "$PYTHON" manage.py seed_demo_data || true
  echo_ok "演示数据已尝试写入"
fi

# —— 前端 ——
if [[ "$SKIP_FRONTEND" -eq 0 ]]; then
  if [[ ! -d "$FRONTEND_DIR" ]]; then
    echo_warn "未找到前端目录 $FRONTEND_DIR，跳过构建"
  elif ! command -v npm >/dev/null 2>&1; then
    echo_warn "未安装 npm，跳过前端构建。请安装 Node.js 后执行: bash deploy/build-frontend.sh"
  else
    bash "$DEPLOY_DIR/build-frontend.sh"
  fi
fi

echo_ok "初始化完成"
echo ""
echo "下一步："
echo "  1. 编辑环境变量: nano $BACKEND_DIR/.env"
echo "  2. 启动后端:     bash $DEPLOY_DIR/start.sh"
echo "  3. （推荐）配置 Nginx，参考: $DEPLOY_DIR/nginx.jiche.conf"
echo "  4. 查看状态:     bash $DEPLOY_DIR/status.sh"
