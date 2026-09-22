#!/usr/bin/env python3
"""生成分享卡片图 public/og.png（微信/社交平台读 og:image）。

刻意不用照片：站内暂无可授权实景图，用等高线山形占位，避免盗图与版权风险。
用法：python3 scripts/gen-og.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "og.png"
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
W, H = 1200, 630
INK, MINT, RIDGE, DIM = "#f2f7f3", "#7fd1a3", "#17452f", "#9fb8a8"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def ridgeline(d: ImageDraw.ImageDraw, base: int, peaks: list[tuple[float, float]], color: str) -> None:
    pts = [(0, H)] + [(x * W, H - base - y) for x, y in peaks] + [(W, H)]
    d.polygon(pts, fill=color)


def main() -> None:
    img = Image.new("RGB", (W, H), "#0f2a1d")
    d = ImageDraw.Draw(img)

    # 背景渐变
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(15 + 20 * t), int(42 + 60 * t), int(29 + 40 * t)))

    ridgeline(d, 0, [(0.0, 60), (0.18, 190), (0.30, 110), (0.46, 250), (0.62, 140), (0.78, 210), (1.0, 120)], RIDGE)
    ridgeline(d, -70, [(0.0, 20), (0.12, 110), (0.26, 40), (0.40, 150), (0.56, 60), (0.72, 130), (0.88, 70), (1.0, 110)], "#1d5a3c")

    d.text((72, 150), "秦岭七十二峪", font=font(104), fill=INK)
    d.text((76, 292), "露营 · 徒步 · 农家乐 · 安全状态", font=font(40), fill=MINT)
    d.text((76, 372), "渭南 / 西安 / 宝鸡 北麓七十二峪口径全收录", font=font(32), fill=DIM)
    d.text((76, 452), "区域联动筛选 · 露营配套看板 · 高德一键导航", font=font(32), fill=DIM)

    d.line([(76, 528), (420, 528)], fill=MINT, width=4)
    d.text((76, 552), "坐标与配套信息为待核实初稿，不作为导航依据", font=font(26), fill="#c8b78a")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"{OUT.relative_to(ROOT)}: {img.size[0]}x{img.size[1]} {OUT.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
