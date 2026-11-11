// Ostmere's service worker: shows a reminder (reminders/words.py's payload) and opens the game when it is tapped.
// Push and click only. It has no fetch handler on purpose: a page must only ever run its own build's bundle.
self.addEventListener("push", (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch { data = {}; }
  const title = data.title || "Ostmere";
  event.waitUntil(self.registration.showNotification(title, {
    body: data.body || "", icon: "/icons/apple-touch-icon.png", data: { url: data.url || "/" }, tag: "ostmere-reminder",
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = new URL((event.notification.data && event.notification.data.url) || "/", self.location.origin).href;
  event.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((open) => {
    const here = open.find((c) => c.url.startsWith(self.location.origin));
    return here ? here.focus() : self.clients.openWindow(url);
  }));
});
