#!/usr/bin/env python3
"""从 PRD.md 第 3 节名录表生成 public/data/valleys.json。

单一数据源：PRD 是名录正本，本脚本只做解析，不做事实校对。
每条数据都携带 source / confidence —— 当前 PRD 名录为未核实初稿，
坐标为等步长近似值，禁止直接用于导航（见 README 数据可信度声明）。

用法：python3 scripts/gen-valleys.py
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRD = ROOT / "PRD.md"
OUT = ROOT / "public" / "data" / "valleys.json"

ROW = re.compile(
    r"^\|\s*(?P<idx>\d+)\s*\|\s*\*{0,2}(?P<name>[^|*]+?)\*{0,2}\s*\|"
    r"\s*(?P<region>[^|]+?)\s*\|\s*(?P<lng>\d{2,3}\.\d+)\s*,\s*(?P<lat>\d{2}\.\d+)\s*\|"
    r"\s*(?P<summary>[^|]*?)\s*\|\s*(?P<mark>[^|]*?)\s*\|\s*$"
)
RANK = re.compile(r"第\s*(\d+)\s*峪")
CITY = re.compile(r"^(西安|宝鸡|渭南)市?")


def parse_region(raw: str) -> tuple[str, str, bool]:
    """'渭南市潼关县' -> ('渭南市', '潼关县', False)；跨县条目置 needs_review。"""
    raw = raw.strip()
    m = CITY.match(raw)
    if m:
        city, rest = f"{m.group(1)}市", raw[m.end():].strip()
    else:
        city, rest = "待定", raw
    review = "/" in rest or rest.startswith("市")
    return city, rest.replace("/", "·") or "待定", review


def main() -> None:
    rows = []
    for line in PRD.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line.rstrip())
        if m:
            rows.append(m.groupdict())
    if len(rows) != 72:
        raise SystemExit(f"解析到 {len(rows)} 条名录，期望 72 —— PRD 表格结构变了，请检查")

    names: dict[str, int] = {}
    for r in rows:
        names[r["name"]] = names.get(r["name"], 0) + 1

    valleys = []
    for r in rows:
        city, district, review = parse_region(r["region"])
        mark = r["mark"].replace("*", "").strip()
        rank = RANK.search(mark)
        is_top10 = bool(rank) and "备选" not in mark
        idx = int(r["idx"])
        collisions = names[r["name"]] > 1
        valleys.append(
            {
                "id": f"VALLEY_{idx:03d}",
                "no": idx,
                "name": r["name"],
                "city": city,
                "district": district,
                "lng": float(r["lng"]),
                "lat": float(r["lat"]),
                "is_top10": is_top10,
                "top10_rank": int(rank.group(1)) if is_top10 else None,
                "difficulty": None,          # PRD 未赋值 -> 前端显示「待核实」
                "status": None,              # None=未核实(灰灯) / 1=开放(绿) / 0=管制(红)
                "status_reason": None,
                "status_updated_at": None,
                "summary": r["summary"],
                "needs_review": review or collisions,
                "review_notes": [
                    *(["重名：与同名峪口需区分"] if collisions else []),
                    *(["区县跨界/归属待核"] if review else []),
                    *(["PRD 标注为首批备选"] if "备选" in mark else []),
                ],
                "source": "PRD.md §3 名录初稿",
                "confidence": "unverified",
                "verified_at": None,
            }
        )

    top10 = sorted([v for v in valleys if v["is_top10"]], key=lambda v: v["top10_rank"])
    payload = {
        "data_version": datetime.now(timezone.utc).strftime("%Y%m%d.%H%M"),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "coordinate_system": "GCJ-02",
        "confidence": "unverified",
        "source_note": "名录与坐标来自 PRD 初稿，未经实地核对；等步长近似坐标，禁止作导航依据。",
        "counts": {
            "total": len(valleys),
            "by_city": {c: sum(1 for v in valleys if v["city"] == c)
                        for c in sorted({v["city"] for v in valleys})},
            "needs_review": sum(1 for v in valleys if v["needs_review"]),
            "top10": [v["id"] for v in top10],
        },
        "valleys": valleys,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(valleys)} 峪 / 城市 {payload['counts']['by_city']} "
          f"/ 待核 {payload['counts']['needs_review']} / Top10 {len(top10)}")


if __name__ == "__main__":
    main()
