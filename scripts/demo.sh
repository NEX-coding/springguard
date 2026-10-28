#!/usr/bin/env bash
# 一键演示：Guard 扫描 → 评测 → 打开结果页
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> [1/3] SpringGuard 确定性扫描"
python3 scripts/run_pipeline.py --project samples/spring-buggy --skip-ocr

echo "==> [2/3] 评测金标准召回"
python3 eval/run_eval.py

echo "==> [3/3] 启动演示页 http://127.0.0.1:5193/"
cd web
exec python3 -m http.server 5193
