#!/usr/bin/env bash
# 一次重建全部產出。從專案根目錄執行： ./build/build.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}

echo "── 1/6 產生地圖 SVG"
(cd src/map && $PY makemap.py && $PY makemap2.py)

echo "── 2/6 把靜態地圖嵌回 roadbook"
$PY build/inject_map.py

echo "── 3/6 產生 PDF"
$PY build/html2pdf.py src/roadbook.html  dist/roadbook.pdf  --footer
$PY build/html2pdf.py src/quickcard.html dist/quickcard.pdf --margin 8

echo "── 4/6 輸出路線圖 PNG"
$PY build/make_route_png.py

echo "── 5/6 組合互動式指南"
$PY build/build_guide.py

echo "── 6/6 打包 PWA"
$PY build/make_icons.py
$PY build/build_pwa.py

echo
echo "完成。產出在 dist/ 與專案根目錄："
ls -1 dist
ls -1 index.html sw.js manifest.webmanifest icon-192.png icon-512.png
