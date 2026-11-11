// Web Push on this browser (docs/design/reminders.md, "Delivery"): what it can do (pushCap), the service worker
// (/sw.js, push and click only), and its one subscription. Permission is asked only from a tap, by subscribe.
export type PushCap = "ok" | "denied" | "ios-install" | "none";

export interface PushEnv {
  userAgent: string;
  maxTouchPoints: number;
  platform: string;
  standalone: boolean;
  hasPush: boolean;
  permission: NotificationPermission | null;
}

export function browserEnv(): PushEnv {
  const nav = navigator as Navigator & { standalone?: boolean };
  const hasPush = "serviceWorker" in nav && "PushManager" in window && "Notification" in window;
  return {
    userAgent: nav.userAgent, maxTouchPoints: nav.maxTouchPoints ?? 0, platform: nav.platform ?? "",
    standalone: nav.standalone === true || window.matchMedia?.("(display-mode: standalone)").matches === true,
    hasPush, permission: "Notification" in window ? Notification.permission : null,
  };
}

/** ok: it can subscribe; denied: notifications are blocked here; ios-install: iOS gives Web Push only to a web app
 * added to the Home Screen; none: this browser has no Web Push. */
export function pushCap(env: PushEnv): PushCap {
  const ios = /iPad|iPhone|iPod/.test(env.userAgent) || (env.platform === "MacIntel" && env.maxTouchPoints > 1);
  if (ios && !env.standalone) return "ios-install";
  if (!env.hasPush) return "none";
  return env.permission === "denied" ? "denied" : "ok";
}

export interface Subscribed {
  endpoint: string;
  p256dh: string;
  auth: string;
}

function keysOf(sub: PushSubscription): Subscribed | null {
  const j = sub.toJSON();
  const p256dh = j.keys?.["p256dh"], auth = j.keys?.["auth"];
  return j.endpoint && p256dh && auth ? { endpoint: j.endpoint, p256dh, auth } : null;
}

function keyBytes(b64url: string): ArrayBuffer {
  const raw = atob(b64url.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (b64url.length % 4)) % 4));
  return Uint8Array.from(raw, (c) => c.charCodeAt(0)).buffer;
}

async function registration(): Promise<ServiceWorkerRegistration> {
  await navigator.serviceWorker.register("/sw.js");
  return navigator.serviceWorker.ready;
}

/** The browser's subscription, if it holds one. */
export async function current(): Promise<{ sub: PushSubscription; keys: Subscribed } | null> {
  const sub = await (await registration()).pushManager.getSubscription();
  const keys = sub ? keysOf(sub) : null;
  return sub && keys ? { sub, keys } : null;
}

/** Subscribes (the browser asks permission, from the tap that called this); null when refused. */
export async function subscribe(publicKey: string): Promise<{ sub: PushSubscription; keys: Subscribed } | null> {
  try {
    const reg = await registration();
    const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: keyBytes(publicKey) });
    const keys = keysOf(sub);
    return keys ? { sub, keys } : null;
  } catch {
    return null;
  }
}

/** The device's IANA time zone. */
export function zone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
}
