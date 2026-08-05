// 動作總表離線快取。每次轉檔會換 CACHE 名稱，舊快取自動清掉。
const CACHE = "asana-38e286a33a1d";
const FILES = ["./", "./index.html"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;   // YouTube 搜尋等外部連結不攔
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
