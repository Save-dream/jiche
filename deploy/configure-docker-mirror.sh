#!/usr/bin/env bash
# 配置 Docker 国内镜像加速（解决 pull docker.io 超时）
set -euo pipefail

MIRROR_JSON='{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1ms.run",
    "https://dockerproxy.cn"
  ]
}'

echo "[INFO] 写入 /etc/docker/daemon.json"
sudo mkdir -p /etc/docker
if [[ -f /etc/docker/daemon.json ]]; then
  sudo cp -a /etc/docker/daemon.json "/etc/docker/daemon.json.bak.$(date +%s)"
fi
echo "$MIRROR_JSON" | sudo tee /etc/docker/daemon.json >/dev/null

echo "[INFO] 重启 Docker"
sudo systemctl daemon-reload
sudo systemctl restart docker

echo "[ OK ] 已配置镜像加速。测试拉取："
echo "  sudo docker pull docker.m.daocloud.io/library/mysql:8.0"
