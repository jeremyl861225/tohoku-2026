#!/usr/bin/env python3
"""把 src/map/map.svg 重新嵌回 src/roadbook.html。

roadbook.html 是「原始檔」而不是產生物，地圖 SVG 直接內嵌在裡面。
只要改了 makemap.py，就跑這支把新地圖換進去，避免手動貼上出錯。
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = ROOT / "src/roadbook.html"
SVG = ROOT / "src/map/map.svg"

PAT = re.compile(r'<svg class="map".*?</svg>', re.S)


def main() -> None:
    html = TARGET.read_text(encoding="utf-8")
    svg = SVG.read_text(encoding="utf-8").strip()
    new, n = PAT.subn(lambda _: svg, html, count=1)
    if n != 1:
        raise SystemExit(f"在 {TARGET.name} 中找到 {n} 個 <svg class=\"map\">，預期 1 個")
    TARGET.write_text(new, encoding="utf-8")
    print(f"  ✓ 已更新 {TARGET.relative_to(ROOT)} 內嵌的地圖")


if __name__ == "__main__":
    main()
