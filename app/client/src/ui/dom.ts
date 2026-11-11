// Small DOM helpers. Text only ever goes in through textContent.

export function el<K extends keyof HTMLElementTagNameMap>(tag: K, className = "", text = ""): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

/** Set text only when it changed, so a per-frame update does not churn the DOM. */
export function setText(node: Element, text: string): void {
  if (node.textContent !== text) node.textContent = text;
}

/** Restart a one-shot CSS animation class (a bounce, a flash). The class goes when it has played: left on, a hidden tab
 * shown again would play it again. */
export function pulse(node: Element, className: string): void {
  node.classList.remove(className);
  void (node as HTMLElement).offsetWidth;
  node.classList.add(className);
  const done = (e: Event): void => {
    if (e.target !== node) return;
    node.removeEventListener("animationend", done);
    node.classList.remove(className);
  };
  node.addEventListener("animationend", done);
}

/** "+1" rising off a card when a completion lands, over the card so nothing moves (ui/ladder.ts says when). */
export function popOne(node: HTMLElement): void {
  const pop = el("span", "pop", "+1");
  pop.setAttribute("aria-hidden", "true");
  pop.addEventListener("animationend", () => pop.remove());
  node.append(pop);
  window.setTimeout(() => pop.remove(), 1500);
}

/** Keyed rows: reuse a key's row across redraws, make new ones, drop the ones that left, keep the given order. */
export function keyed<T, R extends { node: HTMLElement }>(
  parent: Element, items: T[], key: (item: T) => string, rows: Map<string, R>, make: (item: T) => R,
): Map<string, R> {
  const next = rekey(items, key, rows, make);
  place(parent, Array.from(next.values(), (r) => r.node));
  return next;
}

/** `keyed` without the placing: a key's row reused, new ones made, the ones that left removed from the page. */
export function rekey<T, R extends { node: HTMLElement }>(
  items: T[], key: (item: T) => string, rows: Map<string, R>, make: (item: T) => R,
): Map<string, R> {
  const next = new Map<string, R>();
  for (const item of items) {
    const k = key(item);
    next.set(k, rows.get(k) ?? make(item));
  }
  for (const [k, row] of rows) if (!next.has(k)) row.node.remove();
  return next;
}

/** Put `nodes` in `parent` in the given order, moving only what is out of place: re-inserting a node restarts its CSS
 * animations. A node in another parent moves here. */
export function place(parent: Element, nodes: HTMLElement[]): void {
  let cursor = parent.firstElementChild;
  for (const node of nodes) {
    if (node === cursor) cursor = cursor.nextElementSibling;
    else parent.insertBefore(node, cursor);
  }
}

/** The event a control sends when it did what it is for, however it was pressed: one that acts on pointerup is redrawn
 * before a click could follow. The lesson runner (ui/lessons.ts) hears it as it hears a click. */
export const ACTED = "acted";

/** Says `node` acted: sent while it is still in the page, so it reaches the document before a redraw replaces it. */
export function acted(node: HTMLElement): void {
  node.dispatchEvent(new Event(ACTED, { bubbles: true }));
}

/** The OS asks for less motion: a fade is an instant change, an effect shows its still form. There is no in-game toggle. */
export function reducedMotion(): boolean {
  return typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function tapFeedback(): void {
  if ("vibrate" in navigator) navigator.vibrate(8);
}

type Box = { getBoundingClientRect(): { top: number; bottom: number } };

/** Brings `node` into view with its top clear of `pinned`, a sticky part over the same scroll (the hands strip on a
 * phone): the browser's nearest scroll knows nothing of sticky parts, so a top left under it is scrolled down clear by
 * exactly that much, in whichever of `scrollers` this layout scrolls. */
export function revealBelow(node: Box & { scrollIntoView?(arg?: ScrollIntoViewOptions): void }, pinned: Box, scrollers: { scrollTop: number }[]): void {
  node.scrollIntoView?.({ block: "nearest" });
  for (const scroller of scrollers) {
    const under = pinned.getBoundingClientRect().bottom - node.getBoundingClientRect().top;
    if (under > 0) scroller.scrollTop -= under;
  }
}

/** The page's parts pinned over its scroll on a phone (ui/screen.ts: the scene, then the hands strip under it). */
const PINNED = ".stage, .panel-top";

/** The top of the box `node` scrolls in: its nearest ancestor that scrolls (a sheet, the editor), else the window's. */
function scrollBoxTop(node: Element): number {
  for (let n = node.parentElement; n; n = n.parentElement) {
    if (["auto", "scroll"].includes(window.getComputedStyle(n).overflowY)) return n.getBoundingClientRect().top;
  }
  return 0;
}

/** `target` scrolled to the middle of what the pinned parts over its scroll box leave of it (a sheet or the editor that
 * starts below them: all of it): its scroll margin is their overlap for the call, so the browser centres it there; at
 * once under reduced motion. */
export function bringIntoView(doc: Pick<Document, "querySelectorAll">, target: HTMLElement): void {
  const t = target.getBoundingClientRect();
  const over = Array.from(doc.querySelectorAll(PINNED)).map((n) => n.getBoundingClientRect()).filter((r) => r.width > 0 && r.left < t.right && r.right > t.left);
  target.style.scrollMarginTop = `${Math.round(Math.max(0, ...over.map((r) => r.bottom - scrollBoxTop(target))))}px`;
  target.scrollIntoView({ block: "center", behavior: reducedMotion() ? "instant" : "smooth" });
  target.style.scrollMarginTop = "";
}
