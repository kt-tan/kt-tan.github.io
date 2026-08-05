// 自我了斷用。動作總表 2026-08-05 從 /asana/ 搬到 /repertoire/，
// 舊的 service worker 是快取優先，不主動拆掉的話舊網址會永遠吐快取裡的舊頁面。
// 瀏覽器每次導航都會比對 sw.js 有沒有變，變了就裝新的——也就是這一支——
// 它一啟用就清掉所有 asana- 開頭的快取、把自己註銷，然後叫所有分頁重新載入，
// 重新載入時拿到的就是網路上的轉址頁。
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k.startsWith("asana-")).map(k => caches.delete(k)));
    await self.registration.unregister();
    const clients = await self.clients.matchAll({ type: "window" });
    clients.forEach(c => c.navigate(c.url));
  })());
});
