# 极车云服务器部署脚本

代码目录默认：`/home/jiche`（可用环境变量 `JICHE_HOME` 覆盖）。

```
/home/jiche/
├── jiche-backend/
├── jiche-frontend/
└── deploy/          ← 本目录
```

## 快速启动（推荐）

> **Python 必须是 3.10 / 3.11 / 3.12**。  
> **Ubuntu 26.04** 默认只有 **Python 3.14**，`apt` 没有 3.12 包——请用下面「方案 D」。

```bash
# 先看系统和已有 Python
cat /etc/os-release | head -5
python3 --version
ls /usr/bin/python3*
```

### 安装 Python（按你的系统选一种）

**方案 D：Ubuntu 26.04（你的情况）—— 用 uv 装 3.12（推荐）**

```bash
cd /home/jiche
git pull
bash deploy/install-python312.sh --seed
```

等价手动步骤：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv python install 3.12
cd /home/jiche
rm -rf jiche-backend/.venv
PYTHON_BIN="$(uv python find 3.12)" bash deploy/setup.sh --seed
```

**方案 A：Ubuntu 22.04（自带 3.10）**

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-dev \
  libjpeg-dev zlib1g-dev libpng-dev
cd /home/jiche
rm -rf jiche-backend/.venv
PYTHON_BIN=python3.10 bash deploy/setup.sh --seed
```

**方案 B：用 deadsnakes 装 3.11（旧版 Ubuntu）**

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
  libjpeg-dev zlib1g-dev libpng-dev
cd /home/jiche
rm -rf jiche-backend/.venv
PYTHON_BIN=python3.11 bash deploy/setup.sh --seed
```

### 继续部署

```bash
# 2. 编辑生产配置（必做）
nano jiche-backend/.env
# 至少改：DJANGO_DEBUG=false、DJANGO_ALLOWED_HOSTS、数据库、SHARE_WEB_BASE_URL、CORS

# 3. 启动后端
bash deploy/start.sh

# 4. 安装 Nginx（前端静态 + /api 反代）
sudo bash deploy/install-nginx.sh

# 5. 看状态
bash deploy/status.sh
```

或一键（未初始化会自动 setup）：

```bash
bash deploy/up.sh --seed
sudo bash deploy/install-nginx.sh
```

浏览器访问：`http://服务器公网IP`

---

## 常用命令

| 命令 | 说明 |
|------|------|
| `bash deploy/setup.sh` | 初始化环境 |
| `bash deploy/setup.sh --seed` | 初始化并写入演示数据 |
| `bash deploy/build-frontend.sh` | 仅重新构建前端 |
| `bash deploy/start.sh` | 启动后端（Gunicorn 守护进程） |
| `bash deploy/stop.sh` | 停止后端 |
| `bash deploy/restart.sh` | 重启后端 |
| `bash deploy/status.sh` | 查看状态 / 日志尾巴 |
| `bash deploy/up.sh` | 自动初始化（如需要）并启动 |
| `sudo bash deploy/install-nginx.sh` | 安装 Nginx 站点 |
| `sudo bash deploy/install-systemd.sh` | 注册开机自启（systemd） |

### 无 Nginx、临时直接访问 API

```bash
GUNICORN_BIND=0.0.0.0:8000 bash deploy/restart.sh
# 然后访问 http://公网IP:8000/api/brands/
# 安全组需放行 8000（仅调试用）
```

---

## .env 生产示例要点

```env
DJANGO_SECRET_KEY=随机长字符串
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=你的公网IP,你的域名

DB_ENGINE=mysql
DB_NAME=jiche
DB_USER=jiche
DB_PASSWORD=强密码
DB_HOST=127.0.0.1
DB_PORT=3306

WECHAT_MOCK=true
CORS_ALLOWED_ORIGINS=http://你的公网IP
SHARE_WEB_BASE_URL=http://你的公网IP
```

若暂用 SQLite，保持 `DB_ENGINE=sqlite` 即可先跑通。

---

## 日志位置

- `deploy/logs/access.log`
- `deploy/logs/error.log`

```bash
tail -f /home/jiche/deploy/logs/error.log
```

---

## 更新代码后

```bash
cd /home/jiche
git pull
cd jiche-backend && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
bash ../deploy/build-frontend.sh
bash ../deploy/restart.sh
# 若用了 systemd：sudo systemctl restart jiche
```
