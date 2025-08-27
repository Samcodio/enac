self.addEventListener("install", (event) => {
  console.log("SW: Installing...");
  event.waitUntil(
    caches.open("offline-cache").then((cache) => {
      console.log("SW: Caching offline.html");
      return cache.addAll([
        "/static/assets/Offline/offline.html"
      ]);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request).catch(() => {
      if (event.request.mode === "navigate") {
        // If it's a page navigation request, show offline.html
        return caches.match("/static/assets/Offline/offline.html");
      }
      // For other requests (images, CSS, etc.), let them fail silently
      return;
    })
  );
});

