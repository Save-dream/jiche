# 极车后端（Django 4.2）

## 快速开始（本地 SQLite）

```bash
cd jiche-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 已含占位微信配置
python manage.py migrate
python manage.py seed_auth_demo   # 预置超管 + 普通/商家用户
python manage.py seed_catalog     # 品牌车型字典
python manage.py seed_demo_data   # 演示车源 + 收藏 + 留言
python manage.py runserver 8000
```

## 生产部署（代码目录：`/home/jiche`）

```bash
# 1. 准备目录与代码
sudo mkdir -p /home/jiche
sudo chown $USER:$USER /home/jiche
# 将 jiche-backend、jiche-frontend 放到 /home/jiche/ 下

# 2. 后端依赖与迁移
cd /home/jiche/jiche-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 再按生产环境修改 .env
python manage.py migrate
python manage.py seed_auth_demo
python manage.py seed_catalog

# 3. 用 Gunicorn 启动（systemd 示例见下方）
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

systemd 服务文件 `/etc/systemd/system/jiche.service`：

```ini
[Unit]
Description=Jiche Django
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/jiche/jiche-backend
Environment="PATH=/home/jiche/jiche-backend/.venv/bin"
ExecStart=/home/jiche/jiche-backend/.venv/bin/gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 --workers 3 --timeout 60
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /home/jiche/jiche-backend/media
sudo chown -R www-data:www-data /home/jiche/jiche-backend
sudo systemctl daemon-reload
sudo systemctl enable --now jiche
```

Nginx 中前端静态目录与媒体：

- 前端：`root /home/jiche/jiche-frontend/dist;`
- 媒体：`location /media/ { alias /home/jiche/jiche-backend/media/; }`

## 前端开发服务器（本地）

```bash
cd jiche-frontend
npm run dev   # Vite 代理 /api -> http://127.0.0.1:8000
```

## MySQL 生产库建表

**推荐方式（Django 迁移）：**

```bash
# 1. 修改 .env
DB_ENGINE=mysql
DB_NAME=jiche
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306

# 2. 一键初始化
chmod +x scripts/setup_mysql.sh
./scripts/setup_mysql.sh
```

**手动方式：**

```bash
mysql -u root -p < scripts/init_mysql.sql          # 创建库
python manage.py migrate                           # 建表
python manage.py seed_auth_demo                    # 预置账号
```

**SQL 参考文件（仅供 DBA 审阅）：** `scripts/mysql_auth_tables.sql`

## 微信配置（占位 → 真实）

当前 `.env` 使用占位假数据 + `WECHAT_MOCK=true`，不会调用微信 API。

系统完成后，在 `.env` 替换：

```env
WECHAT_MOCK=false
WECHAT_MINI_APP_ID=真实小程序AppID
WECHAT_MINI_APP_SECRET=真实小程序Secret
WECHAT_WEB_APP_ID=真实网站应用AppID
WECHAT_WEB_APP_SECRET=真实网站应用Secret
```

并更新预置管理员的 `unionid`（`python manage.py init_super_admin --unionid 真实unionid`）。

## 认证 API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/login-ticket/` | Web 扫码票据 |
| GET | `/api/auth/login-ticket/{id}/` | 轮询状态 |
| POST | `/api/auth/login-ticket/{id}/simulate/` | Dev 模拟扫码 |
| GET | `/api/auth/me/` | 当前用户 |
| GET | `/api/admin/users/` | 管理员列表 |

## 商家入驻 API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/uploads/image/` | 上传图片 |
| POST | `/api/applications/` | 提交入驻申请 |
| GET | `/api/applications/my/` | 我的最新申请 |
| GET | `/api/admin/applications/` | 管理端申请列表 |
| POST | `/api/admin/applications/{id}/audit/` | 审核通过/驳回 |

## 测试

```bash
python manage.py test apps.accounts.tests apps.shops.tests -v 2
```
