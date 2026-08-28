#!/usr/bin/env bash
# 東北大環線 景點指南 — 一鍵部署到 GitHub Pages
# 用法：  ./build/deploy.sh [repo名稱]      預設 tohoku-2026
# PWA 的五個檔案在專案根目錄，Pages 直接以 main / (root) 供應。
set -euo pipefail

REPO="${1:-tohoku-2026}"
cd "$(dirname "$0")/.."

say() { printf '\033[1;36m▸ %s\033[0m\n' "$*"; }
die() { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ── 0. 檢查必要檔案 ────────────────────────────────
for f in index.html sw.js manifest.webmanifest icon-192.png icon-512.png; do
  [ -f "$f" ] || die "專案根目錄缺少 $f，請先執行 ./build/build.sh"
done

command -v git >/dev/null || die "找不到 git。macOS 請先執行： xcode-select --install"

if ! command -v gh >/dev/null; then
  cat <<'EOS'
✗ 找不到 GitHub CLI（gh）。

  安裝：  brew install gh
  沒有 Homebrew 的話：https://cli.github.com

  安裝後再跑一次這個腳本即可。
EOS
  exit 1
fi

# ── 1. 登入 ────────────────────────────────────────
if ! gh auth status >/dev/null 2>&1; then
  say "尚未登入 GitHub，開始登入流程（會開瀏覽器）"
  gh auth login
fi
OWNER="$(gh api user -q .login)"
say "GitHub 帳號：$OWNER"

# ── 2. 建立本地 commit ─────────────────────────────
[ -d .git ] || { say "初始化 git repo"; git init -q -b main; }
git add -A
git commit -qm "東北大環線 景點指南 PWA (2026.09.22-27)" 2>/dev/null || say "沒有新變更需要提交"

# ── 3. 建立或連結遠端 repo ─────────────────────────
if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  say "repo $OWNER/$REPO 已存在，直接推送"
  git remote get-url origin >/dev/null 2>&1 \
    || git remote add origin "https://github.com/$OWNER/$REPO.git"
  git push -u origin main
else
  say "建立 repo $OWNER/$REPO 並推送"
  gh repo create "$REPO" --public --source=. --remote=origin --push
fi

# ── 4. 開啟 GitHub Pages ───────────────────────────
say "設定 GitHub Pages（main / root）"
if gh api "repos/$OWNER/$REPO/pages" >/dev/null 2>&1; then
  gh api -X PUT "repos/$OWNER/$REPO/pages" --input - >/dev/null <<'JSON'
{"source":{"branch":"main","path":"/"}}
JSON
else
  gh api -X POST "repos/$OWNER/$REPO/pages" --input - >/dev/null <<'JSON'
{"source":{"branch":"main","path":"/"}}
JSON
fi

URL="https://$OWNER.github.io/$REPO/"

# ── 5. 等待上線 ────────────────────────────────────
say "等待 GitHub Pages 建置（通常 30–90 秒）"
for i in $(seq 1 40); do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$URL" || echo 000)"
  if [ "$code" = "200" ]; then
    printf '\n\033[1;32m✓ 上線了\033[0m\n\n  %s\n\n' "$URL"
    cat <<EOS
接下來在 iPhone：
  1. 用 Safari 開啟上面的網址（必須是 Safari）
  2. 下方分享鈕 → 「加入主畫面」
  3. 從主畫面開啟，並在有網路時把景點滑到底，讓照片快取起來

日後改了內容：改 src/ 後跑 ./build/build.sh，把 sw.js 的 v1 改成 v2，
再跑一次 ./build/deploy.sh 即可。
EOS
    command -v open >/dev/null && open "$URL" || true
    exit 0
  fi
  printf '.'
  sleep 5
done

printf '\n\033[1;33m! 還沒回應 200，但設定應該已完成\033[0m\n  稍後再開： %s\n' "$URL"
printf '  也可到 https://github.com/%s/%s/settings/pages 確認狀態\n' "$OWNER" "$REPO"
