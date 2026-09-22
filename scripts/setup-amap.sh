#!/bin/bash
# 配置高德 Key：写本地 .env.local + （网络可用时）写入 GitHub Actions Secrets
#
#   bash scripts/setup-amap.sh <JS_API_KEY> <JSCode>
#
# 幂等：重复执行覆盖旧值。Key 不进 git（.env.local 已忽略）。
set -euo pipefail
cd "$(dirname "$0")/.."

KEY=${1:-}
SEC=${2:-}
[ -n "$KEY" ] || { echo "用法: bash scripts/setup-amap.sh <JS_API_KEY> <JSCode>"; exit 2; }

umask 077
printf 'VITE_AMAP_KEY=%s\nVITE_AMAP_SECURITY=%s\n' "$KEY" "$SEC" > .env.local
echo "已写入 .env.local (key ${#KEY} 字符, jscode ${#SEC} 字符)"
grep -q '^\.env' .gitignore && echo "确认 .env* 已被忽略: $(git check-ignore -v .env.local | head -1)"

export PATH="$HOME/.local/bin:$PATH"
if gh repo view lianmao/qinling72valleys >/dev/null 2>&1; then
  printf '%s' "$KEY" | gh secret set AMAP_JS_KEY --repo lianmao/qinling72valleys >/dev/null && echo "GitHub Secret AMAP_JS_KEY 已设置"
  if [ -n "$SEC" ]; then
    printf '%s' "$SEC" | gh secret set AMAP_SECURITY_CODE --repo lianmao/qinling72valleys >/dev/null && echo "GitHub Secret AMAP_SECURITY_CODE 已设置"
  fi
  gh secret list --repo lianmao/qinling72valleys
else
  echo "! GitHub 不可达，Secrets 未设置 —— 恢复网络后重跑本脚本即可"
fi
