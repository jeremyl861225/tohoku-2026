# 南東北環線 景點指南 — 手機版（PWA）

2026.09.22–27　仙台進出自駕　22 個景點　離線可用

## 檔案

| 檔案 | 用途 |
|---|---|
| `index.html` | 主頁面，含地圖、景點資料、互動邏輯 |
| `sw.js` | Service Worker，負責離線快取（含維基百科照片） |
| `manifest.webmanifest` | 加到主畫面時的名稱、圖示、顯示方式 |
| `icon-192.png` / `icon-512.png` | App 圖示 |

五個檔案都在**專案根目錄**（不是子資料夾）——GitHub Pages 的
「Deploy from a branch」只能選 `/` 或 `/docs`，所以 PWA 必須放在根目錄。

## 線上網址

<https://jeremyl861225.github.io/tohoku-2026/>

Service Worker 需要 HTTPS 才會啟用，GitHub Pages 預設就是 HTTPS。
重新部署跑 `./build/deploy.sh tohoku-2026`。

## 加到 iPhone 主畫面

1. 用 **Safari** 開啟上面的網址（必須是 Safari，Chrome 的加入主畫面不會啟用 PWA）
2. 下方分享鈕 → 「加入主畫面」→ 加入
3. 從主畫面開啟會以全螢幕執行，沒有網址列

## 離線行為

- **第一次開啟時請保持連網**，讓 Service Worker 把頁面與照片抓下來
- 之後蔵王山上、五色沼等收訊不穩的地方也能正常瀏覽
- 離線時畫面底部會出現提示列；文字、地圖、導航座標完全不受影響
- 照片只顯示先前快取過的；沒抓到的會退回分類圖示

## 更新內容

改 `src/` 的內容後跑 `./build/build.sh`（或只跑 `python3 build/build_guide.py && python3 build/build_pwa.py`），
再把 `sw.js` 的 `const V = APP + 'v1'` 改成 `'v2'`，然後 `./build/deploy.sh`。
不改版本號手機會一直讀舊快取。

照片快取用的是不帶版本號的 `tohoku-guide-media`，改版**不會**清掉已經抓下來的照片。
