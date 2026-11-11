// A rule on a count or a level, written in the full condition editor and read back (docs/design/opening-screen.md,
// "The condition editor"): each case of fixtures/subject_cases.json is picked under When, stepped and added; the set_orders it sends holds exactly the case's condition (the shape the engine accepts:
// tests/test_subject_rules_wire.py runs the same cases through the engine); the Rules tab then draws the rule in the
// case's words, and Change opens it on the same subject and number.
import { readFileSync } from "node:fs";
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Condition, Content, Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { RulesTab } from "../src/ui/rules";

install();

interface Case { name: string; pick: string; steps: number; when: Condition; words: string }
const { cases } = JSON.parse(readFileSync("fixtures/subject_cases.json", "utf8")) as { cases: Case[] };
if (cases.length < 3) throw new Error(`only ${cases.length} cases read`);

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const q = (root: ParentNode, sel: string): HTMLButtonElement[] => Array.from(root.querySelectorAll<HTMLButtonElement>(sel));
const one = (root: ParentNode, sel: string): HTMLButtonElement => {
  const found = q(root, sel)[0];
  if (!found) throw new Error(`no ${sel}`);
  return found;
};
const shown = (b: HTMLElement): boolean => { for (let n: HTMLElement | null = b; n; n = n.parentElement) if (n.hidden) return false; return true; };

/** Camp levels at 50, 200 and 400 items, the last held: the fixture's camp (80 items) has reached the first. */
const content: Content = { ...fixtureContent, camp: { ...fixtureContent.camp!, camp_levels: [
  { ...fixtureContent.camp!.camp_levels[0]!, at: 50 * Q }, { ...fixtureContent.camp!.camp_levels[0]!, at: 200 * Q },
  { ...fixtureContent.camp!.camp_levels[1]!, at: 400 * Q, held: true }] } };
const base = fixtureStep("full", 100).view;   // no rules yet; a saved mix to run
const view: View = base;
const MIX = { kind: "switch_mix" as const, mix_id: view.mixes[0]!.id };

function editor(v: View): { tab: RulesTab; decided: Decision[] } {
  const { ctx, got } = testContext(undefined, new Catalog(content));
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(v);
  return { tab, decided: got.decided };
}

/** What the open editor shows of its subject: the button pressed, the shown stepper's label and number. */
function state(cond: HTMLElement): { pick: string | undefined; label: string | undefined; n: string | undefined } {
  const stepper = q(one(cond, ".cond-subject-control"), ".cond-stepper").find(shown);
  return {
    pick: q(cond, ".cond-subject").find((b) => b.getAttribute("aria-pressed") === "true")?.dataset.subject,
    label: stepper?.querySelector(".cond-label")?.textContent ?? undefined,
    n: stepper?.querySelector(".cond-value")?.textContent ?? undefined,
  };
}

for (const c of cases) {
  const { tab, decided } = editor(view);
  one(tab.root, ".rules-new").click();
  const cond = one(tab.root, ".cond");
  one(cond, ".cond-more").click();
  one(cond, `.cond-mix[data-mix="${MIX.mix_id}"]`).click();
  one(cond, `.cond-subject[data-subject="${c.pick}"]`).click();
  for (let i = 0; i < c.steps; i++) q(cond, ".cond-subject-control .cond-stepper").find(shown)!.querySelectorAll("button")[1]!.click();
  const written = state(cond);
  expect(`${c.name}: the sentence`, one(cond, ".cond-sentence").textContent, `${c.words} → ${MIX.mix_id}`);
  one(cond, ".cond-actions .primary").click();
  const set = decided.at(-1);
  expect(`${c.name}: one set_orders, the rule its only order`, set?.kind === "set_orders" ? set.orders : set, [{ when: c.when, then: MIX }]);

  const { tab: back } = editor({ ...view, orders: [{ when: c.when, then: MIX }], orders_on: [false], order_states: ["waiting"] });
  expect(`${c.name}: the Rules tab draws it in its words`, one(back.root, ".rule-cond-text").textContent, c.words);
  one(back.root, ".rule-cond").click();
  const reopened = one(back.root, ".cond");
  expect(`${c.name}: Change opens on the same subject and number`, state(reopened), written);
  expect(`${c.name}: and the same sentence`, one(reopened, ".cond-sentence").textContent, `${c.words} → ${MIX.mix_id}`);
}

// A count starts at the next time from now and a level at the next level; the Camp stops below its held level.
{
  const { tab } = editor(view);
  one(tab.root, ".rules-new").click();
  const cond = one(tab.root, ".cond");
  one(cond, ".cond-more").click();
  one(cond, '.cond-subject[data-subject="task:shelter"]').click();
  expect("shelter, done once of 3: starts at 2 times", state(cond), { pick: "task:shelter", label: "Times", n: "2" });
  one(cond, '.cond-subject[data-subject="level:foraging"]').click();
  expect("foraging at level 2: starts at level 3", state(cond), { pick: "level:foraging", label: "Level", n: "3" });
  one(cond, '.cond-subject[data-subject="camp"]').click();
  expect("the Camp: only levels below the held one", q(cond, ".cond-subject-control .cond-stepper").find(shown)!.querySelectorAll("button")[1]!.disabled, true);
}

// A pick that shows a control brings it into view, centred in its scroll box (dom.bringIntoView), so on a desktop it
// never opens under the pinned foot: the store levels for a store, the stepper for a level or a task. A pick in the
// simple view shows no levels, so nothing scrolls; picking the same subject again shows nothing new.
{
  const scrolls = (node: HTMLElement): unknown[] => [...(Reflect.get(node, "scrolls") as unknown[])];
  const { tab } = editor(view);
  one(tab.root, ".rules-new").click();
  const cond = one(tab.root, ".cond");
  one(cond, '.cond-task[data-card="gather"]').click();
  const store = q(cond, ".cond-store[data-store]")[0];
  if (store) { store.click(); expect("simple view: a store shows no levels, no scroll", scrolls(one(cond, ".cond-levels")), []); }
  one(cond, ".cond-more").click();
  q(cond, ".cond-store[data-store]").find((b) => b.getAttribute("aria-pressed") !== "true")!.click();
  const centred = [{ block: "center", behavior: "smooth" }];
  expect("a store: its levels centred", scrolls(one(cond, ".cond-levels")), centred);
  const control = one(cond, ".cond-subject-control");
  one(cond, '.cond-subject[data-subject="level:foraging"]').click();
  expect("a level: its stepper centred", scrolls(control), centred);
  one(cond, '.cond-subject[data-subject="task:gather"]').click();
  expect("a task: centred again", scrolls(control), [...centred, ...centred]);
  one(cond, '.cond-subject[data-subject="task:gather"]').click();
  expect("the same task again: no scroll", scrolls(control).length, 2);
}
