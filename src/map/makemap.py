#!/usr/bin/env python3
"""產生南東北環線路線圖 SVG（靜態 map.svg ＋ 互動 map_i.svg）。

邊界資料來自 prefectures.json（宮城・山形・福島三縣，已用 Douglas-Peucker
簡化到約 400 m 誤差）。**不需要 basemap／matplotlib／numpy**——舊版靠 GSHHS
離線海岸線，在新版 Python 上裝不起來，改成純 Python 讀 GeoJSON 自行投影。

要重新產生 prefectures.json，見 build/make_prefectures.py。
"""
import json
import math
import re
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

# ── 視野範圍（涵蓋三縣，略裁去福島最南與山形庄内外海）──────────
LAT0, LAT1 = 37.00, 39.00
LON0, LON1 = 139.20, 141.70
W = 396.0


def mercy(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


MY0, MY1 = mercy(LAT0), mercy(LAT1)
MX0, MX1 = math.radians(LON0), math.radians(LON1)
SCALE = W / (MX1 - MX0)
H = (MY1 - MY0) * SCALE


def prj(lon, lat):
    return (math.radians(lon) - MX0) * SCALE, (MY1 - mercy(lat)) * SCALE


def ring_path(ring):
    pts, last = [], None
    for lon, lat in ring:
        x, y = prj(lon, lat)
        if last and abs(x - last[0]) < 0.3 and abs(y - last[1]) < 0.3:
            continue
        pts.append(f"{x:.1f},{y:.1f}")
        last = (x, y)
    return ("M" + "L".join(pts) + "Z") if len(pts) >= 3 else None


def line_path(pts):
    return "M" + "L".join("%.1f,%.1f" % prj(lo, la) for lo, la in pts)


# ── 路線（含道路走廊塑形點，讓線貼著實際走法而不是直線）──────
ROUTE = [
    (140.917, 38.140),                       # 仙台空港
    (140.890, 38.200), (140.882, 38.260),    # → 仙台
    (140.960, 38.320), (141.060, 38.372),    # → 松島（利府）
    (140.980, 38.480), (140.955, 38.573),    # → 古川
    (140.830, 38.700), (140.716, 38.743),    # → 鳴子温泉
    (140.691, 38.729),                       # 鳴子峡
    (140.600, 38.660), (140.531, 38.571),    # → 銀山温泉（R47→尾花沢）
    (140.480, 38.470), (140.435, 38.313),    # → 山寺（東根・天童）
    (140.340, 38.180), (140.230, 38.010),
    (140.104, 37.909),                       # 米沢（上杉神社）
    (140.020, 37.760), (139.960, 37.600),
    (139.930, 37.488),                       # 会津若松（鶴ヶ城）
    (140.005, 37.560), (140.048, 37.614),    # → 磐梯山ゴールドライン（山湖台）
    (140.064, 37.652), (140.088, 37.652),    # → 桧原湖・五色沼
    (140.148, 37.671),                       # 中津川渓谷（磐梯吾妻レークライン）
    (140.205, 37.690), (140.255, 37.723),    # → 浄土平（磐梯吾妻スカイライン）
    (140.400, 37.760), (140.470, 37.790),    # → 福島（土湯峠・R115）
    (140.560, 37.910), (140.617, 38.003),    # → 白石（東北自動車道）
    (140.531, 38.112),                       # 遠刈田温泉
    (140.448, 38.128),                       # 蔵王御釜（折返支線）
    (140.531, 38.112), (140.640, 38.070),
    (140.800, 38.100), (140.917, 38.140),    # → 仙台空港
]

# name, lon, lat, kind(term/stay/stop), badge, anchor, dx, dy, spot-id
PTS = [
    ("仙台空港",   140.917, 38.140, "term", "",  "start",  9,  4, "sendai-ap"),
    ("仙台",       140.882, 38.260, "stay", "1", "end",   -9,  4, "zuihoden"),
    ("松島",       141.060, 38.372, "stop", "",  "start",  9,  4, "zuiganji"),
    ("鳴子溫泉",   140.716, 38.743, "stay", "2", "start",  9,  4, "naruko-onsen"),
    ("銀山溫泉",   140.531, 38.571, "stay", "3", "end",   -9,  3, "ginzan-onsen"),
    ("山寺",       140.435, 38.313, "stop", "",  "end",   -9,  4, "yamadera"),
    ("米澤",       140.104, 37.909, "stop", "",  "end",   -9,  4, "uesugi"),
    ("會津若松",   139.930, 37.488, "stay", "4", "start",  9,  4, "tsurugajo"),
    ("五色沼",     140.088, 37.652, "stop", "",  "end",   -9, -5, "goshikinuma"),
    ("淨土平",     140.255, 37.723, "stop", "",  "start",  9,  4, "jododaira"),
    ("遠刈田溫泉", 140.531, 38.112, "stay", "5", "start",  9,  9, "togatta-onsen"),
    ("藏王御釜",   140.4496, 38.1362, "stop", "",  "end",  -10, -6, "okama"),
]

PREF = [("宮城縣", 141.20, 38.62), ("山形縣", 139.95, 38.65), ("福島縣", 140.75, 37.35)]



# ── 從 guide_data.js 讀景點（避免地圖與資料分歧）───────────────
def load_spots():
    src = (HERE.parent / "guide_data.js").read_text(encoding="utf-8")
    out = []
    for b in re.findall(r"\{(?:[^{}]|\{[^{}]*\}|\[[^\]]*\])*?\}", src, re.S):
        gid = re.search(r'\bid:"([^"]+)"', b)
        day = re.search(r"\bday:\s*(\d+)", b)
        lat = re.search(r"\blat:\s*(-?[\d.]+)", b)
        lng = re.search(r"\blng:\s*(-?[\d.]+)", b)
        tim = re.search(r'\btime:"([^"]*)"', b)
        nam = re.search(r'\bname:"([^"]*)"', b)
        if not (gid and day and lat and lng):
            continue
        out.append(dict(id=gid.group(1), day=int(day.group(1)),
                        lat=float(lat.group(1)), lng=float(lng.group(1)),
                        time=tim.group(1) if tim else "",
                        name=nam.group(1) if nam else "",
                        nomap=("nomap:true" in b)))
    out.sort(key=lambda x: (x["day"], x["time"]))
    return out


def day_groups(a):
    """每日一個 <g>：當天路線 + 帶編號的標記；同時回傳每日的 viewBox。"""
    spots = load_spots()
    boxes = {}
    for d in range(1, 7):
        allday = [x for x in spots if x["day"] == d]
        pts = [x for x in allday if not x["nomap"]]
        if not pts:
            continue
        a(f'<g class="m-day" data-day="{d}">')
        if len(pts) > 1:
            dd = "M" + "L".join("%.1f,%.1f" % prj(x["lng"], x["lat"]) for x in pts)
            a(f'<path class="m-route-case" data-day="{d}" vector-effect="non-scaling-stroke" d="{dd}"/>')
            a(f'<path class="m-route" data-day="{d}" vector-effect="non-scaling-stroke" d="{dd}"/>')
        xs, ys = [], []
        for i, x in enumerate(allday):          # 編號含晚餐卡，與行程卡一致
            if x["nomap"]:
                continue
            px, py = prj(x["lng"], x["lat"])
            xs.append(px); ys.append(py)
            # 子元素用相對座標，外層 translate；縮放時 JS 會補上 scale(1/k)
            # 讓標記與標籤在任何縮放下都維持固定的螢幕尺寸
            a(f'<g class="m-pin m-mk" data-id="{x["id"]}" data-day="{d}" data-x="{px:.1f}" data-y="{py:.1f}" '
              f'transform="translate({px:.1f},{py:.1f})" tabindex="0" role="button" aria-label="{x["name"]}">')
            a('<circle class="m-hit" cx="0" cy="0" r="15"/>')
            a('<circle class="m-dot-seq" cx="0" cy="0" r="8"/>')
            a(f'<text class="m-num m-seq" x="0" y="3.1">{i + 1}</text>')
            a(f'<text class="m-lbl strong" x="11" y="4" text-anchor="start">{x["name"]}</text>')
            a("</g>")
        a("</g>")
        pad = 34
        x0, x1 = min(xs) - pad, max(xs) + pad
        y0, y1 = min(ys) - pad, max(ys) + pad
        # 維持與整體圖相同的長寬比，避免變形
        ar = H / W
        w, h = x1 - x0, y1 - y0
        if h / w < ar:
            nh = w * ar; y0 -= (nh - h) / 2; h = nh
        else:
            nw = h / ar; x0 -= (nw - w) / 2; w = nw
        boxes[d] = [round(x0, 1), round(y0, 1), round(w, 1), round(h, 1)]
    return boxes


def build(interactive):
    pref = json.loads((HERE / "prefectures.json").read_text(encoding="utf-8"))
    s = []
    a = s.append
    label = "南東北環線路線圖"
    box_holder = []
    a('<<<SVGOPEN>>>')
    a(f'<rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" class="m-sea"/>')
    a('<g class="m-land">')
    for rings in pref.values():
        for r in rings:
            d = ring_path(r)
            if d:
                a(f'<path vector-effect="non-scaling-stroke" d="{d}"/>')
    a('</g>')
    for nm, lo, la in PREF:
        x, y = prj(lo, la)
        a(f'<text class="m-pref" x="{x:.1f}" y="{y:.1f}">{nm}</text>')
    a('<g class="m-all">')
    a(f'<path class="m-route-case" d="{line_path(ROUTE)}"/>')
    a(f'<path class="m-route" d="{line_path(ROUTE)}"/>')

    for nm, lo, la, kind, badge, anc, dx, dy, sid in PTS:
        x, y = prj(lo, la)
        if interactive:
            a(f'<g class="m-pin" data-id="{sid}" tabindex="0" role="button" aria-label="{nm}">')
            a(f'<circle class="m-hit" cx="{x:.1f}" cy="{y:.1f}" r="15"/>')
        else:
            a('<g>')
        if kind == "stay":
            a(f'<circle class="m-dot-stay" cx="{x:.1f}" cy="{y:.1f}" r="7.5"/>')
            a(f'<text class="m-badge" x="{x:.1f}" y="{y + 2.9:.1f}">{badge}</text>')
        elif kind == "term":
            a(f'<circle class="m-dot-term" cx="{x:.1f}" cy="{y:.1f}" r="6"/>')
            a(f'<circle class="m-dot-term-in" cx="{x:.1f}" cy="{y:.1f}" r="2.4"/>')
        else:
            a(f'<circle class="m-dot" cx="{x:.1f}" cy="{y:.1f}" r="4"/>')
        cls = "m-lbl" + (" strong" if kind in ("stay", "term") else "")
        a(f'<text class="{cls}" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anc}">{nm}</text>')
        a('</g>')

    a('</g>')                       # /m-all
    if interactive:
        box_holder.append(day_groups(a))

    # 比例尺 50 km
    km = 50.0 / 111.32 / math.cos(math.radians(38.0))
    x0, y0 = prj(LON0 + 0.16, LAT0 + 0.14)
    x1, _ = prj(LON0 + 0.16 + km, LAT0 + 0.14)
    bar = x1 - x0
    a(f'<g class="m-scale"><line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0 + bar:.1f}" y2="{y0:.1f}"/>'
      f'<line x1="{x0:.1f}" y1="{y0 - 3:.1f}" x2="{x0:.1f}" y2="{y0 + 3:.1f}"/>'
      f'<line x1="{x0 + bar:.1f}" y1="{y0 - 3:.1f}" x2="{x0 + bar:.1f}" y2="{y0 + 3:.1f}"/>'
      f'<text x="{x0 + bar / 2:.1f}" y="{y0 - 6:.1f}">50 km</text></g>')
    # 指北針
    nx, ny = W - 26, 26
    a(f'<g class="m-north"><path d="M{nx},{ny - 13} L{nx + 5},{ny + 5} L{nx},{ny + 1} '
      f'L{nx - 5},{ny + 5} Z"/><text x="{nx}" y="{ny + 17}">N</text></g>')
    a('</svg>')
    dbox = json.dumps(box_holder[0], separators=(",", ":")) if box_holder else "{}"
    open_tag = (f'<svg class="map" viewBox="0 0 {W:.0f} {H:.0f}" '
                f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}" '
                f"data-full=\"0 0 {W:.0f} {H:.0f}\" data-daybox='{dbox}'>")
    return "\n".join(s).replace('<<<SVGOPEN>>>', open_tag)


if __name__ == "__main__":
    for name, inter in (("map.svg", False), ("map_i.svg", True)):
        svg = build(inter)
        (HERE / name).write_text(svg, encoding="utf-8")
        print(f"  ✓ src/map/{name}　{W:.0f}x{H:.0f}　{len(svg) // 1024} KB")
