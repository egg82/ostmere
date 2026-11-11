// One lesson at a time, and none held for ever (ui/lessons.ts; docs/design/opening-screen.md, "Lessons"): a lesson
// whose trigger has gone and whose next step's control stays off screen is abandoned (nothing kept) after HELD_MS, so
// the next lesson can run and this one starts over; while one lesson runs, another's guided offer (the ledger's, the strip's, the mix offer
// row's) waits off screen, so its Show me never opens an editor with no lesson to walk it.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { FIRST_MIX, FIRST_RULE } from "../src/game/lessons";
import { ChipOffer } from "../src/ui/chipoffer";
import { Ledger } from "../src/ui/ledger";
import { HELD_MS, Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const RECT = { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 };
const KEPT: Flat = { ...NEW_FLAT, lessons: [FIRST_MIX] };
const mid = fixtureStep("mid", 100).view;
const withMix: View = { ...mid, orders: [], orders_on: [] };
let clock = 0;

/** A control on show (the fake DOM's `rect`), under `parent`. */
function control(cls: string, data: Record<string, string>, parent: HTMLElement = document.body): HTMLButtonElement {
  const n = document.createElement("button");
  n.className = cls;
  Object.assign(n.dataset, data);
  Object.assign(n, { rect: RECT });
  parent.append(n);
  return n;
}
function section(cls: string): HTMLElement {
  const n = document.createElement("section");
  n.className = cls;
  document.body.append(n);
  return n;
}
function rig(account: Flat = KEPT) {
  document.body.replaceChildren();
  const { ctx } = testContext();
  const sent: Flat[] = [];
  const keeps = keepsOf(account, sent);
  let changed = 0;
  const lessons = new Lessons({ catalog: ctx.catalog, glow: ctx.glow, keeps }, document.body, () => { changed += 1; }, document, () => clock);
  const line = (): string => (lessons.root.hidden ? "" : lessons.root.querySelector(".lesson-line")?.textContent ?? "");
  const text = (key: string): string => ctx.catalog.text.get(key);
  const tick = (t: number): void => { clock = t; lessons.tick(); };
  return { ctx: { ...ctx, keeps, lesson: () => lessons.current, lessonSubject: () => lessons.subject }, lessons, keeps, sent, line, text, tick, changed: () => changed };
}

{  // its trigger still on show (the mix offer's Show me, the editor closed): the lesson waits, as long as it takes
  const r = rig(NEW_FLAT);
  const noMix: View = { ...withMix, mixes: [], active_mix_id: null };
  r.lessons.update(noMix);
  const offer = control("offer-both", { teach: "mix-offer", cards: "stand look" });
  r.tick(0);
  offer.click();
  const editor = section("editor");
  const first = control("add-card", { card: "stand" }, editor);
  r.tick(1);
  first.click();
  editor.remove();   // past the trigger's own step, the editor closed: only the Show me is left
  r.tick(2);
  r.tick(2 + 10 * HELD_MS);
  expect("its Show me can open the editor again: not held", [r.lessons.current, r.line()], [FIRST_MIX, r.text("ui.lesson.mix_offer")]);
}

/** The rule lesson walked through Add rule to its Rules-row read, the rule not on; returns the Rules tab's section. */
function afterAddRule(r: ReturnType<typeof rig>): HTMLElement {
  const offer = control("primary", { teach: "rule-offer", task: "stand", watch: "wood", kind: "store" });
  r.tick(0);
  offer.click();
  const cond = section("cond");
  const doTask = control("cond-task", { card: "stand" }, cond);
  r.tick(1);
  doTask.click();
  const when = control("pick", { store: "wood" }, cond);
  r.tick(2);
  when.click();
  const actions = document.createElement("div");
  actions.className = "cond-actions";
  cond.append(actions);
  const add = control("primary", {}, actions);
  r.tick(3);
  add.click();
  cond.remove();
  offer.remove();
  const rules = section("rules");
  control("rule-cond", {}, rules);
  r.tick(4);
  expect("the Rules row's line", r.line(), r.text("ui.lesson.rule_kept"));
  r.lessons.root.querySelector<HTMLElement>(".lesson-next")?.click();   // a read step ends on a tap of the note
  r.tick(60_000);
  return rules;
}

{  // on the Rules tab, the rule never on: the Rules row's line stays and the hand-back waits as long as the rule takes
  const r = rig();
  r.lessons.update(withMix);
  afterAddRule(r);
  for (let t = 60_001; t <= 60_001 + 10 * HELD_MS; t += HELD_MS / 2) r.tick(t);
  expect("still waiting for the hand-back", [r.lessons.current, r.line()], [FIRST_RULE, r.text("ui.lesson.rule_kept")]);
}

{  // left the Rules tab, the rule never on: it is abandoned, nothing kept
  const r = rig();
  r.lessons.update(withMix);
  afterAddRule(r).remove();
  r.tick(60_001);
  r.tick(60_001 + HELD_MS - 1);
  expect("held", r.lessons.current, FIRST_RULE);
  r.tick(60_001 + HELD_MS);
  expect("abandoned, not kept: it starts over the next time it may", [r.lessons.current, r.keeps.lessonKept(FIRST_RULE), r.sent.length], [null, false, 0]);
}

/** The red wood line the fixture's wood order card answers, so the ledger offers that card as a rule. */
const red: LedgerLine = {
  store: "wood", segment: { start: 100, start_value: 14_000, rate: -120_000, limit: 0 }, net_per_hour: -120_000,
  contributions: [{ runner: "tend", per_hour: -120_000 }], empties_at: null, fills_at: null, falling: true, covered: false, starved: false, cap: 40_000,
};
const redView: View = { ...withMix, ledger: [red, ...withMix.ledger.filter((l) => l.store !== "wood")] };

console.log("lessonhold: ok");
