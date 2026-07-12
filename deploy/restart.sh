#!/usr/bin/env bash
# 重启后端
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$DIR/stop.sh" || true
sleep 1
bash "$DIR/start.sh"
