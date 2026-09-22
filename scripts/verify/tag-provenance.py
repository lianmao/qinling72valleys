#!/usr/bin/env python3
"""给 public/data/top10_details.json 打两类标签（可重复执行）：

1) provenance —— prd_listed（名称字面出现在**用户交付的原始 PRD**）| derived（文档只有描述，名称由本站归纳）
   基线固定取首个提交 7d6f898:PRD.md，不用当前工作副本：否则后来往 PRD 里补的示例会把自己的推断"洗"成文档来源。
2) verify —— 合并公开检索结果（slow-verify.py 的输出），供界面分档显示（公开可查 / 折叠待核实）。

用法：python3 scripts/verify/tag-provenance.py [/tmp/qinling-verified.json]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
F = ROOT / "public/data/top10_details.json"
BASELINE = "7d6f898"  # 用户交付的原始文档所在提交


def show(path: str) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASELINE}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


SRC = show("PRD.md") + show("geministudy.md")

d = json.loads(F.read_text(encoding="utf-8"))
verify = {}
if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
    for r in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")):
        verify[r["name"]] = {"status": r["verdict"], "checked_by": "public_serp",
                             "query": r["query"], "evidence": r.get("matched_titles", [])[:2]}

n_prd = n_derived = 0


def tag(item: dict) -> None:
    global n_prd, n_derived
    if item["name"] in SRC:
        item["provenance"] = "prd_listed"
        n_prd += 1
    else:
        item["provenance"] = "derived"
        n_derived += 1


for v in d["valleys"].values():
    for s in v["agritainment"]:
        tag(s)
        s["verify"] = verify.get(s["name"])
    for group in ("campsites", "family_spots", "photo_spots"):
        for s in v["around"][group]:
            tag(s)
            s["verify"] = verify.get(s["name"])

d["meta"]["provenance_legend"] = {
    "prd_listed": "名称字面出现在需求文档（PRD §4.1）中",
    "derived": "需求文档只有描述性文字，名称由本站归纳整理",
}
d["meta"]["verify_legend"] = {
    "found_local": "公开检索命中且属地相符",
    "found_foreign": "仅命中外省同名实体",
    "not_found": "公开渠道未检索到",
    "blocked": "检索通道被拦，未判定",
}
F.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"provenance: prd_listed={n_prd} derived={n_derived}；verify 合并 {len(verify)} 条")
