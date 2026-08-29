/* 南東北環線 景點指南 — 離線快取
 *
 * 注意：jeremyl861225.github.io 上多個 PWA 共用同一個 origin，
 * caches 與 service worker 是整個 origin 共用的命名空間。因此本檔嚴守三條：
 *   1. activate 只刪「本 app 前綴」的舊快取，不可全刪（會清掉別的 app 的離線資料）
 *   2. fetch 只攔本 app 子路徑（/tohoku-2026/）的同源請求
 *   3. 維基照片快取不帶版本號，改版時不會被清掉
 */
const APP   = 'tohoku-guide-';
const V     = APP + 'v10';      // 改了 index.html 就把版本號加一
const MEDIA = APP + 'media';   // 不帶版本：維基照片跨版本永久保留
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];
const BASE  = new URL('./', location).pathname;   // '/tohoku-2026/'

self.addEventListener('install', e => {
  // 一般 addAll，不要加 cache:'reload'（實測在 Pages 上會卡住、快取一直 0 筆）
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(
        ks.filter(k => k.startsWith(APP) && k !== V && k !== MEDIA)
          .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // 維基百科的照片與 API：快取優先，抓到就永久留著（蔵王山上、五色沼收訊不穩也看得到）
  const isWiki = /(^|\.)wikipedia\.org$/.test(url.hostname) ||
                 /(^|\.)wikimedia\.org$/.test(url.hostname);
  if (isWiki) {
    e.respondWith((async () => {
      const cache = await caches.open(MEDIA);
      const hit = await cache.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        // 只有 ok 且非 opaque 的回應寫得進 Cache。opaque（status 0）呼叫 put()
        // 會被拒絕，未處理的拒絕還會讓這次回應卡住不返回——所以圖片端要用 CORS 取。
        if (res && res.ok && res.type !== 'opaque') {
          e.waitUntil(cache.put(req, res.clone()).catch(() => {}));
        }
        return res;
      } catch (err) {
        return hit || Response.error();
      }
    })());
    return;
  }

  // 本站資源：先快取、背景更新。只管自己子路徑，別碰同 origin 的其他 app
  if (url.origin === location.origin && url.pathname.startsWith(BASE)) {
    e.respondWith(
      caches.match(req).then(hit => {
        // 背景更新繞過瀏覽器 HTTP 快取，否則 Pages 的 Expires 會讓新版遲遲不生效
        let fresh = req;
        try { fresh = new Request(req, { cache: 'reload' }); } catch (err) { /* navigate 請求會丟例外 */ }
        const net = fetch(fresh).then(res => {
          if (res && res.ok) caches.open(V).then(c => c.put(req, res.clone()));
          return res;
        }).catch(() => hit);
        return hit || net;
      })
    );
  }
});
