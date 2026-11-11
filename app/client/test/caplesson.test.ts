// The cap rule's lesson (game/lessons.ts, CAP_RULE; docs/design/opening-screen.md, "Hint: the first full store"), on the
// whole screen: a new save has no cap rule, so the first full store the hands fill carries the quiet dot and the lesson
// starts from it, once writing rules is open (a rule of this save seen on and off). It walks the Rules tab's own New rule with nothing filled in, and the rule
// the player adds is theirs: a "reaches" rule on that store doing the task they picked. Before writing rules is open,
// after the lesson is kept, or with a reaching rule already on the store, nothing is marked.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { CAP_RULE, FIRST_MIX, FIRST_RULE } from "../src/game/lessons";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });   // the lesson's reading clock

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const full = fixtureStep("capfull", AT);   // full wood, and a rule of this game's
const RULES_OPEN = { ...NEW_FLAT, rule_seen: true, lessons: [FIRST_MIX, FIRST_RULE] };

function rig(view: View, keeps: Keeps) {
  const decided: Decision[] = [];
  const screen = new Screen(catalog, (d) => { decided.push(d); }, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show({ ...full, view });
  /** Every element laid out with a size, so the runner can see what is not hidden. */
  const lay = (n: Element = screen.root): void => {
    Object.assign(n, { rect: { left: 20, top: 300, width: 60, height: 16, right: 80, bottom: 316 } });
    for (const k of Array.from(n.children)) lay(k);
  };
  const frame = (ms = 1): void => { lay(); clock += ms; screen.tick(AT); };
  const line = (): HTMLElement | null => screen.root.querySelector<HTMLElement>('.line[data-teach="cap-line"]');
  const dotted = (): boolean => screen.root.querySelector('.line[data-teach="cap-line"] > .new-dot') !== null;
  const note = (): string => { const n = screen.root.querySelector<HTMLElement>(".lesson-note"); return n && !n.hidden ? n.querySelector(".lesson-line")?.textContent ?? "" : ""; };
  const tap = (selector: string): void => {
    const n = screen.root.querySelector<HTMLElement>(selector);
    if (!n) throw new Error(`nothing to tap at ${selector}`);
    n.click();
    frame();
  };
  return { screen, decided, frame, line, dotted, note, tap, keeps };
}
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);
const wood = catalog.storeLabel("wood");

{  // the walk, step by step, on the real controls; the rule added is the player's pick
  const r = rig(full.view, keepsOf(RULES_OPEN));
  r.frame();
  expect("the full line is the lesson's trigger, about wood", r.line()?.dataset.store, "wood");
  expect("it carries the quiet dot", r.dotted(), true);
  r.frame();
  expect("the lesson starts on the line", r.note(), text("ui.lesson.cap_full", { store: wood }));
  r.tap(".lesson-next");   // a read step: a tap on the note ends it
  r.frame();
  expect("then the Rules tab", r.note(), text("ui.lesson.cap_rules"));
  r.tap('.tabs [data-tab="rules"]');
  expect("then New rule", r.note(), text("ui.lesson.cap_new"));
  r.tap(".rules .rules-new");
  expect("then More options", r.note(), text("ui.lesson.cap_more"));
  expect("nothing is filled in: no task pressed", r.screen.root.querySelector('.cond .cond-task[aria-pressed="true"]') !== null, false);
  r.tap(".cond .cond-more");
  expect("then the store", r.note(), text("ui.lesson.rule_when", { when: wood }));
  r.tap('.cond .cond-store[data-store="wood"]');
  expect("then the levels", r.note(), text("ui.lesson.cap_levels"));
  r.tap(".cond .cond-fold");
  expect("then reaches", r.note(), text("ui.lesson.cap_reaches", { store: wood }));
  r.tap('.cond .cond-test[data-test="reaches"]');
  expect("then what the hands do instead", r.note(), text("ui.lesson.cap_do"));
  r.tap('.cond .cond-task[data-card="tend"]');
  expect("then Add", r.note(), text("ui.lesson.rule_add"));
  expect("nothing was sent before Add", r.decided.length, 0);
  r.tap(".cond-actions .primary");
  expect("done, and kept", r.keeps.lessonKept(CAP_RULE) && r.keeps.lessonDone(CAP_RULE), true);
  const set = r.decided.find((d): d is Extract<Decision, { kind: "set_orders" }> => d.kind === "set_orders");
  const added: Order | undefined = set?.orders.at(-1);
  const when = added?.when;
  expect("the rule comes on when wood reaches its cap", when && when.kind === "at_least" && when.watched.kind === "store_value" ? [when.watched.store, when.value] : null,
    ["wood", full.view.ledger.find((l) => l.store === "wood")?.cap]);
  expect("and runs what the player picked", JSON.stringify(r.decided).includes('"tend"'), true);
}

{  // before writing rules is open (no rule of theirs seen on and off): no mark, no lesson
  const r = rig(full.view, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE] }));
  r.frame(); r.frame();
  expect("no trigger", r.line() !== null, false);
  expect("no lesson", r.note(), "");
}

{  // a new save on an account that has seen rules in an old one: no rule or queued tap in this game yet, and the Rules
   // tab is drawn anyway, empty but for New rule, so the cap rule's lesson starts and its walk reaches the editor
  const fresh = fixtureStep("full", AT).view;
  expect("control: this game has no rule and nothing queued", [fresh.orders.length, fresh.queue.length], [0, 0]);
  const r = rig(fresh, keepsOf(RULES_OPEN));
  r.frame(); r.frame();
  const tab = r.screen.root.querySelector<HTMLElement>('.tabs [data-tab="rules"]');
  expect("the Rules tab is drawn", tab !== null && tab.style.visibility !== "hidden", true);
  expect("the lesson starts on the full line", r.note(), text("ui.lesson.cap_full", { store: wood }));
  r.tap(".lesson-next"); r.frame();
  r.tap('.tabs [data-tab="rules"]');
  expect("the empty tab offers New rule, and the walk goes on", r.note(), text("ui.lesson.cap_new"));
  r.tap(".rules .rules-new");
  expect("into the editor", r.note(), text("ui.lesson.cap_more"));
}

{  // kept: done or skipped once, it never comes back
  const r = rig(full.view, keepsOf({ ...RULES_OPEN, lessons: [...RULES_OPEN.lessons, CAP_RULE] }));
  r.frame(); r.frame();
  expect("kept: no trigger", r.line() !== null, false);
  expect("kept: no dot on the line", r.screen.root.querySelector(".line > .new-dot") !== null, false);
}

{  // a rule on wood reaching a level is already the answer
  const rule: Order = { when: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 30, release: 10 }, then: { kind: "tap_card", card: "tend" } };
  const r = rig({ ...full.view, orders: [rule], orders_on: [false], order_states: ["waiting"] }, keepsOf(RULES_OPEN));
  r.frame(); r.frame();
  expect("answered: no trigger", r.line() !== null, false);
}

{  // skipped at the line: kept as skipped, and the full line goes on saying what is lost
  const r = rig(full.view, keepsOf(RULES_OPEN));
  r.frame(); r.frame();
  r.tap(".lesson-note .lesson-skip");
  expect("skipped and kept", r.keeps.lessonKept(CAP_RULE) && !r.keeps.lessonDone(CAP_RULE), true);
  r.screen.show(full);
  r.frame();
  expect("no trigger after the skip", r.line() !== null, false);
  expect("the line still reads full, with what is lost", r.screen.root.querySelector('.line.full .line-eta')?.textContent, text("ui.ledger.full"));
}
