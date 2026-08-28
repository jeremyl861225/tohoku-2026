#!/usr/bin/env python3
"""組合互動式景點指南：樣板 + 景點資料 + 互動版地圖 SVG → dist/guide.html

樣板 src/guide_shell.html 內有兩個佔位符：
    <!--MAP-->    →  src/map/map_i.svg 的完整內容
    //--DATA--    →  src/guide_data.js 的完整內容
產出是單一自足檔案，沒有任何外部 script / css / img 依賴。
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def build() -> pathlib.Path:
    shell = (ROOT / "src/guide_shell.html").read_text(encoding="utf-8")
    data = (ROOT / "src/guide_data.js").read_text(encoding="utf-8")
    svg = (ROOT / "src/map/map_i.svg").read_text(encoding="utf-8")

    for token in ("<!--MAP-->", "//--DATA--"):
        if token not in shell:
            raise SystemExit(f"樣板缺少佔位符 {token}")

    out = shell.replace("<!--MAP-->", svg).replace("//--DATA--", data)
    dst = ROOT / "dist/guide.html"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"  ✓ {dst.relative_to(ROOT)}　{len(out) // 1024} KB")
    return dst


if __name__ == "__main__":
    build()
