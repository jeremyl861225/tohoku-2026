#!/usr/bin/env python3
"""把 HTML 轉成 PDF（Chromium 列印引擎，中文用系統的 Noto CJK）。

用法：
    python3 build/html2pdf.py src/roadbook.html dist/roadbook.pdf --footer
    python3 build/html2pdf.py src/quickcard.html dist/quickcard.pdf --margin 8
"""
import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright

FOOTER = """<div style="width:100%;font-size:7pt;color:#7A8D97;
  font-family:'Noto Sans CJK TC',sans-serif;padding:0 11mm;
  display:flex;justify-content:space-between;">
  <span>南東北環線 ROADBOOK · 2026.09.22–09.27</span>
  <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>"""


def render(src: pathlib.Path, out: pathlib.Path, footer: bool, margin_mm: float) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    m = f"{margin_mm}mm"
    opts = dict(
        path=str(out),
        format="A4",
        print_background=True,
        margin={"top": "12mm" if footer else m, "bottom": "15mm" if footer else m,
                "left": m, "right": m},
    )
    if footer:
        opts.update(display_header_footer=True, header_template="<div></div>",
                    footer_template=FOOTER)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(src.resolve().as_uri(), wait_until="networkidle")
        pg.emulate_media(media="print")
        pg.pdf(**opts)
        b.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=pathlib.Path)
    ap.add_argument("out", type=pathlib.Path)
    ap.add_argument("--footer", action="store_true", help="加上頁碼頁尾（roadbook 用）")
    ap.add_argument("--margin", type=float, default=11.0, help="左右邊界 mm")
    a = ap.parse_args()
    if not a.src.exists():
        print(f"找不到 {a.src}", file=sys.stderr)
        return 1
    render(a.src, a.out, a.footer, a.margin)

    try:
        from pypdf import PdfReader
        n = len(PdfReader(str(a.out)).pages)
        print(f"  ✓ {a.out}　{n} 頁")
    except Exception:
        print(f"  ✓ {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
