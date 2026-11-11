// A small stand-in for the DOM, enough for the parts that draw rules (rules.ts, condition.ts, ledger.ts, hands.ts) to
// run under node: elements with classes, attributes, data, children, events and a simple selector engine (tags,
// classes, [attr] and [attr="v"], descendant and child combinators, selector lists). Layout is whatever a test sets
// with `rect`. Installed on globalThis by `install()`.

type Listener = (e: FakeEvent) => void;

export class FakeEvent {
  defaultPrevented = false;
  stopped = false;
  target: FakeEl | null = null;
  constructor(readonly type: string, init: Record<string, unknown> = {}) { Object.assign(this, init); }
  preventDefault(): void { this.defaultPrevented = true; }
  stopImmediatePropagation(): void { this.stopped = true; }
  stopPropagation(): void { this.stopped = true; }
}

interface Rect { left: number; top: number; width: number; height: number; right: number; bottom: number }

export class FakeEl {
  className = "";
  hidden = false;
  disabled = false;
  type = "";
  checked = false;
  value = "";
  title = "";
  open = false;
  parent: FakeEl | null = null;
  kids: (FakeEl | string)[] = [];
  readonly style: Record<string, string> & { setProperty(k: string, v: string): void; removeProperty(k: string): void; getPropertyValue(k: string): string };
  readonly dataset: Record<string, string> = {};
  rect: Rect = { left: 0, top: 0, width: 0, height: 0, right: 0, bottom: 0 };
  private readonly attrs = new Map<string, string>();
  private readonly on = new Map<string, { f: Listener; capture: boolean; once: boolean }[]>();

  constructor(readonly tagName: string) {
    const style: Record<string, string> = {};
    this.style = Object.assign(style, {
      setProperty: (k: string, v: string) => { style[k] = v; },
      removeProperty: (k: string) => { delete style[k]; },
      getPropertyValue: (k: string) => style[k] ?? "",
    }) as FakeEl["style"];
  }

  get classList() {
    const names = () => new Set(this.className.split(" ").filter(Boolean));
    const set = (s: Set<string>) => { this.className = [...s].join(" "); };
    return {
      add: (...c: string[]) => { const s = names(); for (const x of c) s.add(x); set(s); },
      remove: (...c: string[]) => { const s = names(); for (const x of c) s.delete(x); set(s); },
      contains: (c: string) => names().has(c),
      toggle: (c: string, force?: boolean) => {
        const s = names();
        const on = force ?? !s.has(c);
        if (on) s.add(c); else s.delete(c);
        set(s);
        return on;
      },
    };
  }

  get isConnected(): boolean {
    let n: FakeEl | null = this;
    while (n.parent) n = n.parent;
    return n === fakeDocument.body;
  }

  get textContent(): string { return this.kids.map((k) => (typeof k === "string" ? k : k.textContent)).join(""); }
  set textContent(v: string) { this.replaceChildren(...(v ? [v] : [])); }

  get parentElement(): FakeEl | null { return this.parent; }
  get children(): FakeEl[] { return this.kids.filter((k): k is FakeEl => typeof k !== "string"); }
  get firstChild(): FakeEl | string | null { return this.kids[0] ?? null; }
  get firstElementChild(): FakeEl | null { return this.children[0] ?? null; }
  get lastElementChild(): FakeEl | null { return this.children.at(-1) ?? null; }
  get childElementCount(): number { return this.children.length; }
  get nextElementSibling(): FakeEl | null {
    const sibs = this.parent?.children ?? [];
    return sibs[sibs.indexOf(this) + 1] ?? null;
  }
  get offsetWidth(): number { return this.rect.width; }
  get offsetHeight(): number { return this.rect.height; }
  get offsetParent(): FakeEl | null { return this.hidden ? null : this.parent; }

  private adopt(k: FakeEl | string): FakeEl | string {
    if (typeof k !== "string") { k.remove(); k.parent = this; }
    return k;
  }
  // adopt() first: it may take the node out of this.kids, which reassigns the array.
  append(...k: (FakeEl | string)[]): void { for (const x of k) { const a = this.adopt(x); this.kids.push(a); } }
  prepend(...k: (FakeEl | string)[]): void { const a = k.map((x) => this.adopt(x)); this.kids.unshift(...a); }
  replaceChildren(...k: (FakeEl | string)[]): void {
    for (const c of this.kids) if (typeof c !== "string") c.parent = null;
    this.kids = [];
    this.append(...k);
  }
  insertBefore(node: FakeEl, before: FakeEl | null): void {
    this.adopt(node);
    const at = before ? this.kids.indexOf(before) : -1;
    if (at < 0) this.kids.push(node); else this.kids.splice(at, 0, node);
  }
  before(...k: FakeEl[]): void {
    for (const x of k) this.parent?.insertBefore(x, this);
  }
  after(...k: FakeEl[]): void {
    const parent = this.parent;
    if (!parent) return;
    const next = parent.kids[parent.kids.indexOf(this) + 1];
    for (const x of k) parent.insertBefore(x, typeof next === "string" ? null : next ?? null);
  }
  remove(): void {
    if (!this.parent) return;
    this.parent.kids = this.parent.kids.filter((k) => k !== this);
    this.parent = null;
  }
  contains(n: FakeEl | null): boolean {
    for (let x = n; x; x = x.parent) if (x === this) return true;
    return false;
  }
  cloneNode(): FakeEl {
    const c = new FakeEl(this.tagName);
    c.className = this.className;
    c.kids = this.kids.map((k) => (typeof k === "string" ? k : k.cloneNode()));
    for (const k of c.kids) if (typeof k !== "string") k.parent = c;
    return c;
  }

  setAttribute(k: string, v: string): void { this.attrs.set(k, String(v)); }
  getAttribute(k: string): string | null { return this.attrs.get(k) ?? null; }
  removeAttribute(k: string): void { this.attrs.delete(k); }
  attr(k: string): string | undefined {
    if (k.startsWith("data-")) return this.dataset[k.slice(5).replace(/-(\w)/g, (_, c: string) => c.toUpperCase())];
    return this.attrs.get(k);
  }

  addEventListener(type: string, f: Listener, opts?: boolean | { capture?: boolean; once?: boolean }): void {
    const o = typeof opts === "object" ? opts : { capture: opts === true };
    this.on.set(type, [...(this.on.get(type) ?? []), { f, capture: o.capture === true, once: o.once === true }]);
  }
  removeEventListener(type: string, f: Listener): void { this.on.set(type, (this.on.get(type) ?? []).filter((l) => l.f !== f)); }
  /** Capture listeners first, then the rest; then up the tree (bubbling), as far as the document. */
  dispatchEvent(e: FakeEvent): boolean {
    e.target ??= this;
    const path: FakeEl[] = [];
    for (let n: FakeEl | null = this; n; n = n.parent) path.push(n);
    const run = (n: FakeEl, capture: boolean): void => {
      for (const l of [...(n.on.get(e.type) ?? [])]) {
        if (e.stopped || l.capture !== capture) continue;
        if (l.once) n.removeEventListener(e.type, l.f);
        l.f(e);
      }
    };
    fakeDocument.fire(e, true);
    for (const n of [...path].reverse()) run(n, true);
    if (!e.stopped) for (const n of path) { run(n, false); if (e.stopped) break; }
    if (!e.stopped) fakeDocument.fire(e, false);
    return !e.defaultPrevented;
  }
  /** A click, as a press would make one: nothing on a disabled control. */
  click(): void { if (!this.disabled) this.dispatchEvent(new FakeEvent("click")); }
  focus(): void { fakeDocument.activeElement = this; }
  setPointerCapture(): void { /* moves arrive on this node anyway: tests dispatch them here */ }
  getBoundingClientRect(): Rect { return this.rect; }
  /** Every scrollIntoView asked of this node, with its options: nothing lays out here, so a test reads what was asked. */
  readonly scrolls: unknown[] = [];
  /** The node's scroll-margin-top at each of those calls. */
  readonly scrollMargins: string[] = [];
  scrollIntoView(options?: unknown): void { this.scrolls.push(options ?? null); this.scrollMargins.push(this.style["scrollMarginTop"] ?? ""); }
  showModal(): void { this.open = true; }
  close(): void { this.open = false; }

  matches(selector: string): boolean { return selector.split(",").some((s) => matchComplex(this, s.trim())); }
  closest(selector: string): FakeEl | null {
    for (let n: FakeEl | null = this; n; n = n.parent) if (n.matches(selector)) return n;
    return null;
  }
  querySelectorAll<T = FakeEl>(selector: string): T[] {
    const out: FakeEl[] = [];
    const walk = (n: FakeEl): void => {
      for (const k of n.children) {
        if (selector.split(",").some((s) => matchComplex(k, s.trim(), this))) out.push(k);
        walk(k);
      }
    };
    walk(this);
    return out as T[];
  }
  querySelector<T = FakeEl>(selector: string): T | null { return (this.querySelectorAll<T>(selector)[0] ?? null); }

  /** The visible text of this node and everything under it that isn't hidden. */
  shown(): string {
    if (this.hidden) return "";
    return this.kids.map((k) => (typeof k === "string" ? k : k.shown())).join("");
  }
}

/** One compound selector: tag, .classes, [attr] / [attr="v"], :scope. */
function matchCompound(n: FakeEl, sel: string, scope?: FakeEl): boolean {
  if (sel === ":scope") return n === scope;
  const m = /^([a-z][\w-]*)?((?:\.[\w-]+|\[[^\]]+\]|:scope)*)$/i.exec(sel);
  if (!m) throw new Error(`fake-dom: selector not understood: ${sel}`);
  if (m[1] && n.tagName !== m[1]) return false;
  for (const part of m[2]!.match(/\.[\w-]+|\[[^\]]+\]|:scope/g) ?? []) {
    if (part === ":scope") { if (n !== scope) return false; continue; }
    if (part.startsWith(".")) { if (!n.classList.contains(part.slice(1))) return false; continue; }
    const a = /^\[([\w-]+)(?:="([^"]*)")?\]$/.exec(part);
    if (!a) throw new Error(`fake-dom: attribute selector not understood: ${part}`);
    const v = n.attr(a[1]!);
    if (v === undefined || (a[2] !== undefined && v !== a[2])) return false;
  }
  return true;
}

function matchComplex(n: FakeEl, sel: string, scope?: FakeEl): boolean {
  const parts = sel.match(/>|(?:[^\s>[\]]+|\[[^\]]*\])+/g) ?? [];   // whitespace inside [attr="a b"] stays
  const test = (node: FakeEl | null, i: number): boolean => {
    if (!node || !matchCompound(node, parts[i]!, scope)) return false;
    if (i === 0) return true;
    if (parts[i - 1] === ">") return test(node.parent, i - 2);
    for (let a = node.parent; a; a = a.parent) if (test(a, i - 1)) return true;
    return false;
  };
  return test(n, parts.length - 1);
}

class FakeDocument {
  body = new FakeEl("body");
  activeElement: FakeEl | null = null;
  /** What elementFromPoint answers: a test points it at the node under the pointer. */
  under: FakeEl | null = null;
  private readonly on = new Map<string, { f: Listener; capture: boolean }[]>();
  createElement(tag: string): FakeEl { return new FakeEl(tag); }
  addEventListener(type: string, f: Listener, opts?: boolean | { capture?: boolean }): void {
    const capture = typeof opts === "object" ? opts.capture === true : opts === true;
    this.on.set(type, [...(this.on.get(type) ?? []), { f, capture }]);
  }
  removeEventListener(type: string, f: Listener): void { this.on.set(type, (this.on.get(type) ?? []).filter((x) => x.f !== f)); }
  /** The document's listeners of one phase: capture ones run before the target's, the rest after the bubble. */
  fire(e: FakeEvent, capture: boolean): void { for (const l of [...(this.on.get(e.type) ?? [])]) if (l.capture === capture) l.f(e); }
  elementFromPoint(): FakeEl | null { return this.under; }
  /** The note's stack at a point, top first: `under`, with whatever a test stacks above it (`over`). */
  over: FakeEl[] = [];
  elementsFromPoint(): FakeEl[] { return [...this.over, ...(this.under ? [this.under] : [])]; }
  querySelectorAll(sel: string): FakeEl[] { return this.body.querySelectorAll(sel); }
  querySelector(sel: string): FakeEl | null { return this.body.querySelector(sel); }
  /** The element whose `id` attribute is set (setAttribute("id", ...)); a page's ids are the markup's. */
  getElementById(id: string): FakeEl | null { return this.body.querySelector(`[id="${id}"]`); }
}

export const fakeDocument = new FakeDocument();

export function install(): void {
  const store = new Map<string, string>();
  const sessionStorage = {
    getItem: (k: string) => store.get(k) ?? null, setItem: (k: string, v: string) => { store.set(k, v); },
    removeItem: (k: string) => { store.delete(k); }, clear: () => store.clear(),
  };
  const location = { pathname: "/", search: "", hash: "" };
  const history = { state: null, replaceState: (_s: unknown, _t: string, url: string) => { location.hash = url.includes("#") ? url.slice(url.indexOf("#")) : ""; } };
  // getComputedStyle answers a node's own inline overflow-y: nothing cascades here
  const win = { addEventListener: () => {}, matchMedia: () => ({ matches: false, addEventListener: () => {} }), setTimeout, clearTimeout,
    getComputedStyle: (n: FakeEl) => ({ overflowY: n.style["overflowY"] ?? "" }) };
  Object.assign(globalThis, { document: fakeDocument, sessionStorage, location, history, window: win, Event: FakeEvent });   // a part's own events (dom.acted) go through the fake tree
}

/** A pointer event of `type` at (x, y), from pointer 1. */
export function pointer(type: string, x: number, y: number): FakeEvent {
  return new FakeEvent(type, { clientX: x, clientY: y, pointerId: 1, button: 0 });
}
