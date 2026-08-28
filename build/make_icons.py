#!/usr/bin/env python3
"""產生 PWA 圖示：以實際路線的輪廓當標誌（深墨底＋藍色環線＋橘色進出點）。"""
import math
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAT0, LAT1, LON0, LON1 = 38.05, 40.90, 139.75, 141.30

# 與 src/map/makemap.py 相同的路線節點（去程 + 回程，構成閉環）
ROUTE = [
    (140.917, 38.140), (141.010, 38.290), (141.060, 38.372), (141.150, 38.600),
    (141.130, 38.850), (141.099, 38.993), (141.110, 39.280), (140.900, 39.300),
    (140.550, 39.310), (140.480, 39.450), (140.560, 39.594), (140.670, 39.710),
    (140.790, 39.790), (140.670, 39.710), (140.560, 39.594), (140.800, 39.660),
    (141.150, 39.700), (141.050, 40.000), (140.860, 40.190), (140.889, 40.464),
    (140.960, 40.550), (140.858, 40.654), (140.700, 40.660), (140.590, 40.640),
    (140.464, 40.603), (140.320, 40.720), (140.204, 40.779), (140.100, 40.667),
    (139.919, 40.647), (139.907, 40.573), (139.926, 40.413), (140.030, 40.210),
    (140.103, 39.720), (140.480, 39.450), (140.550, 39.310), (141.110, 39.280),
    (141.130, 38.930), (140.960, 38.570), (140.870, 38.270), (140.917, 38.140),
]
# 過夜點（白）與進出點（橘）
MARKS = [(141.060, 38.372, "#FFFFFF", .85), (140.889, 40.464, "#FFFFFF", .85),
         (140.464, 40.603, "#FFFFFF", .85), (140.103, 39.720, "#FFFFFF", .85),
         (140.917, 38.140, "#B87C1E", 1.25)]


def mercy(lat: float) -> float:
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def draw(size: int, pad_frac: float = .11, w_frac: float = .029) -> None:
    S = size * 4                       # 4× 超取樣後縮小，邊緣才乾淨
    pad, w = int(S * pad_frac), max(3, int(S * w_frac))
    my0, my1 = mercy(LAT0), mercy(LAT1)
    mx0, mx1 = math.radians(LON0), math.radians(LON1)
    sc = min((S - 2 * pad) / (mx1 - mx0), (S - 2 * pad) / (my1 - my0))
    ox = (S - (mx1 - mx0) * sc) / 2
    oy = (S - (my1 - my0) * sc) / 2

    def f(lon, lat):
        return ox + (math.radians(lon) - mx0) * sc, oy + (my1 - mercy(lat)) * sc

    im = Image.new("RGB", (S, S), "#12232E")
    d = ImageDraw.Draw(im)
    d.line([f(lo, la) for lo, la in ROUTE], fill="#1C7FC4", width=w, joint="curve")
    for lo, la, color, rf in MARKS:
        x, y = f(lo, la)
        r = w * rf
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)

    out = ROOT / f"icon-{size}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.resize((size, size), Image.LANCZOS).save(out)
    print(f"  ✓ {out.relative_to(ROOT)}")


if __name__ == "__main__":
    for s in (192, 512):
        draw(s)
