#!/usr/bin/env python3
"""导出待复核实体清单 → /tmp 下的 entities.json（供 slow-verify.py 使用）。

用法：python3 scripts/verify/gen-entities.py [entities|valleys]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VALLEYS = json.loads((ROOT / "public/data/valleys.json").read_text(encoding="utf-8"))["valleys"]
VAL = {v["id"]: v for v in VALLEYS}
NAMES = {v["id"]: v["name"] for v in VALLEYS}
D = json.loads((ROOT / "public/data/top10_details.json").read_text(encoding="utf-8"))["valleys"]

which = sys.argv[1] if len(sys.argv) > 1 else "entities"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/qinling-entities.json")
out = []


def region_of(vid: str) -> str:
    v = VAL[vid]
    return f"{v['city'].replace('市', '')} {v['district'].split('·')[0]}"


def add(group: str, vid: str, kind: str, name: str) -> None:
    if name not in [x["name"] for x in out if x["group"] == group]:
        out.append({"group": group, "valley": NAMES.get(vid, vid), "region": region_of(vid),
                    "kind": kind, "name": name})


if which == "entities":
    for vid, det in D.items():
        for s in det["agritainment"]:
            add("农家乐", vid, "店", s["name"])
        for s in det["around"]["campsites"]:
            add("露营地", vid, "地", s["name"])
        for s in det["around"]["family_spots"]:
            add("亲子", vid, "地", s["name"])
        for s in det["around"]["photo_spots"]:
            add("打卡点", vid, "地", s["name"])
else:
    for v in VALLEYS:
        add("峪口名", v["id"], "地", f"{v['name']} 峪")

OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{OUT}: {len(out)} 条 " + str({g: sum(1 for x in out if x["group"] == g) for g in {x["group"] for x in out}}))
