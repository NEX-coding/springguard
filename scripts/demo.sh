#!/usr/bin/env bash
# 一键启动：可供本机与局域网他人使用的 Web 服务
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> 启动 SpringGuard Web（样例扫描 / ZIP 上传）"
echo "    本机:   http://127.0.0.1:5193/"
IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
if [[ -n "${IP:-}" ]]; then
  echo "    局域网: http://${IP}:5193/"
fi
exec python3 scripts/app_server.py 5193
