// The dry store's lesson (game/lessons.ts, DRY_STORE; game/dryhint.ts; docs/design/opening-screen.md, "Hint: the first dry
// store"): a card of the running mix stopped on a store that ran dry, nothing covers it, and a card in play that makes it
// is outside the mix. The line carries the quiet dot and the lesson walks the running mix's own Edit, the maker's add
// button and Save; the mix saved is the player's, with the maker in it. Each fact of the cue taken away clears the mark.
import { fakeDocument, FakeEvent, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { anySelfFedMix, dryCue } from "../src/game/dryhint";
import { Keeps } from "../src/game/keeps";
import { DRY_STORE, FIRST_MIX, FIRST_RULE, LESSONS, mayStart } from "../src/game/lessons";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const step = fixtureStep("drystore", AT);
const dry = step.view;
const TAUGHT = { ...NEW_FLAT, rule_seen: true, lessons: [FIRST_MIX, FIRST_RULE] };
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);
const wood = catalog.storeLabel("wood");
const stool = catalog.cardLabel("stool");
const gather = catalog.cardLabel("gather");
const withWood = (view: View, change: (l: View["ledger"][number]) => View["ledger"][number]): View =>
  ({ ...view, ledger: view.ledger.map((l) => (l.store === "wood" ? change(l) : l)) });

// the cue, one fact at a time
expect("the fixture's stopped stool on dry wood, gather outside the mix", dryCue(catalog, dry), { store: "wood", card: "stool", maker: "gather" });
expect("a line that is not starved: nothing", dryCue(catalog, withWood(dry, (l) => ({ ...l, starved: false }))), null);
expect("a starved line a rule covers: the rule is the answer already", dryCue(catalog, withWood(dry, (l) => ({ ...l, covered: true }))), null);
expect("a stopped card that is not paused (running): nothing", dryCue(catalog, { ...dry, cards: dry.cards.map((c) => (c.card === "stool" ? { ...c, run: "full" as const } : c)) }), null);
expect("a spent card (nothing can refill it) is not this lesson's", dryCue(catalog, { ...dry, cards: dry.cards.map((c) => (c.card === "stool" ? { ...c, run: "spent" as const, spent_store: "wood" } : c)) }), null);
expect("the maker already runs in the mix: the handover refills it", dryCue(catalog, { ...dry, cards: dry.cards.map((c) => (c.card === "gather" ? { ...c, share_bp: 5000 } : c)) }), null);
expect("the maker not ready: adding it would not refill", dryCue(catalog, { ...dry, cards: dry.cards.map((c) => (c.card === "gather" ? { ...c, blocker: { condition: { kind: "at_least" as const, watched: { kind: "skill_level" as const, skill: "foraging" }, value: 9, release: 9 }, ready_at: null } } : c)) }), null);
expect("no maker in play: nothing to add", dryCue(catalog, { ...dry, cards: dry.cards.filter((c) => c.card !== "gather") }), null);
expect("no running mix: nothing", dryCue(catalog, { ...dry, running_mix_id: null }), null);

// the lesson's own condition
const lesson = LESSONS.find((l) => l.id === DRY_STORE)!;
expect("control: rules taught, it may start", mayStart(lesson, dry, keepsOf(TAUGHT)), true);
expect("before the first rule's lesson (and no hands rule): it waits", mayStart(lesson, dry, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX] })), false);
const handsRule: Order = { when: { kind: "at_most", watched: { kind: "store_value", store: "warmth" }, value: 10, release: 20 }, then: { kind: "switch_mix", mix_id: "Stools" } };
expect("a save with a hands rule is past the first rule: it may start", mayStart(lesson, { ...dry, orders: [handsRule], orders_on: [false], order_states: ["waiting"] }, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX] })), true);
const fed = { ...dry, mixes: dry.mixes.map((m) => (m.id === "Stools" ? { ...m, components: [...m.components, { kind: "card_share" as const, card: "gather", share_bp: 5000 }] } : m)) };
expect("control: no saved mix feeds itself in the fixture", anySelfFedMix(dry), false);
expect("a saved mix holding stool and gather has done what it teaches", [anySelfFedMix(fed), mayStart(lesson, fed, keepsOf(TAUGHT))], [true, false]);

function rig(view: View, keeps: Keeps) {
  const decided: Decision[] = [];
  const screen = new Screen(catalog, (d) => { decided.push(d); }, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show({ ...step, view });
  const lay = (n: Element = screen.root): void => {
    Object.assign(n, { rect: { left: 20, top: 300, width: 60, height: 16, right: 80, bottom: 316 } });
    for (const k of Array.from(n.children)) lay(k);
  };
  const frame = (ms = 1): void => { lay(); clock += ms; screen.tick(AT); };
  const line = (): HTMLElement | null => screen.root.querySelector<HTMLElement>('.line[data-teach="dry-line"]');
  const dotted = (): boolean => screen.root.querySelector('.line[data-teach="dry-line"] > .new-dot') !== null;
  const note = (): string => { const n = screen.root.querySelector<HTMLElement>(".lesson-note"); return n && !n.hidden ? n.querySelector(".lesson-line")?.textContent ?? "" : ""; };
  const tap = (selector: string): void => {
    const n = screen.root.querySelector<HTMLElement>(selector);
    if (!n) throw new Error(`nothing to tap at ${selector}`);
    n.click();
    frame();
  };
  return { screen, decided, frame, line, dotted, note, tap, keeps };
}

{  // the walk, on the real controls; nothing is sent until the player saves
  const r = rig(dry, keepsOf(TAUGHT));
  r.frame();
  expect("the dry line is the trigger, about wood", r.line()?.dataset.store, "wood");
  expect("it carries the quiet dot", r.dotted(), true);
  r.frame();
  expect("the lesson starts on the line", r.note(), text("ui.lesson.dry_line", { store: wood, card: stool }));
  r.tap(".lesson-next");
  r.frame();
  expect("then Edit, naming the maker", r.note(), text("ui.lesson.dry_edit", { task: gather, store: wood }));
  r.tap(".hands-mix .hands-meta .hands-edit");
  r.frame();
  expect("then the maker's add button", r.note(), text("ui.lesson.stopped_add", { task: gather }));
  const chip = r.screen.root.querySelector<HTMLElement>('.editor .add-card[data-card="gather"]');
  expect("the Add list is open and the maker's chip glows", [chip?.closest(".folded") !== null, chip?.classList.contains("glow")], [false, true]);
  fakeDocument.querySelector('.editor .add-card[data-card="gather"]')?.dispatchEvent(new FakeEvent("click", { detail: 0 }));   // a key's tap: it joins
  r.frame();
  expect("then Save, saying where the stopped card's time goes", r.note(), text("ui.lesson.dry_save", { card: stool, task: gather, store: wood }));
  expect("nothing was sent before Save", r.decided.length, 0);
  r.tap(".editor .editor-head .primary");
  r.frame();
  expect("last, the rule in one line", r.note(), text("ui.lesson.dry_rule"));
  r.tap(".lesson-next");
  r.frame();
  expect("done, and kept", r.keeps.lessonKept(DRY_STORE) && r.keeps.lessonDone(DRY_STORE), true);
  const saved = r.decided.flatMap((d) => (d.kind === "save_mix" ? [d.mix.components.flatMap((c) => (c.kind === "card_share" ? [c.card] : []))] : []));
  expect("the player's mix was saved with stool and gather", saved.at(-1), ["stool", "gather"]);
  expect("no rule was written for them", r.decided.some((d) => d.kind === "set_orders"), false);
}

{  // kept: never again
  const r = rig(dry, keepsOf({ ...TAUGHT, lessons: [...TAUGHT.lessons, DRY_STORE] }));
  r.frame(); r.frame();
  expect("kept: no trigger", r.line() !== null, false);
  expect("kept: no lesson", r.note(), "");
}

{  // skipped at the line: kept as skipped, and the line still reads dry
  const r = rig(dry, keepsOf(TAUGHT));
  r.frame(); r.frame();
  r.tap(".lesson-note .lesson-skip");
  expect("skipped and kept", r.keeps.lessonKept(DRY_STORE) && !r.keeps.lessonDone(DRY_STORE), true);
  r.frame();
  expect("no trigger after the skip", r.line() !== null, false);
  expect("the line still says it ran dry", Array.from(r.screen.root.querySelectorAll(".line .line-eta")).some((n) => n.textContent?.startsWith(text("ui.ledger.starved"))), true);
}

{  // lessons off for the account: no mark, no lesson
  const r = rig(dry, keepsOf(TAUGHT, null, { lessons: false }));
  r.frame(); r.frame();
  expect("off: no trigger", r.line() !== null, false);
}
