# 极车 Docker：宿主机数据与日志路径

以下路径相对代码根目录 `/home/jiche`（即含 `docker-compose.yml` 的目录）。

## 数据目录（持久化，bind mount）

| 用途 | 宿主机路径 | 容器内路径 | 服务 |
|------|------------|------------|------|
| MySQL 数据文件 | `/home/jiche/data/mysql/` | `/var/lib/mysql` | mysql |
| 上传图片 / 媒体 | `/home/jiche/data/media/` | `/app/media` | backend |

> `docker compose down` **不会**删除上述目录；只有手动 `rm` 才会丢数据。

## 日志目录（bind mount）

| 用途 | 宿主机路径 | 容器内路径 | 服务 |
|------|------------|------------|------|
| 后端访问日志 | `/home/jiche/logs/backend/access.log` | `/var/log/jiche/access.log` | gunicorn |
| 后端错误日志 | `/home/jiche/logs/backend/error.log` | `/var/log/jiche/error.log` | gunicorn |
| Nginx 访问日志 | `/home/jiche/logs/nginx/access.log` | `/var/log/nginx/access.log` | nginx |
| Nginx 错误日志 | `/home/jiche/logs/nginx/error.log` | `/var/log/nginx/error.log` | nginx |
| MySQL 错误日志 | `/home/jiche/logs/mysql/error.log` | `/var/log/mysql/error.log` | mysql |
| MySQL 慢查询 | `/home/jiche/logs/mysql/slow.log` | `/var/log/mysql/slow.log` | mysql |

## 常用查看命令

```bash
# 后端
tail -f /home/jiche/logs/backend/error.log
tail -f /home/jiche/logs/backend/access.log

# Nginx
tail -f /home/jiche/logs/nginx/error.log
tail -f /home/jiche/logs/nginx/access.log

# MySQL
tail -f /home/jiche/logs/mysql/error.log
tail -f /home/jiche/logs/mysql/slow.log

# 仍可用 Docker 汇总日志（补充用）
cd /home/jiche && sudo docker compose logs -f --tail=100
```

## 首次启动前

```bash
bash /home/jiche/deploy/prepare-host-dirs.sh
```
