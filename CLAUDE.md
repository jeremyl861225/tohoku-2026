# CLAUDE.md — 專案接手說明

給接手這個專案的 Claude Code。先讀完這份再動任何檔案。

---

## 這是什麼

Jeremy 一個人到日本東北自駕六天的行前資料包。**行程本身已經定案、機票已開票**，
這個 repo 產出三份給他實際帶著走的文件，以及一個裝在手機上的離線 App。

不是通用旅遊工具，是一次性的、針對這趟旅程的交付物。所有內容都以
**繁體中文**撰寫，日文地名附原文，這是硬性慣例。

## 旅程事實（改動前務必核對）

| 項目 | 值 |
|---|---|
| 日期 | 2026/09/22（二）–09/27（日），六天五夜 |
| 旅人 | 單人（獨旅）。這影響訂房——見「一人泊」 |
| 去程 | **JX862** TPE 11:35 → SDJ 16:00　星宇 A330-900neo 經濟艙 |
| 回程 | **JX863** SDJ 17:20 → TPE 20:10 |
| 形式 | 仙台進出，順時針環線，全程自駕，不走回頭路 |
| 里程 | 1,070 km／駕駛 18:45（不含 D6 増田町則 1,050 km／18:05） |
| 路線 | 仙台空港→松島→平泉→田澤湖／乳頭溫泉→角館→十和田湖→奧入瀨→八甲田→弘前→五能線海岸→十二湖→秋田→増田町→仙台空港 |

每日路線、里程、住宿見 `docs/ITINERARY.md`。**為什麼這樣排**見 `docs/DECISIONS.md`——
改行程前一定要讀，很多安排是有原因的，不是隨手排的。

## 交付物

| 產出 | 用途 | 來源 |
|---|---|---|
| `dist/roadbook.pdf`（11 頁 A4） | 主要行程書，逐日 roadbook 形式 | `src/roadbook.html` |
| `dist/quickcard.pdf`（1 頁 A4） | 車上速查卡，夾遮陽板用 | `src/quickcard.html` |
| `dist/guide.html` | 互動式景點指南，單一自足檔案 | `src/guide_shell.html` + `src/guide_data.js` + `src/map/map_i.svg` |
| 根目錄的 `index.html` ＋ `sw.js` ＋ `manifest.webmanifest` ＋ `icon-*.png` | 上述指南的 PWA 版，加到 iPhone 主畫面、離線可用 | `dist/guide.html` 加工 |
| `dist/route-map.png` | 路線圖單張圖片，存手機相簿用 | `src/map/map.svg` |

## 目錄結構

```
tohoku-2026/
├── CLAUDE.md              ← 你正在讀的
├── README.md              ← 給人看的簡介
├── requirements.txt
├── docs/
│   ├── ITINERARY.md       ← 行程事實：每日路線、時刻、住宿、費用
│   └── DECISIONS.md       ← 決策紀錄：為什麼這樣排、為什麼不那樣
├── src/                   ← 原始檔（手寫，不是產生物）
│   ├── roadbook.html      ← 行程書。地圖 SVG 內嵌在裡面
│   ├── quickcard.html     ← 速查卡
│   ├── guide_shell.html   ← 互動指南樣板，含 <!--MAP--> 與 //--DATA-- 佔位符
│   ├── guide_data.js      ← 22 個景點的資料陣列（內容的主要來源）
│   └── map/
│       ├── makemap.py     ← 產生靜態地圖 map.svg
│       ├── makemap2.py    ← 產生互動版 map_i.svg（標記帶 data-id）
│       ├── map.svg  map_i.svg   ← 產生物
├── build/
│   ├── build.sh           ← 一鍵重建全部
│   ├── make_route_png.py     ← 路線圖 PNG
│   ├── inject_map.py      ← 把 map.svg 換回 roadbook.html
│   ├── html2pdf.py        ← HTML → PDF
│   ├── build_guide.py     ← 組合互動指南
│   ├── make_icons.py      ← 產生 PWA 圖示
│   ├── build_pwa.py       ← guide.html → 根目錄 index.html
│   └── deploy.sh          ← 一鍵部署到 GitHub Pages
├── index.html             ← PWA 主檔，產生物，不要直接改
├── sw.js                  ← 手寫。離線快取
├── manifest.webmanifest   ← 手寫
├── icon-192.png icon-512.png   ← build/make_icons.py 產生
└── dist/                  ← 全部是產生物

**PWA 的五個檔案刻意放在專案根目錄**，因為 GitHub Pages 的「Deploy from a
branch」只能選 `/` 或 `/docs`，放進子目錄就得另外接 Actions。這也和 Jeremy
其他幾個 app（todo-app、patient-list、book-reader）的擺法一致。
```

## 建置

```bash
pip install -r requirements.txt
playwright install chromium          # 必要，PDF 用 Chromium 列印引擎
./build/build.sh                     # 一次重建全部
```

單獨重建：

```bash
python3 build/html2pdf.py src/roadbook.html dist/roadbook.pdf --footer
python3 build/build_guide.py && python3 build/build_pwa.py
```

環境依賴中比較特別的是 **basemap-data-hires**：地圖的海岸線與湖泊來自離線的
GSHHS 資料，沒有它 `makemap.py` 只能用 intermediate 解析度，十和田湖與田澤湖
會消失。安裝在受限網路下需要 `pip install --break-system-packages`。

## 哪個檔案改哪裡

- **改景點內容**（介紹、票價、停車、拍攝建議）→ 只改 `src/guide_data.js`，
  然後 `build_guide.py` + `build_pwa.py`。**注意 roadbook.html 裡有一份平行的
  簡述**，兩邊目前是手動同步的，這是已知的技術債。
- **改每日時刻／路線** → 改 `src/roadbook.html` 的對應 `.day` 區塊，
  同時檢查 `src/quickcard.html` 的 `.days` 表與 `guide_data.js` 的 `time` 欄位。
- **改地圖** → 改 `src/map/makemap.py`（節點座標在 `PTS`、路線在 `OUT`／`BACK`），
  兩支都要跑，然後 `inject_map.py`。
- **改配色／版面** → CSS 變數集中在每個 HTML 檔頂端的 `:root`，三個檔案共用同一組。

## 設計系統

三份文件共用一套視覺語言：**日本高速公路指標 ＋ 拉力賽 roadbook**。

```
--ink    #12232E   深墨，標題底色與主要文字
--aoike  #1C7FC4   青池藍，路線、停留點、主要強調
--ochre  #B87C1E   進出點、攝影提示、初紅葉
--exp    #0B6E4F   高速道路段（綠色指標）
--sign   #114E8C   一般道段（藍色指標）
--warn   #A33A2A   風險警示
--paper  #EFF2F1   背景
```

- 字體三分工：襯線（標題）／無襯線（內文）／等寬（時間、距離、代碼）。
  **所有數字資料一律用等寬**，這是刻意的——車上掃視時對齊比美觀重要。
- roadbook 的每日卡片用左側時間軸：實心圓點＝停留點，虛線段＝駕駛段，
  km 與分鐘標在路段上。
- 列印時每張日程卡 `break-inside: avoid`，不允許跨頁切開。
- **手機優先響應式**：Jeremy 主要在手機上看，窄螢幕必須改流式單欄、表格轉卡片，
  不接受把固定版心整頁等比縮小。

## 資料模型

`src/guide_data.js` 的 `SPOTS` 陣列，每筆：

```js
{
  id: "aoike",              // 唯一鍵，也是地圖標記的 data-id
  day: 5,                   // 1–6
  name: "十二湖・青池",       // 中文名
  jp: "十二湖・青池",         // 日文原文
  romaji: "Jūniko / Aoike",
  type: "湖泊・森林",         // 決定無照片時的後備圖示，見 index.html 的 ICON 表
  stay: "90 分", time: "12:00",
  lat: 40.4109, lng: 139.9296,   // 導航按鈕與座標顯示用
  wiki: ["十二湖", "青池"],       // 日文維基條目候選，依序嘗試取照片
  desc: "…",                     // 卡片正文
  fields: [["費用","…"], …],      // 展開後的欄位表
  tip: "…", photo: "…",           // 兩種提示條，可省略
  keys: "十二湖 青池 白神山地"      // 只給搜尋比對用的關鍵字
}
```

只有 14 個景點在地圖上有標記（行程主要節點），`id` 必須與 `makemap2.py` 的
`PTS` 最後一欄對得上，否則點地圖不會跳轉。

## 照片機制（重要）

**沒有任何照片被打包進檔案。** 頁面在瀏覽器端向日文維基百科要圖：

1. 先試 Action API 加 `origin=*`，用 `pithumbsize=900` 指定尺寸
2. 失敗改用 REST API `ja.wikipedia.org/api/rest_v1/page/summary/<title>`
3. 兩條都失敗 → 退回自繪 SVG 分類圖示，不會破圖

候選條目是陣列，依序嘗試，所以條目名猜錯不會致命。

**這代表**：用 `file://` 直接開，Safari 會擋掉跨網域請求、照片全部載不出來；
Chrome 通常可以。要穩定看到照片就得走 HTTPS——這是 PWA 存在的主因之一。

### 三個會讓照片「全部不出現」的地雷（2026-08-28 實測修掉）

這三個都不會報錯，只會安靜地一張圖都不顯示，務必不要改回去：

1. **不可自己改寫縮圖寬度**。舊版拿到縮圖網址後用正則把 `/320px-` 換成
   `/900px-`，現在 Wikimedia 只供應 API 實際產生的那一個尺寸，換過的網址一律
   回 **400**（實測 330px 可、640/800/900/1024 全部 400）。要高解析度就用
   Action API 的 `pithumbsize` 去要，讓伺服器自己產。
2. **`<img>` 必須設 `crossOrigin='anonymous'`**（且要在指定 `src` 之前設）。
   不設就是 no-cors，拿到的是 opaque 回應，`cache.put()` 存不進去——離線照片
   等於沒有，而且那個被拒絕的 put 還會讓該次請求卡住不返回。
   Wikimedia 圖床回 `Access-Control-Allow-Origin: *`，走 CORS 沒有問題。
3. **`attach()` 裡的 `<img>` 絕對不可以加 `loading='lazy'`**。那個 img 是先在
   記憶體裡建好、等 `onload` 才插進 DOM 的；`lazy` 會讓瀏覽器因為「元素不在
   文件裡、不在視窗內」而**永遠不開始載入**，於是 onload 不觸發、img 也就永遠
   插不進 DOM——互相卡死，22 張全滅。何況離線快取本來就要在第一次連網時把圖
   全部抓下來，本來就不該延後。

## PWA

根目錄的 `sw.js` 做兩件事：
- app shell 快取優先、背景更新
- **維基百科的照片與 API 快取優先且永久保留**——這是為了奧入瀨、十二湖那些
  沒訊號的地方。第一次開啟必須連網，讓它把圖抓下來。

改了 `index.html` 之後**一定要把 `sw.js` 的 `V` 從 `v1` 改成 `v2`**，
否則手機會一直讀舊快取。這是最容易忘記的一步。

`sw.js` 另有三條**不能違反**的規則，因為 `jeremyl861225.github.io` 上的每個
repo 共用同一個 origin、`caches` 是整個 origin 共用的命名空間：

1. `activate` 只能刪**自己前綴**（`tohoku-guide-`）的舊快取。寫成
   `k !== V` 會把 Clinical-Tools、todo-app 等別的 app 的離線資料一起清掉。
2. `fetch` 只攔自己子路徑（`/tohoku-2026/`）的同源請求。
3. 照片快取用**不帶版本號**的 `tohoku-guide-media`，改版時不會被清掉——
   奧入瀨、十二湖那些沒訊號的地方靠的就是它。

部署：`build/deploy.sh [repo名稱]`，需要 `gh` CLI 並已 `gh auth login`。
腳本會建 repo、推送、用 API 開啟 Pages、輪詢到 200 為止再印出網址。

## 已知限制與待辦

| 項目 | 狀態 |
|---|---|
| **飯店空房** | **未確認，也無法由程式確認**。已查證的是營業狀態與單人方案是否存在。訂房必須以「1 名」條件即時查詢——很多旅館 2 名有房、1 名不顯示 |
| 東北高速 Pass（TEP） | 每年實施期間不同，須訂租車時向租車公司確認 2026 秋季是否開放，且**取車時當場申請、事後不能補辦** |
| 増田町公休 | 多數內藏 09:00–16:00，**週三多為公休**。9/27 是週日，應無影響，但出發前仍應確認 |
| roadbook 與 guide 的景點描述 | 兩份平行維護，改一邊要記得改另一邊 |
| 維基條目名 | 部分是推測的（如「千畳敷海岸」可能有消歧義），靠候選陣列與圖示後備吸收 |
| 營業時間與票價 | 全部標註「出發前再確認」，不保證到 9 月仍正確 |

## 慣例

- 一律繁體中文，不用簡體
- 日文地名保留原文（`名稱 <span class="jp">日文</span>`），首次出現時附羅馬拼音
- 數字、時刻、距離用等寬字體
- 產出物一律進 `dist/`；根目錄只放 PWA 要上線的那五個檔案
- HTML 都是單一自足檔案，**不引入任何外部 CDN**（山區沒網路）
