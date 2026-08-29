# 南東北環線 2026

Jeremy 的南東北自駕行前資料包。2026/09/22–27，仙台進出，全程自駕，單人。
範圍為**宮城・山形・福島**三縣，595 km／11:06。

路線：仙台空港 → 仙台 → 松島 → 鳴子溫泉 → 銀山溫泉 → 山寺 → 米澤 →
會津若松 → 五色沼 → 遠刈田溫泉 → 藏王御釜 → 仙台空港（逆時針環線，不走回頭路）

## 產出

| 檔案 | 說明 |
|---|---|
| 根目錄 `index.html` | 手機版 PWA，30 個景點＋6 張晚餐卡，加到主畫面、離線可用 |
| `dist/guide.html` | 同內容的單一自足檔案（不含 Service Worker） |
| `dist/roadbook.pdf` | 逐日行程書 |
| `dist/quickcard.pdf` | 1 頁 A4 速查卡，車上用 |
| `dist/route-map.png` | 路線圖，存手機相簿用 |

## 手機版

線上網址：<https://jeremyl861225.github.io/tohoku-2026/>

用 **Safari** 開啟 → 分享鈕 →「加入主畫面」，即可全螢幕離線使用。
第一次開啟請保持連網，讓它把景點照片抓下來快取。使用與更新說明見 `docs/PWA.md`。

## 建置

手機版與地圖**不需要任何第三方套件**（只要 Python 3）：

```bash
python3 src/map/makemap.py && python3 build/build_guide.py && python3 build/build_pwa.py
```

PDF 需要 playwright：

```bash
pip install -r requirements.txt
playwright install chromium
./build/build.sh
```

重新部署：

```bash
./build/deploy.sh tohoku-2026
```

需要 `gh` CLI（`brew install gh`）並已登入。

## 文件

- `CLAUDE.md` — 接手說明，改動前必讀
- `docs/ITINERARY.md` — 行程事實：分段車程、住宿、餐廳、已查證事項
- `docs/DECISIONS.md` — 決策紀錄：為什麼逆時針、為什麼銀山排週四
- `docs/PWA.md` — 手機版的安裝、離線行為與更新方式
