# 東北大環線 2026

Jeremy 的東北自駕行前資料包。2026/09/22–27，仙台進出，全程自駕，單人。

## 產出

| 檔案 | 說明 |
|---|---|
| `dist/roadbook.pdf` | 11 頁 A4 行程書，逐日 roadbook |
| `dist/quickcard.pdf` | 1 頁 A4 速查卡，車上用 |
| `dist/guide.html` | 互動式景點指南，22 個景點，單一自足檔案 |
| `dist/route-map.png` | 路線圖，存手機相簿用 |
| 根目錄 `index.html` | 手機版 PWA，加到主畫面、離線可用（與 `dist/guide.html` 同內容） |

## 建置

```bash
pip install -r requirements.txt
playwright install chromium
./build/build.sh
```

## 手機版

線上網址：<https://jeremyl861225.github.io/tohoku-2026/>

用 **Safari** 開啟 → 分享鈕 → 「加入主畫面」，即可全螢幕離線使用。
第一次開啟請保持連網，讓它把 22 張照片抓下來快取；之後奧入瀨、十二湖
那些沒訊號的地方也看得到。使用與更新說明見 `docs/PWA.md`。

重新部署：

```bash
./build/deploy.sh tohoku-2026
```

需要 `gh` CLI（`brew install gh`）並已登入。

## 文件

- `CLAUDE.md` — 接手說明，改動前必讀
- `docs/PWA.md` — 手機版的安裝、離線行為與更新方式
- `docs/ITINERARY.md` — 行程事實：路線、時刻、住宿、費用、已查證項目
- `docs/DECISIONS.md` — 決策紀錄：為什麼這樣排、踩過哪些坑
