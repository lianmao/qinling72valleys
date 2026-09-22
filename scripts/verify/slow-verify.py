#!/usr/bin/env python3
"""公开检索复核（慢速版，可断点续跑）。

为什么慢：本次实测各公开通道的反爬阈值都很低 ——
  搜狗 curl 约 5 次后 302 → /antispider/；360 curl 约十几次后返回无结果页，headless 浏览器直接进验证页；
  必应 RSS 忽略检索式（会给出假信号）；必应 HTML 返回无关页面；百度/点评/小红书/马蜂窝 反爬。
所以把节奏放到接近人手的频率（默认 50s/条），用时间换有效结论。

用法：
  python3 scripts/verify/gen-entities.py entities /tmp/qinling-entities.json
  python3 scripts/verify/slow-verify.py /tmp/qinling-entities.json /tmp/qinling-verified.json [秒/条]

判据：检索式 = 实体全名 + 属地词；只看 SERP 标题是否含完整名称。
  found_local 命中且属地词相符 / found_foreign 仅命中外省同名 / not_found 无命中 / blocked 通道被拦
结果逐条落盘，中断后重跑会跳过已完成的条目。
"""
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Tuple

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TAG = re.compile(r"<[^>]+>")
H3 = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
NOISE = re.compile(r"其他人还搜|搜狗图片|相关搜索|^在.{2,8}(市|省)?搜索|360地图")
BLOCKED = ("antispider", "安全验证", "请输入验证码", "异常流量")
LOCAL = ("西安", "长安", "秦岭", "蓝田", "鄠邑", "户县", "周至", "华阴", "渭南", "眉县", "潼关", "华州",
         "临渭", "辋川", "涝峪", "大峪", "沣峪", "子午", "太平峪", "高冠", "太乙", "沙窝", "黑山岔",
         "清峪", "汤峪", "陕西", "石砭峪", "祥峪", "终南")
FOREIGN = ("河南", "北京", "河北", "四川", "云南", "山西", "浙江", "广东", "山东", "湖南", "湖北", "安徽",
           "福建", "江西", "辽宁", "吉林", "甘肃", "新疆", "青海", "江苏", "重庆", "贵州")

JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(JAR))


def fetch(query: str, attempt: int = 4) -> Tuple[List[str], str]:
    url = "https://www.sogou.com/web?query=" + urllib.parse.quote(query)
    status = "error"
    for i in range(attempt):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9", "Referer": "https://www.sogou.com/"})
            with OPENER.open(req, timeout=25) as r:
                body = r.read().decode("utf-8", "ignore")
            if any(k in body for k in BLOCKED) or len(body) < 50000:
                status = "blocked"
                wait = 180 + i * 120
                print(f"   ⛔ 被拦，退避 {wait}s …", flush=True)
                time.sleep(wait)
                continue
            titles = [html.unescape(TAG.sub("", t)).replace("\r", " ").replace("\n", " ").strip()
                      for t in H3.findall(body)]
            titles = [t for t in titles if t and not NOISE.search(t)]
            if len(titles) < 5:
                status = "blocked"
                time.sleep(120)
                continue
            return titles, "ok"
        except Exception as e:
            status = f"error:{type(e).__name__}"
            time.sleep(30)
    return [], status


def verdict(name: str, titles: List[str]) -> Tuple[str, List[str]]:
    core = re.sub(r"[（(].*?[)）]", "", name).strip()
    hits = [t for t in titles if core in t]
    if not hits:
        return "not_found", []
    if any(any(k in t for k in LOCAL) for t in hits):
        return "found_local", hits[:3]
    if any(any(k in t for k in FOREIGN) for t in hits):
        return "found_foreign", hits[:3]
    return "found_ambiguous", hits[:3]


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    pace = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0
    entities = json.loads(Path(src).read_text(encoding="utf-8"))
    results = json.loads(Path(dst).read_text(encoding="utf-8")) if Path(dst).exists() else []
    todo = [e for e in entities if e["name"] not in {r["name"] for r in results}]
    print(f"待复核 {len(todo)} 条，节奏 {pace}s/条 ≈ {len(todo) * pace / 60:.0f} 分钟", flush=True)

    for i, e in enumerate(todo, 1):
        core = re.sub(r"[（(].*?[)）]", "", e["name"]).strip()
        query = f"{core} {e.get('region', '秦岭')}"
        titles, status = fetch(query)
        v, hits = ("blocked", []) if status != "ok" else verdict(e["name"], titles)
        results.append({"group": e["group"], "valley": e.get("valley", ""), "name": e["name"],
                        "query": query, "verdict": v, "matched_titles": hits, "n_titles": len(titles)})
        Path(dst).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{i}/{len(todo)}] {v:<14} {e['name']:<30} {hits[0][:40] if hits else ''}", flush=True)
        time.sleep(pace)

    for g in sorted({r["group"] for r in results}):
        rows = [r for r in results if r["group"] == g]
        print(f"  {g:<6}", {v: sum(1 for r in rows if r["verdict"] == v) for v in {r["verdict"] for r in rows}})
    print(f"→ {dst}\n下一步：python3 scripts/verify/tag-provenance.py {dst}")


if __name__ == "__main__":
    main()
