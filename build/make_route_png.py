#!/usr/bin/env python3
"""把 src/map/map.svg 算成高解析度 PNG（存手機相簿用）→ dist/route-map.png

SVG 的顏色靠外部 CSS 變數，所以這裡把 roadbook.html 的地圖樣式段落抽出來
包成一個臨時頁面再截圖，確保 PNG 與 PDF 裡的地圖長得一模一樣。
"""
import pathlib
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIDTH = 1100          # CSS px，乘上 device_scale_factor 2 → 2200 px 寬


def main() -> None:
    svg = (ROOT / "src/map/map.svg").read_text(encoding="utf-8")
    css = (ROOT / "src/roadbook.html").read_text(encoding="utf-8")

    root = css[css.index(":root{"):css.index("*{box-sizing")]
    mapcss = css[css.index("/* ───────── 路線地圖 ───────── */"):
                 css.index("/* ───────── 全線圖 ───────── */")]

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{root}
body{{margin:0;padding:0;background:#fff}}
{mapcss}
.map-col{{flex:none!important;width:{WIDTH}px!important;max-width:none!important}}
svg.map{{width:{WIDTH}px!important;border:none}}
</style></head><body><div class="map-col">{svg}</div></body></html>"""

    out = ROOT / "dist/route-map.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                     encoding="utf-8") as f:
        f.write(html)
        tmp = pathlib.Path(f.name)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": WIDTH + 80, "height": 1700},
                            device_scale_factor=2)
            pg.goto(tmp.as_uri())
            pg.wait_for_timeout(300)
            pg.locator("svg.map").screenshot(path=str(out))
            b.close()
    finally:
        tmp.unlink(missing_ok=True)

    from PIL import Image
    w, h = Image.open(out).size
    print(f"  ✓ {out.relative_to(ROOT)}　{w}×{h}")


if __name__ == "__main__":
    main()
