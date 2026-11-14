// A feature's card (CONTRACT.txt, "A feature's card"): shown once when the page first sees its feature unlocked, after
// what arrived with it; never by a page whose first view already holds the feature; its one button puts it away.
import { Catalog } from "../src/game/catalog";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Content, View } from "../src/api/types";
import { FeatureCard } from "../src/ui/featurecard";

const vars = new Map<string, string>();
let timers: (() => void)[] = [];
let made: Fake[] = [];
class Fake {
  className = ""; textContent = ""; type = ""; open = false; kids: Fake[] = [];
  private on = new Map<string, (() => void)[]>();
  constructor(readonly tag: string) {}
  addEventListener(name: string, f: () => void) { this.on.set(name, [...(this.on.get(name) ?? []), f]); }
  private fire(name: string) { for (const f of this.on.get(name) ?? []) f(); }
  click() { this.fire("click"); }
  append(...k: Fake[]) { this.kids.push(...k); }
  replaceChildren(...k: Fake[]) { this.kids = k; }
  show() { this.open = true; }
  close() { this.open = false; this.fire("close"); }
  offsetHeight = 198;
  all(): Fake[] { return [this, ...this.kids.flatMap((k) => k.all())]; }
}
Object.assign(globalThis, {
  document: {
    createElement: (tag: string) => { const f = new Fake(tag); made.push(f); return f; }, addEventListener: () => undefined,
    documentElement: { style: { setProperty: (k: string, v: string) => void vars.set(k, v), removeProperty: (k: string) => void vars.delete(k) } },
  },
  window: { setTimeout: (f: () => void) => { timers.push(f); return timers.length; }, clearTimeout: () => undefined },
  ResizeObserver: class { constructor(private readonly f: () => void) {} observe() { this.f(); } disconnect() {} },
  fetch: () => Promise.resolve(new Response("")),
});

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const card = { title_key: "ui.close", line_keys: ["ui.chronicle.open", "ui.tab.cards"], button_key: "ui.tab.book" };
const content: Content = {
  ...fixtureContent,
  feature_infos: [...fixtureContent.feature_infos, { feature: "day_done", hint_key: null, label_key: null, feature_card: card }],
};
const base = fixtureStep("covered", 900).view;
const without: View = base;
const withIt: View = { ...base, unlocked: [...base.unlocked, { category: "feature", id: "day_done" }] };

/** A fresh page: its first view, then the next; frames ticked while `busy` holds, then once it no longer does. */
function run(first: View, next: View, busyFrames = 0) {
  timers = [];
  made = [];
  let busy = busyFrames > 0;
  const hosted: unknown[] = [];
  const part = new FeatureCard(new Catalog(content), { arrive: () => undefined, effect: () => undefined, line: () => undefined, get busy() { return busy; } },
    { append: (node) => void hosted.push(node) });
  part.update(first, null);
  part.update(next, first);
  for (let i = 0; i < busyFrames; i += 1) part.tick();
  const waitedWhileBusy = timers.length === 0;
  busy = false;
  part.tick();
  part.tick();
  const scheduled = timers.length;
  for (const f of timers) f();
  const root = made.find((n) => n.tag === "dialog");
  if (!root) throw new Error("no dialog made");
  return { root, onPage: hosted.includes(part.root), waitedWhileBusy, scheduled };
}

{  // live, or on a return: the feature newly unlocked brings the card, once what came with it has been revealed
  const r = run(without, withIt, 3);
  check(r.waitedWhileBusy, "the card waits while what arrived with the feature is still being revealed");
  check(r.scheduled === 1 && r.root.open, "then it comes up, once");
  check(r.onPage, "the card is on the page");
  const texts = r.root.all().map((n) => n.textContent);
  check(texts.includes("Not now") && texts.includes("Chronicle") && texts.includes("Tasks"), `title and lines: ${texts.join("|")}`);
  const buttons = r.root.all().filter((n) => n.tag === "button");
  check(buttons.length === 1 && buttons[0]?.textContent === "Book", "one button, the content's");
  check(vars.get("--end-h") === "198px", "while it is up the page reserves its height");
  buttons[0]?.click();
  check(!r.root.open && !vars.has("--end-h"), "the button puts it away and releases the height");
}

{  // a page whose first view already holds the feature (a reopen, a deploy's redraw) never shows it
  const r = run(withIt, withIt);
  check(r.scheduled === 0 && !r.root.open, "a feature already unlocked at the first view brings no card");
}

{  // a feature without a card brings none; nor does a view that has not unlocked it
  const r = run(without, without);
  check(r.scheduled === 0 && !r.root.open, "no feature, no card");
}

{  // a whole hour reads "1 h", not "1 h 0 m"; with minutes it keeps both
  const { format } = new Catalog(content);
  check(format.duration(3600) === "1 h", `a whole hour: ${format.duration(3600)}`);
  check(format.duration(5400) === "1 h 30 m", `an hour and a half: ${format.duration(5400)}`);
}
