#!/bin/bash
# 网络间歇性 reset：所有 gh 调用带重试。幂等，可反复执行。
export PATH="$HOME/.local/bin:$PATH"
REPO=lianmao/qinling72valleys
retry() {  # retry <标签> <命令...>
  local label=$1; shift
  for i in $(seq 1 6); do
    if out=$("$@" 2>&1); then echo "ok   $label: $out"; return 0; fi
    case "$out" in *"already exists"*|*"409"*) echo "ok   $label: (已存在)"; return 0;; esac
    echo "  retry $i $label …"; sleep 5
  done
  echo "FAIL $label: $out"; return 1
}

retry "enable-pages" gh api -X POST "repos/$REPO/pages" -f build_type=workflow
retry "pages-info"   gh api "repos/$REPO/pages" --jq '{status,build_type,html_url}' || true
retry "dispatch"     gh workflow run deploy.yml --repo "$REPO"
sleep 8
retry "runs"         gh run list --repo "$REPO" --limit 3 --json status,conclusion,headSha,url \
                       --jq '.[] | "\(.status)/\(.conclusion) \(.headSha[0:7]) \(.url)"'
