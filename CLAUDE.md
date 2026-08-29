# CLAUDE.md — 專案接手說明

給接手這個專案的 Claude Code。先讀完這份再動任何檔案。

---

## 這是什麼

Jeremy 一個人到日本南東北（宮城・山形・福島）自駕六天的行前資料包。
**機票已開票、行程已定案**，這個 repo 產出三份給他實際帶著走的文件，
以及一個裝在手機上的離線 App。

不是通用旅遊工具，是一次性的、針對這趟旅程的交付物。所有內容都以
**繁體中文**撰寫，日文地名附原文，這是硬性慣例。

> **2026-08-28 全面改版。** 初版排的是「東北大環線」（含秋田・青森、
> 1,129 km／18:39），因為四晚訂不到房、有折返與夜間駕駛而整個打掉。
> 舊內容不再保留於工作區，但完整保存在 git 歷史裡（commit `67cf937` 之前）。
> **為什麼改**見 `docs/DECISIONS.md`。

## 旅程事實（改動前務必核對）

| 項目 | 值 |
|---|---|
| 日期 | 2026/09/22（二）–09/27（日），六天五夜 |
| 旅人 | 單人（獨旅）。這影響訂房——見「一人泊」 |
| 去程 | **JX862** TPE 11:35 → SDJ 16:00　星宇 A330-900neo 經濟艙 |
| 回程 | **JX863** SDJ 17:20 → TPE 20:10。**須 15:20 前還車** |
| 範圍 | 宮城・山形・福島（不含秋田・青森・岩手） |
| 形式 | 仙台進出，**逆時針環線**，全程自駕，不走回頭路 |
| 里程 | **626 km／駕駛 12:08**（Google Maps 實測；D6 加白石城選配為 103 km／2:21） |
| 路線 | 仙台空港→仙台→松島→鳴子溫泉→銀山溫泉→山寺→米澤→會津若松→五色沼→**淨土平**→遠刈田溫泉→藏王御釜→仙台空港 |

每日路線、分段車程、住宿、餐廳見 `docs/ITINERARY.md`。
**為什麼這樣排**見 `docs/DECISIONS.md`——改行程前一定要讀。

## 交付物

| 產出 | 用途 | 來源 |
|---|---|---|
| `dist/roadbook.pdf` | 主要行程書，逐日 roadbook 形式 | `src/roadbook.html` |
| `dist/quickcard.pdf`（1 頁 A4） | 車上速查卡，夾遮陽板用 | `src/quickcard.html` |
| `dist/guide.html` | 互動式景點指南，單一自足檔案 | `src/guide_shell.html` + `src/guide_data.js` + `src/map/map_i.svg` |
| 根目錄的 `index.html` ＋ `sw.js` ＋ `manifest.webmanifest` ＋ `icon-*.png` | 上述指南的 PWA 版，加到 iPhone 主畫面、離線可用 | `dist/guide.html` 加工 |
| `dist/route-map.png` | 路線圖單張圖片，存手機相簿用 | `src/map/map.svg` |

## 目錄結構

```
tohoku-2026/
├── CLAUDE.md              ← 你正在讀的
├── README.md
├── requirements.txt
├── docs/
│   ├── ITINERARY.md       ← 行程事實：分段車程、住宿、餐廳、已查證事項
│   ├── DECISIONS.md       ← 決策紀錄：為什麼逆時針、為什麼銀山排週四
│   └── PWA.md             ← 手機版安裝與更新說明
├── src/
│   ├── roadbook.html      ← 行程書。地圖 SVG 內嵌在裡面
│   ├── quickcard.html     ← 速查卡
│   ├── guide_shell.html   ← 互動指南樣板，含 <!--MAP--> 與 //--DATA-- 佔位符
│   ├── guide_data.js      ← 30 個景點 + 6 張晚餐卡的資料陣列（內容的主要來源）
│   └── map/
│       ├── prefectures.json  ← 宮城・山形・福島縣界（已簡化，18 KB）
│       ├── makemap.py        ← 一支腳本同時產出 map.svg 與 map_i.svg
│       └── map.svg  map_i.svg   ← 產生物
├── build/
│   ├── build.sh           ← 一鍵重建全部
│   ├── make_prefectures.py   ← 從公開 GeoJSON 重新產生 prefectures.json
│   ├── make_route_png.py  ← 路線圖 PNG
│   ├── inject_map.py      ← 把 map.svg 換回 roadbook.html
│   ├── html2pdf.py        ← HTML → PDF
│   ├── build_guide.py     ← 組合互動指南
│   ├── make_icons.py      ← 產生 PWA 圖示
│   ├── build_pwa.py       ← guide.html → 根目錄 index.html
│   └── deploy.sh          ← 一鍵部署到 GitHub Pages
├── index.html  sw.js  manifest.webmanifest  icon-192.png  icon-512.png
└── dist/                  ← 全部是產生物
```

**PWA 的五個檔案刻意放在專案根目錄**，因為 GitHub Pages 的「Deploy from a
branch」只能選 `/` 或 `/docs`，放進子目錄就得另外接 Actions。這也和 Jeremy
其他幾個 app（todo-app、patient-list、book-reader）的擺法一致。

## 建置

```bash
pip install -r requirements.txt
playwright install chromium          # 只有 PDF 需要
./build/build.sh
```

只重建手機版（**不需要任何第三方套件**）：

```bash
python3 src/map/makemap.py && python3 build/build_guide.py && python3 build/build_pwa.py
```

**地圖已經不需要 basemap／matplotlib／numpy。** 舊版靠 GSHHS 離線海岸線，
在 Python 3.14 的 externally-managed 環境下整組裝不起來。現在改成讀
`src/map/prefectures.json`（從公開 GeoJSON 抽出的三縣邊界，已用 Douglas-Peucker
簡化到約 400 m 誤差）再用純 Python 做 Mercator 投影，零依賴。

**PDF 仍需要 playwright。** 若機器上沒有，`dist/*.pdf` 就無法產生——
這時候不要去改 `src/roadbook.html` 卻留著舊 PDF，那會讓 src 與 dist 不一致。

## 哪個檔案改哪裡

- **改景點內容** → 只改 `src/guide_data.js`，然後 `build_guide.py` + `build_pwa.py`。
  **注意 roadbook.html 裡有一份平行的簡述**，兩邊手動同步，這是已知技術債。
- **改每日時刻／路線** → 改 `src/roadbook.html` 的對應 `.day` 區塊，
  同時檢查 `src/quickcard.html` 的 `.days` 表與 `guide_data.js` 的 `time` 欄位。
- **改地圖** → 改 `src/map/makemap.py`（節點在 `PTS`、路線在 `ROUTE`、視野在 `LAT0/LAT1/LON0/LON1`），
  跑 `python3 src/map/makemap.py`，再跑 `build/inject_map.py` 換進 roadbook。
- **改配色／版面** → CSS 變數集中在每個 HTML 檔頂端的 `:root`，三個檔案共用同一組。

## 設計系統

三份文件共用一套視覺語言：**日本高速公路指標 ＋ 拉力賽 roadbook**。

```
--ink    #12232E   深墨，標題底色與主要文字
--aoike  #1C7FC4   青池藍，路線、停留點、主要強調
--ochre  #B87C1E   進出點、攝影提示
--exp    #0B6E4F   高速道路段（綠色指標）
--sign   #114E8C   一般道段（藍色指標）
--warn   #A33A2A   風險警示
--paper  #EFF2F1   背景
```

- 字體三分工：襯線（標題）／無襯線（內文）／等寬（時間、距離、代碼）。
  **所有數字資料一律用等寬**，車上掃視時對齊比美觀重要。
- 列印時每張日程卡 `break-inside: avoid`，不允許跨頁切開。
- **手機優先響應式**：Jeremy 主要在手機上看，窄螢幕必須改流式單欄、表格轉卡片。

## 資料模型

`src/guide_data.js` 的 `SPOTS` 陣列，每筆：

```js
{
  id: "ginzan-onsen",       // 唯一鍵，也是地圖標記的 data-id
  day: 3,                   // 1–6
  name: "銀山溫泉",          // 中文名
  jp: "銀山温泉",            // 日文原文
  romaji: "Ginzan Onsen",
  type: "溫泉・住宿",         // 決定無照片時的後備圖示，見 guide_shell.html 的 ICON 表
  stay: "住宿", time: "15:00",
  lat: 38.5706, lng: 140.5305,   // 座標顯示與地圖圖釘定位用
  gq: "銀山温泉",                 // Google 地圖查詢字串——見下面「地圖連結用 gq」
  leg: { t:"30 分", d:"31.2 km", src:"osrm" },   // 「開到這張卡」的那段路，見下面
  wiki: ["銀山温泉"],             // 日文維基條目候選，依序嘗試取照片
  desc: "…",                     // 卡片正文
  fields: [["自駕","…"], …],      // 展開後的欄位表
  tip: "…", photo: "…",           // 兩種提示條，可省略
  keys: "銀山温泉 大正浪漫 煤氣燈"  // 只給搜尋比對用的關鍵字
}
```

目前 **30 個景點 + 6 張晚餐卡、其中 12 個在地圖上有標記**（自然景觀 13 個，佔 42%）。`id` 必須與 `makemap.py` 的
`PTS` 最後一欄對得上，否則點地圖不會跳轉。收尾時用這段檢查：

```bash
python3 - <<'PY'
import re, pathlib
d = pathlib.Path("src/guide_data.js").read_text(encoding="utf-8")
m = pathlib.Path("src/map/makemap.py").read_text(encoding="utf-8")
print(set(re.findall(r',\s*"([a-z0-9-]+)"\),', m)) - set(re.findall(r'\bid:"([^"]+)"', d)) or "✓ 全部對得上")
PY
```

## `leg`＝開到這張卡的那一段路

`leg` 掛在**終點**那張卡上，不是起點。`t` 時間、`d` 距離、`src` 來源
（`google` 實測／`osrm` 估算，會顯示「約」／`walk` 步行／`same` 同區不畫）。

每天第一張卡的 `leg` 另外要帶兩個欄位，因為它前面沒有卡可以當起點：

```js
leg:{ t:"57 分", d:"49.8 km", src:"google",
      from:"銀山温泉",          // Google 路線的起點地名（住宿地）
      stay:"銀山溫泉旅館" }     // 卡上那顆徽章顯示的字
```

沒有 `from` 的話，那天第一段就不會畫出來——**這正是 2026-08-29 修掉的那個 bug**：
`render()` 在日界把 `prev` 清成 `null`，於是每天早上從飯店出發的那段路整個消失。
渲染出來的是 `.leg.leg-day`（虛線左框、`data-from="lodging"`）。
D1 沒有這一段，那天是落地後直接出發。

**這些車程本來就含在 `ITINERARY.md` 的每日總計裡**，不是額外加上去的。

**地圖標記不要放得太近。** 鳴子峽與鳴子溫泉只差 4 km，在 396 px 寬的地圖上
只差約 5 px，兩個標籤會疊在一起——所以鳴子峽只做成景點卡、不給圖釘。

## 地圖連結用 `gq`，不是座標

每筆 spot 有一個 `gq`（Google query）欄位——景點卡的「Google 地圖」按鈕用它去查地名，
點下去會開出該景點的正式頁面（評論、營業時間、照片）。**沒有 `gq` 的就退回座標。**

```js
const gmap = s.gq
  ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(s.gq)}`
  : `https://www.google.com/maps/search/?api=1&query=${s.lat},${s.lng}`;
```

### 為什麼不是「全部都用地名」

**Google Maps 查不到地名時，會退回「使用者所在地附近的同類搜尋」，而不是報錯。**
實測到兩個災難性的例子：

- `山湖台展望所` → 指到**台北碧山里**（差 2,239 km），因為日本沒有這個 POI 名，
  Google 就在使用者所在地找「觀景台」
- `大峠トンネル` → 指到 **463 km 外**的同名隧道

所以 **`gq` 只能給「已實測會解析到正確 POI」的景點**。目前 31 個裡有 29 個有 `gq`，
`goldline`（山湖台）與 `ohtoge`（大峠道路）刻意留空用座標——它們是路上的展望點與
一段公路，沒有可靠的 POI。

### 新增景點時怎麼驗

載入 `https://www.google.com/maps/search/?api=1&query=<候選字串>`，等它跳轉後
從網址列的 `@lat,lng` 取出解析結果，和資料檔的座標算距離。**2 km 內才算通過。**
順便也會抓到資料檔自己的座標錯誤——這次就靠它抓到 6 個（駒草平差 3.2 km、
堺田分水嶺差 4.5 km、滝見台差 2.1 km），並發現 **D6 的賽の磧與駒草平順序顛倒**
（依經度，下山應該是 御釜 140.450 → 駒草平 140.468 → 賽の磧 140.483 → 滝見台 140.525）。

**地名太籠統會變成分類搜尋**（`滝の湯`、`浄土平`、`駒草平 蔵王` 都中過），
加地區限定詞或改用具體設施名才會命中：`鳴子温泉 滝の湯`、`浄土平ビジターセンター`、
`駒草平展望台`。

## 照片機制（重要）

**沒有任何照片被打包進檔案。** 頁面在瀏覽器端向日文維基百科要圖：

1. 先試 Action API 加 `origin=*`，用 `pithumbsize=900` 指定尺寸
2. 失敗改用 REST API `ja.wikipedia.org/api/rest_v1/page/summary/<title>`
3. 兩條都失敗 → 退回自繪 SVG 分類圖示，不會破圖

候選條目是陣列，依序嘗試，所以條目名猜錯不會致命。

### 四個會讓照片「全部不出現」的地雷（2026-08-28 實測修掉）

這四個都不會報錯，只會安靜地一張圖都不顯示，務必不要改回去：

1. **不可自己改寫縮圖寬度**。舊版拿到縮圖網址後用正則把 `/320px-` 換成
   `/900px-`，現在 Wikimedia 只供應 API 實際產生的那一個尺寸，換過的網址一律
   回 **400**（實測 330px 可、640/800/900/1024 全部 400）。要高解析度就用
   Action API 的 `pithumbsize` 去要。
2. **`<img>` 必須設 `crossOrigin='anonymous'`**（且要在指定 `src` 之前設）。
   不設就是 no-cors，拿到的是 opaque 回應，`cache.put()` 存不進去——離線照片
   等於沒有，而且那個被拒絕的 put 還會讓該次請求卡住不返回。
3. **`attach()` 裡的 `<img>` 絕對不可以加 `loading='lazy'`**。那個 img 是先在
   記憶體裡建好、等 `onload` 才插進 DOM 的；`lazy` 會讓瀏覽器因為「元素不在
   文件裡」而永遠不開始載入，於是 onload 不觸發、img 也永遠插不進 DOM。
4. **照片必須等 Service Worker 接管後才載入**。SW 註冊掛在 `window load`，
   第一次造訪時照片會在 SW 接管前就抓完、整批繞過離線快取（實測只有 2 筆進快取）。
   `build_pwa.py` 注入 `window.DEFER_PHOTOS=true`，`render()` 照跑但
   `loadPhotos()` 等 `serviceWorker.controller` 出現（或 4 秒逾時）才呼叫。

## PWA

根目錄的 `sw.js` 做兩件事：
- app shell 快取優先、背景更新
- **維基百科的照片與 API 快取優先且永久保留**

改了 `index.html` 之後**一定要把 `sw.js` 的 `V` 加一版**，否則手機會一直讀舊快取。
這是最容易忘記的一步。

`sw.js` 另有三條**不能違反**的規則，因為 `jeremyl861225.github.io` 上的每個
repo 共用同一個 origin、`caches` 是整個 origin 共用的命名空間：

1. `activate` 只能刪**自己前綴**（`tohoku-guide-`）的舊快取。寫成
   `k !== V` 會把 Clinical-Tools、todo-app 等別的 app 的離線資料一起清掉。
2. `fetch` 只攔自己子路徑（`/tohoku-2026/`）的同源請求。
3. 照片快取用**不帶版本號**的 `tohoku-guide-media`，改版時不會被清掉。

部署：`build/deploy.sh [repo名稱]`，需要 `gh` CLI 並已 `gh auth login`。

## 已知限制與待辦

| 項目 | 狀態 |
|---|---|
| **PDF 未產生** | 這台機器沒有 playwright，`dist/roadbook.pdf` 與 `quickcard.pdf` **尚未重建**。原始檔（`src/*.html`）已是新行程 |
| **飯店空房** | 2026-08-28 以 Agoda 實查，五晚都有房。空房每天在變，訂房前須重查 |
| 蔵王ハイライン | 9/27 正常開放（7:30–17:00），但**起霧就看不到御釜**，且 2026-08 曾因累積雨量臨時封閉過 |
| 銀山溫泉住宿 | 單人加價極兇（NT$16,999／晚），住山上或山下尚未決定 |
| roadbook 與 guide 的景點描述 | 兩份平行維護，改一邊要記得改另一邊 |
| 營業時間與票價 | 全部標註「出發前再確認」 |

## 慣例

- 一律繁體中文，不用簡體
- 日文地名保留原文，首次出現時附羅馬拼音
- 數字、時刻、距離用等寬字體
- 產出物一律進 `dist/`；根目錄只放 PWA 要上線的那五個檔案
- HTML 都是單一自足檔案，**不引入任何外部 CDN**（山區沒網路）
