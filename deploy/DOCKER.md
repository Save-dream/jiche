# 极车 Docker 部署

数据与日志全部落在宿主机，路径清单见 [`PATHS.md`](./PATHS.md)。

服务器开机后，只要 Docker 已启用，容器会随 `restart: always` 自动拉起。

## 为何服务器 git pull 没有新代码？

Docker / 用户管理等改动若**还没 push 到 GitHub**，服务器会显示 `Already up to date`。  
请先在本地提交并推送 `main`，再在服务器 `git pull`。

## 一次性准备

```bash
cd /home/jiche
git pull

# 1) 宿主机目录
bash deploy/prepare-host-dirs.sh

# 2) 安装 Docker（get.docker.com 在国内常失败，优先用下面任一方式）
```

### 安装 Docker（推荐 apt，国内更稳）

**方式 A：系统自带包（最简单）**

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2
# 若没有 docker-compose-v2 插件，可装独立包：
# sudo apt-get install -y docker-compose
sudo systemctl enable --now docker
docker --version
docker compose version || docker-compose --version
```

**方式 B：阿里云 Docker CE 镜像**

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
```

> `curl https://get.docker.com | sh` 在阿里云等环境常出现 `Connection reset by peer`，请改用上面方式。

```bash
# 3) 环境变量
cp .env.docker.example .env
nano .env   # 改密码、公网 IP、SECRET_KEY
```

## Docker Hub 超时（国内 ECS 常见）

报错类似：`dial tcp ... registry-1.docker.io ... i/o timeout`

```bash
bash deploy/configure-docker-mirror.sh
sudo docker pull docker.m.daocloud.io/library/mysql:8.0
```

compose / Dockerfile 已默认使用 `docker.m.daocloud.io/library/...` 前缀。

## 启动 / 更新

```bash
cd /home/jiche

# 停旧进程，避免占 80 端口
bash deploy/stop.sh 2>/dev/null || true
sudo systemctl stop jiche 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

bash deploy/prepare-host-dirs.sh
bash deploy/configure-docker-mirror.sh
sudo docker compose up -d --build

sudo docker compose ps
tail -f logs/backend/error.log
```

浏览器访问：`http://服务器公网IP`

若没有 `docker compose` 子命令，用：

```bash
sudo docker-compose up -d --build
```

## 开机自启

1. `systemctl enable docker`  
2. compose 中 `restart: always`  

可选 systemd 包装见下文「可选：systemd」。

## 数据与日志（摘要）

| 类型 | 宿主机路径 |
|------|------------|
| MySQL 数据 | `/home/jiche/data/mysql/` |
| 上传文件 | `/home/jiche/data/media/` |
| 后端日志 | `/home/jiche/logs/backend/*.log` |
| Nginx 日志 | `/home/jiche/logs/nginx/*.log` |
| MySQL 日志 | `/home/jiche/logs/mysql/*.log` |

完整表：[`PATHS.md`](./PATHS.md)

## 从现有 SQLite 迁到 Docker MySQL

```bash
bash deploy/stop.sh
sudo systemctl stop jiche 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

cd /home/jiche/jiche-backend
source .venv/bin/activate
python manage.py dumpdata \
  --natural-foreign --natural-primary \
  -e contenttypes -e auth.permission \
  -o /tmp/jiche_dump.json
```

启动 Docker 后导入：

```bash
cd /home/jiche
bash deploy/prepare-host-dirs.sh
sudo docker compose up -d --build
sudo docker compose cp /tmp/jiche_dump.json backend:/tmp/jiche_dump.json
sudo docker compose exec backend python manage.py loaddata /tmp/jiche_dump.json
```

不需要旧数据则跳过 dump/load。

## 连接 MySQL

| 项 | 值 |
|---|---|
| Host | `127.0.0.1` |
| Port | `.env` 中 `MYSQL_PUBLISH_PORT`，默认 `3306` |
| Database / User / Password | `.env` 里 `DB_*` |

```bash
mysql -h127.0.0.1 -P3306 -ujiche -p
# 或
sudo docker compose exec mysql mysql -ujiche -p jiche
```

## 可选：systemd

```bash
sudo tee /etc/systemd/system/jiche-docker.service >/dev/null <<'EOF'
[Unit]
Description=Jiche Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/jiche
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now jiche-docker.service
```

## 常用命令

| 命令 | 说明 |
|---|---|
| `bash deploy/prepare-host-dirs.sh` | 创建 data/logs 目录 |
| `sudo docker compose up -d --build` | 构建并启动 |
| `sudo docker compose restart` | 重启 |
| `sudo docker compose down` | 停容器（**保留**宿主机 data/logs） |
| `tail -f logs/backend/error.log` | 看后端错误日志 |
