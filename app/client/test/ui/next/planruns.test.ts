// One run per Plan entry (docs/decisions/mixes.md, "One queue, two ways in"): Plan lists every card the queue takes,
// work done again and again and a card a lane runs now included, and each pick adds one run of it, counted after the
// runs already planned (the tap under way and the card's earlier entries). Next draws a run of the same card as one row,
// "once" or ×N, whose Remove and ≡ act on one entry. The owner's case: an uncapped action card a hands tap runs, the
// queue empty.
import { install } from "../../fake-dom";
import { testContext } from "../../context";
import { fixtureContent } from "../../../fixtures/content";
import { fixtureStep } from "../../../fixtures/steps";
import type { Card, Decision, QueueEntry, View } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { moveQueued, onFace, planCards, rowStep, tapUntil, unqueue, whenReady } from "../../../src/game/mixes/queue";
import { nextRows } from "../../../src/ui/next/nextlist";
import { NextOrder } from "../../../src/ui/next/nextorder";
import { StintPlan } from "../../../src/ui/next/stintplan";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const ended = fixtureStep("restoffer", 100).view;
const listed = (v: View) => planCards(catalog, v).map((c) => c.card);
const entries = (d: Decision | null): QueueEntry[] => (d !== null && d.kind === "set_queue" ? d.entries : []);
const after = (v: View, d: Decision | null): View => ({ ...v, queue: entries(d) });

expect("control: gather is work done again and again, on the hands", [catalog.cards.get("gather")?.presentation, catalog.laneOf("gather"), catalog.ruled("gather")], ["action", "hands", false]);
const gather: Card = { ...ended.cards.find((c) => c.card === "gather")!, cap: null, completions: 9, by: "tap", share_bp: 0 };
const base: View = { ...ended, cards: ended.cards.map((c) => (c.card === "gather" ? gather : c)), queue: [] };
const running: View = { ...base, lanes: base.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "gather" } : l)) };

expect("work done again and again is listed", listed(base).includes("gather"), true);
expect("a card a hands tap runs is listed", listed(running).includes("gather"), true);
expect("idle: one run, the next completion", entries(whenReady(catalog, base, "gather")), [tapUntil("gather", 10)]);
const one = after(running, whenReady(catalog, running, "gather"));
expect("running: one run after the tap under way", one.queue, [tapUntil("gather", 11)]);
expect("still listed once planned", listed(one).includes("gather"), true);
const two = after(one, whenReady(catalog, one, "gather"));
expect("picked again: another run after the first", two.queue, [tapUntil("gather", 11), tapUntil("gather", 12)]);

// Next: the two runs are one row, ×2; Remove takes one off and the run left is still one after the tap under way.
const { ctx } = testContext();
const plan = new StintPlan(ctx, () => {});
const idle = new NextOrder(ctx, document.createElement("div"), () => null, () => {});
const words = (v: View) => nextRows(ctx, v, plan, idle).filter((r) => r.classList.contains("next-row")).map((r) => r.querySelector(".rule-action")?.textContent);
expect("one row for a run of the same card", words(two), [`${catalog.cardLabel("gather")} ×2`]);
expect("a single run says once", words(one), [`${catalog.cardLabel("gather")} once`]);
expect("Remove takes one off", unqueue(two, 1), { kind: "set_queue", entries: [tapUntil("gather", 11)] });
expect("whichever one it is", unqueue(two, 0), { kind: "set_queue", entries: [tapUntil("gather", 11)] });
const removeLabel = nextRows(ctx, two, plan, idle).find((r) => r.classList.contains("next-row"))?.querySelector("button.quiet")?.textContent;
expect("and says so", removeLabel, "Remove one");

// A run of another card between them: each row is its own, and moving one keeps each card's runs in order.
const stool = ended.cards.find((c) => c.card === "stool")!;
const mixed: View = { ...two, queue: [tapUntil("gather", 11), tapUntil(stool.card, stool.completions + 1), tapUntil("gather", 12)] };
expect("rows split by another card", words(mixed), [`${catalog.cardLabel("gather")} once`, `${catalog.cardLabel("stool")} once`, `${catalog.cardLabel("gather")} once`]);
expect("moving the last run up renumbers the card's runs in order", entries(moveQueued(mixed, 2, 1)), [tapUntil("gather", 11), tapUntil("gather", 12), tapUntil(stool.card, stool.completions + 1)]);
expect("moving the first run down too", entries(moveQueued(mixed, 0, 1)), [tapUntil(stool.card, stool.completions + 1), tapUntil("gather", 11), tapUntil("gather", 12)]);

// The face's When ready keeps its own rules: a step only, not once queued, not the card its lane runs.
expect("the face takes no work done again and again", onFace(catalog, base, gather), false);
const stoolBusy: View = { ...running, cards: running.cards.map((c) => (c.card === "stool" ? { ...c, blocker: null } : c)) };
const readyStool = stoolBusy.cards.find((c) => c.card === "stool")!;
expect("control: a ready step while the hands run another tap is on its face", onFace(catalog, stoolBusy, readyStool), true);
expect("not once queued", onFace(catalog, after(stoolBusy, whenReady(catalog, stoolBusy, "stool")), readyStool), false);
const stoolRuns: View = { ...stoolBusy, lanes: stoolBusy.lanes.map((l) => (l.lane === catalog.laneOf("stool") ? { ...l, running_card: "stool" } : l)) };
expect("not the card its lane runs", onFace(catalog, stoolRuns, readyStool), false);

// A row moves one entry past the next row whole: up before it, down after its last.
const runs3: View = { ...running, queue: [tapUntil(stool.card, stool.completions + 1), tapUntil("gather", 11), tapUntil("gather", 12)] };
expect("up from the gather row: before the stool", rowStep(runs3, 2, -1), 0);
expect("down from the stool: after the gather row's last", rowStep(runs3, 0, 1), 2);
expect("nothing above the top row", rowStep(runs3, 0, -1), null);

// A capped card is offered while a run fits under its cap: two left, two picks, then off Plan.
const capped: View = { ...base, cards: base.cards.map((c) => (c.card === "gather" ? { ...c, cap: 11 } : c)) };
const p1 = after(capped, whenReady(catalog, capped, "gather"));
const p2 = after(p1, whenReady(catalog, p1, "gather"));
expect("two runs fit", p2.queue, [tapUntil("gather", 10), tapUntil("gather", 11)]);
expect("then it is off Plan", [listed(p2).includes("gather"), whenReady(catalog, p2, "gather")], [false, null]);

// A row of runs with no other row to move past has no ≡.
{
  const handles = (v: View) => nextRows(ctx, v, plan, new NextOrder(ctx, document.createElement("div"), () => v, () => {})).filter((r) => r.classList.contains("next-row")).map((r) => r.querySelectorAll(".rule-handle").length);
  expect("one row of two runs: nothing to move past", handles(two), [0]);
  expect("control: with another card's row, each has one", handles(mixed), [1, 1, 1]);
}
