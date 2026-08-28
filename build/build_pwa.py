#!/usr/bin/env python3
"""把 dist/guide.html 包成 PWA：注入 manifest、Service Worker 註冊、離線提示列。

輸出根目錄的 index.html。同層的 sw.js、manifest.webmanifest、icon-*.png 為手寫或由
build/make_icons.py 產生，這支腳本不會動它們。

PWA 放在專案根目錄，是為了讓 GitHub Pages 直接以 main / (root) 供應——
Pages 的「Deploy from a branch」只能選 / 或 /docs，放子目錄就得另外接 Actions。
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

HEAD = """<title>東北大環線 互動式景點指南｜2026.09.22–27</title>
<link rel="manifest" href="./manifest.webmanifest">
<meta name="theme-color" content="#12232E">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="東北大環線">
<link rel="apple-touch-icon" href="./icon-192.png">
<link rel="icon" href="./icon-192.png">"""

BAR_CSS = """.offbar{position:fixed;left:0;right:0;bottom:0;z-index:60;
  background:var(--ink);color:#fff;font-family:var(--mono);font-size:11px;
  letter-spacing:.06em;padding:9px 16px;display:flex;gap:12px;align-items:center;
  justify-content:center;border-top:1px solid #0A1720}
.offbar b{color:#8FB6CE;font-weight:400}
.offbar button{font-family:var(--mono);font-size:11px;background:#fff;color:var(--ink);
  border:none;border-radius:2px;padding:4px 10px;cursor:pointer}
.foot{max-width:1240px;"""

JS = """window.DEFER_PHOTOS=true;
render();

/* ── 離線與安裝 ──
   照片必須等 Service Worker 接管之後再抓。第一次造訪時 SW 還在安裝，
   這時發出的照片請求不會經過 SW，也就不會進離線快取——到了奧入瀨、
   十二湖那種沒訊號的地方就一張都看不到（要開第二次才會補上）。
   文字與地圖不等，先 render()，只延後照片。 */
(async()=>{
  if('serviceWorker' in navigator){
    try{
      await navigator.serviceWorker.register('./sw.js');
      if(!navigator.serviceWorker.controller){
        await Promise.race([
          new Promise(r=>navigator.serviceWorker.addEventListener('controllerchange',r,{once:true})),
          new Promise(r=>setTimeout(r,4000))   // 保險，不能無限等
        ]);
      }
    }catch(e){}
  }
  loadPhotos();
})();
const bar=document.getElementById('offbar');
function showBar(html,btn){
  if(!bar) return;
  bar.innerHTML=html; bar.hidden=false;
  if(btn){const b=document.createElement('button');b.textContent='知道了';
    b.onclick=()=>bar.hidden=true;bar.appendChild(b);}
}
function netState(){
  if(!navigator.onLine){
    showBar('<b>目前離線</b>\u3000文字與路線圖照常使用；照片只顯示先前快取過的',true);
  }else{ if(bar) bar.hidden=true; }
}
window.addEventListener('online',netState);
window.addEventListener('offline',netState);
netState();
</script>"""


def sub(s: str, old: str, new: str, label: str) -> str:
    if old not in s:
        print(f"  ! 注入點找不到：{label}", file=sys.stderr)
        raise SystemExit(1)
    return s.replace(old, new, 1)


def build() -> pathlib.Path:
    src = ROOT / "dist/guide.html"
    if not src.exists():
        raise SystemExit("請先執行 build/build_guide.py")
    s = src.read_text(encoding="utf-8")

    s = sub(s, "<title>東北大環線 互動式景點指南｜2026.09.22–27</title>", HEAD, "head")
    s = sub(s, '<p class="foot">', '<div id="offbar" class="offbar" hidden></div>\n\n<p class="foot">', "offbar")
    s = sub(s, ".foot{max-width:1240px;", BAR_CSS, "offbar css")
    s = sub(s, "render();\n</script>", JS, "sw register")

    dst = ROOT / "index.html"
    dst.write_text(s, encoding="utf-8")
    print(f"  ✓ {dst.relative_to(ROOT)}　{len(s) // 1024} KB")
    return dst


if __name__ == "__main__":
    build()
