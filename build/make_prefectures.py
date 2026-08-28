#!/usr/bin/env python3
"""從公開的日本行政區 GeoJSON 產生 src/map/prefectures.json（宮城・山形・福島）。

平常不需要跑——產出物已進版控。只有要換視野範圍或加縣時才需要。

資料來源：https://github.com/dataofjapan/land（japan.geojson，約 12 MB）
用 Douglas-Peucker 簡化到約 400 m 誤差，並丟掉極小離島，
結果約 18 KB，可以安心進版控。

用法：
    curl -L -o /tmp/japan.geojson \\
      https://raw.githubusercontent.com/dataofjapan/land/master/japan.geojson
    python3 build/make_prefectures.py /tmp/japan.geojson
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WANT = {"宮城県": "miyagi", "山形県": "yamagata", "福島県": "fukushima"}
EPS = 0.004          # 約 400 m，路線圖尺度下看不出差別
MIN_RING_PTS = 6
MIN_ISLAND_DEG = 0.02


def _perp(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def simplify(pts, eps):
    """Douglas-Peucker。"""
    if len(pts) < 3:
        return pts
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = _perp(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return simplify(pts[:idx + 1], eps)[:-1] + simplify(pts[idx:], eps)
    return [pts[0], pts[-1]]


def main(src_path):
    data = json.loads(pathlib.Path(src_path).read_text(encoding="utf-8"))
    out = {}
    for f in data["features"]:
        ja = f["properties"].get("nam_ja")
        if ja not in WANT:
            continue
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = []
        for poly in polys:
            outer = [tuple(c[:2]) for c in poly[0]]
            lons = [c[0] for c in outer]
            lats = [c[1] for c in outer]
            # 丟掉極小離島（會變成畫面上的雜點）
            if (max(lons) - min(lons)) < MIN_ISLAND_DEG and \
               (max(lats) - min(lats)) < MIN_ISLAND_DEG:
                continue
            s = simplify(outer, EPS)
            if len(s) >= MIN_RING_PTS:
                rings.append([[round(x, 4), round(y, 4)] for x, y in s])
        out[WANT[ja]] = rings
        print(f"  {ja}: {len(polys)} 個多邊形 → 保留 {len(rings)}，"
              f"點數 {sum(len(r) for r in rings)}")

    dst = ROOT / "src/map/prefectures.json"
    dst.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"  ✓ {dst.relative_to(ROOT)}　{dst.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
