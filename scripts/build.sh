#!/bin/bash
# 依赖安装 + 生产构建（走 npmmirror；本机代理不稳，失败即重试）
set -euo pipefail
cd "$(dirname "$0")/.."
for i in 1 2 3; do
  echo "=== install attempt $i ==="
  if npm install --no-audit --no-fund --loglevel=error; then break; fi
  [ "$i" = 3 ] && exit 1
  sleep 5
done
echo "=== build ==="
npm run build
echo "=== dist ==="
ls -1 dist dist/assets 2>/dev/null | head -30
