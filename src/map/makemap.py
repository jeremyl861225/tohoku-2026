#!/usr/bin/env python3
"""以離線 GSHHS 海岸線資料產生東北大環線路線圖 SVG。"""
import math
from mpl_toolkits.basemap import Basemap

# ── 視野範圍 ─────────────────────────────────────────
LAT0, LAT1 = 37.98, 41.38
LON0, LON1 = 139.15, 142.15
W = 396.0                      # SVG 寬度(px)
PAD = 0                        # 邊界留白

def mercy(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

MY0, MY1 = mercy(LAT0), mercy(LAT1)
MX0, MX1 = math.radians(LON0), math.radians(LON1)
SCALE = W / (MX1 - MX0)
H = (MY1 - MY0) * SCALE

def prj(lon, lat):
    x = (math.radians(lon) - MX0) * SCALE
    y = (MY1 - mercy(lat)) * SCALE
    return x, y

def path_from(xs, ys, close=True):
    pts = []
    last = None
    for lon, lat in zip(xs, ys):
        x, y = prj(lon, lat)
        if last and abs(x - last[0]) < 0.35 and abs(y - last[1]) < 0.35:
            continue
        pts.append(f"{x:.1f},{y:.1f}")
        last = (x, y)
    if len(pts) < 3:
        return None
    return "M" + "L".join(pts) + ("Z" if close else "")

# ── 海岸線與湖泊 ─────────────────────────────────────
m = Basemap(projection='cyl', llcrnrlat=LAT0 - .4, urcrnrlat=LAT1 + .4,
            llcrnrlon=LON0 - .4, urcrnrlon=LON1 + .4, resolution='h')
land, lakes = [], []
for (xs, ys), t in zip(m.coastpolygons, m.coastpolygontypes):
    d = path_from(xs, ys)
    if not d:
        continue
    (lakes if t == 2 else land).append(d)

# ── 路線 ─────────────────────────────────────────────
OUT = [  # 去程 D1–D5（含道路走廊塑形點）
    (140.917, 38.140), (141.010, 38.290), (141.060, 38.372),
    (141.150, 38.600), (141.130, 38.850), (141.099, 38.993),
    (141.110, 39.280), (140.900, 39.300), (140.550, 39.310),
    (140.480, 39.450), (140.560, 39.594), (140.670, 39.710),
    (140.790, 39.790), (140.670, 39.710), (140.560, 39.594),
    (140.800, 39.660), (141.150, 39.700), (141.050, 40.000),
    (140.860, 40.190), (140.889, 40.464), (140.960, 40.550),
    (140.858, 40.654), (140.700, 40.660), (140.590, 40.640),
    (140.464, 40.603), (140.320, 40.720), (140.204, 40.779),
    (140.100, 40.667), (139.919, 40.647), (139.907, 40.573),
    (139.926, 40.413), (140.030, 40.210), (140.103, 39.720),
]
BACK = [  # 回程 D6
    (140.103, 39.720), (140.480, 39.450), (140.550, 39.310),
    (141.110, 39.280), (141.130, 38.930), (140.960, 38.570),
    (140.870, 38.270), (140.917, 38.140),
]

def poly(pts):
    return "M" + "L".join("%.1f,%.1f" % prj(lo, la) for lo, la in pts)

# ── 標記點 ───────────────────────────────────────────
# name, lon, lat, kind(term/stay/stop), badge, anchor, dx, dy
PTS = [
    ("仙台空港", 140.917, 38.140, "term", "",   "start",  9,  4),
    ("松島",     141.060, 38.372, "stay", "1",  "start",  9,  4),
    ("平泉",     141.099, 38.993, "stop", "",   "start",  9,  4),
    ("角館",     140.562, 39.594, "stop", "",   "end",   -9,  4),
    ("田澤湖",   140.670, 39.710, "stop", "",   "end",   -9, -3),
    ("乳頭溫泉", 140.790, 39.790, "stay", "2",  "start",  9,  1),
    ("十和田湖", 140.889, 40.464, "stay", "3",  "end",   -9,  4),
    ("奧入瀨",   140.960, 40.550, "stop", "",   "start",  9,  3),
    ("八甲田",   140.858, 40.654, "stop", "",   "start",  8, -5),
    ("弘前",     140.464, 40.603, "stay", "4",  "end",   -9,  4),
    ("千疊敷",   140.100, 40.667, "stop", "",   "end",   -9, -2),
    ("深浦",     139.907, 40.573, "stop", "",   "end",   -9,  4),
    ("十二湖",   139.926, 40.413, "stop", "",   "end",   -9,  4),
    ("秋田市",   140.103, 39.720, "stay", "5",  "end",   -9,  4),
]
PREF = [("青森縣", 140.95, 41.02), ("秋田縣", 140.33, 39.33),
        ("岩手縣", 141.48, 39.55), ("宮城縣", 140.62, 38.63)]

# ── 比例尺（50 km）────────────────────────────────────
km50_deg = 50.0 / 111.32 / math.cos(math.radians(39.7))
x0, y0 = prj(LON0 + 0.18, LAT0 + 0.16)
x1, _ = prj(LON0 + 0.18 + km50_deg, LAT0 + 0.16)
bar = x1 - x0

s = []
a = s.append
a(f'<svg class="map" viewBox="0 0 {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg" '
  f'role="img" aria-label="東北大環線路線圖">')
a('<rect x="0" y="0" width="%.0f" height="%.0f" class="m-sea"/>' % (W, H))
a('<g class="m-land">')
for d in land:
    a(f'<path d="{d}"/>')
a('</g><g class="m-lake">')
for d in lakes:
    a(f'<path d="{d}"/>')
a('</g>')
for nm, lo, la in PREF:
    x, y = prj(lo, la)
    a(f'<text class="m-pref" x="{x:.1f}" y="{y:.1f}">{nm}</text>')
a(f'<path class="m-route-case" d="{poly(OUT)}"/>')
a(f'<path class="m-route" d="{poly(OUT)}"/>')
a(f'<path class="m-route-case" d="{poly(BACK)}"/>')
a(f'<path class="m-back" d="{poly(BACK)}"/>')
for nm, lo, la, kind, badge, anc, dx, dy in PTS:
    x, y = prj(lo, la)
    if kind == "stay":
        a(f'<circle class="m-dot-stay" cx="{x:.1f}" cy="{y:.1f}" r="7.5"/>')
        a(f'<text class="m-badge" x="{x:.1f}" y="{y + 2.9:.1f}">{badge}</text>')
    elif kind == "term":
        a(f'<circle class="m-dot-term" cx="{x:.1f}" cy="{y:.1f}" r="6"/>')
        a(f'<circle class="m-dot-term-in" cx="{x:.1f}" cy="{y:.1f}" r="2.4"/>')
    else:
        a(f'<circle class="m-dot" cx="{x:.1f}" cy="{y:.1f}" r="4"/>')
    cls = "m-lbl" + (" strong" if kind in ("stay", "term") else "")
    a(f'<text class="{cls}" x="{x + dx:.1f}" y="{y + dy:.1f}" '
      f'text-anchor="{anc}">{nm}</text>')
# 比例尺
a(f'<g class="m-scale"><line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0 + bar:.1f}" y2="{y0:.1f}"/>'
  f'<line x1="{x0:.1f}" y1="{y0 - 3:.1f}" x2="{x0:.1f}" y2="{y0 + 3:.1f}"/>'
  f'<line x1="{x0 + bar:.1f}" y1="{y0 - 3:.1f}" x2="{x0 + bar:.1f}" y2="{y0 + 3:.1f}"/>'
  f'<text x="{x0 + bar / 2:.1f}" y="{y0 - 6:.1f}">50 km</text></g>')
# 指北針
nx, ny = W - 26, 26
a(f'<g class="m-north"><path d="M{nx},{ny - 13} L{nx + 5},{ny + 5} L{nx},{ny + 1} '
  f'L{nx - 5},{ny + 5} Z"/><text x="{nx}" y="{ny + 17}">N</text></g>')
a('</svg>')

svg = "\n".join(s)
open("map.svg", "w", encoding="utf-8").write(svg)
print(f"SVG {W:.0f}x{H:.0f}  land={len(land)} lakes={len(lakes)}  bytes={len(svg)}")
