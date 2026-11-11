// A skill's prestige on the page (docs/design/prestige-phases.md, "What the page shows"): the row below its top says
// when the forecast tops it out; at its top it is marked, counts the levels waiting and holds the Push past control,
// the lesson's trigger, which shows nowhere earlier; mastered at its top it has no control; its level is the
// one counted across phases, which never falls at a click, as its next pay is; Undo and Choose follow undo_open and
// pick_owed. The sheet lists the menu with ranks and plain before/after numbers, and each button sends the verb. A
// return's line names a skill that reached its top since the last view, never what the wait missed.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { prestigeStep, withPrestige } from "../fixtures/prestige";
import type { SkillBar, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { PRESTIGE } from "../src/game/lessons";
import { changeText, toppedSince } from "../src/game/prestige";
import { UI } from "../src/game/text";
import { Skills } from "../src/ui/skills";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(withPrestige(fixtureContent));
const { text, format } = catalog;
const AT = 100;
const H = 3600;

function drawn(view: View) {
  const { ctx, got } = testContext(undefined, catalog);
  const part = new Skills(ctx);
  part.update(view, null);
  part.tick(AT);
  const row = (skill: string) => {
    const node = [...part.root.querySelectorAll<HTMLElement>(".skill")].find((n) => n.querySelector(".skill-name")?.textContent === catalog.skillLabel(skill));
    if (!node) throw new Error(`no row for ${skill}`);
    const act = node.querySelector<HTMLButtonElement>(".skill-foot .primary");
    const undo = node.querySelector<HTMLButtonElement>(".skill-foot .quiet");
    const foot = node.querySelector<HTMLElement>(".skill-foot");
    return {
      node, act, undo, level: node.querySelector(".skill-level")?.textContent, next: node.querySelector(".skill-next")?.textContent,
      note: foot?.hidden ? null : node.querySelector(".skill-note")?.textContent, top: node.classList.contains("at-top"),
      shownAct: act && !act.hidden ? act.textContent : null, teach: act?.dataset["teach"] ?? null, shownUndo: undo ? !undo.hidden : false,
    };
  };
  return { part, row, got };
}

const prestige = prestigeStep("prestige", AT).view;
{
  const { row } = drawn(prestige);
  const below = row("foraging"), top = row("firecraft"), mastered = row("carving");
  expect("below the top: the forecast's time to it", below.note, text.fill(UI.prestigeTopsOut, { d: format.duration(2 * H + 15 * 60) }));
  expect("below the top: no control, so no lesson trigger", [below.shownAct, below.teach], [null, null]);
  expect("at the top: marked, and says so", [top.top, top.next], [true, text.get(UI.prestigeTop)]);
  expect("at the top: the levels waiting and Prestige, the lesson's trigger", [top.note, top.shownAct, top.teach],
    [text.fill(UI.prestigeWaiting, { n: "6" }), text.get(UI.prestigeButton), "prestige"]);
  expect("mastered at its top: says so, no control, no foot", [mastered.next, mastered.shownAct, mastered.note, mastered.top],
    [text.get(UI.prestigeMastered), null, null, false]);
  expect("phase 3: the counted level, with no phase beside it", mastered.level, text.fill(UI.level, { n: "30" }));
  expect("phase 1: the level alone", below.level, text.fill(UI.level, { n: "2" }));
}
{
  // no forecast entry: no "tops out in", and the foot stays shut
  const { row } = drawn({ ...prestige, forecast: { ...prestige.forecast!, tops_out: [] } });
  expect("not in the forecast: no time, no foot", row("foraging").note, null);
}
{
  const { row, got } = drawn(prestigeStep("prestigeclicked", AT).view);
  const r = row("firecraft");
  expect("after the click: Undo, no Prestige", [r.shownUndo, r.shownAct], [true, null]);
  r.undo?.click();
  expect("Undo sends undo_pick", got.decided, [{ kind: "undo_pick", skill: "firecraft" }]);
}
{
  const r = drawn(prestigeStep("prestigeowed", AT).view).row("firecraft");
  expect("a pick owed: Choose, never the lesson's trigger", [r.shownAct, r.teach, r.shownUndo], [text.get(UI.prestigeChoose), null, false]);
}
{
  // the next pay counts levels across phases: foraging pays at 3, so phase 2's level 1 (counted 11) has nothing ahead
  const bar = prestige.skills.find((s) => s.skill === "foraging") as SkillBar;
  const phase2: SkillBar = { ...bar, level: 1, prestige: { ...bar.prestige!, phase: 2, level_counted: 11 } };
  const r = drawn({ ...prestige, skills: [phase2] }).row("foraging");
  expect("counted past every pay: nothing ahead", r.next, text.get(UI.skillNone));
}

// The sheet: opened from the row's control, the menu with its ranks and plain numbers, and a button per node.
{
  const { part, row, got } = drawn(prestige);
  row("firecraft").act?.click();
  const sheet = part.root.querySelector<HTMLDialogElement>(".prestige-sheet");
  expect("the control opens the sheet", sheet?.open, true);
  const nodes = [...(sheet?.querySelectorAll<HTMLElement>(".prestige-node") ?? [])];
  expect("one row per menu node", nodes.length, 3);
  expect("the first node's rank", nodes[0]?.querySelector(".prestige-rank")?.textContent, "1/5");
  expect("its change as plain numbers", nodes[0]?.querySelector(".prestige-change")?.textContent,
    text.fill(UI.prestigeCap, { store: catalog.storeTitle("wood"), before: "44", after: "48" }));
  expect("the start of the next phase", sheet?.querySelector(".prestige-intro")?.textContent, text.fill(UI.prestigeStarts, { before: "10", after: "19", n: "16" }));
  nodes[1]?.querySelector<HTMLButtonElement>(".primary")?.click();
  expect("a node's button sends prestige", got.decided, [{ kind: "prestige", skill: "firecraft", node: "two" }]);
  part.update(prestigeStep("prestigeclicked", AT).view, prestige);
  expect("after the click the sheet says the phase began and offers Undo", [sheet?.querySelector(".prestige-intro")?.textContent, sheet?.querySelector(".prestige-undo .quiet")?.textContent],
    [text.fill(UI.prestigeBegun, { n: "17" }), text.get(UI.prestigeUndo)]);
}

// Moving a pick: after a click the row offers Picks, the sheet lists the picked node with Move, choosing it says what it
// costs and offers the menu's nodes, and a node's button sends move_pick. A parked rank is listed with its push.
{
  const clicked = prestigeStep("prestigeclicked", AT).view;
  const { part, row, got } = drawn(clicked);
  const r = row("firecraft");
  const picks = r.node.querySelector<HTMLButtonElement>(".skill-foot .picks");
  expect("after the click: Picks shows", [picks?.hidden, picks?.textContent], [false, text.get(UI.prestigePicks)]);
  expect("below the top and with nothing picked: no Picks", [row("foraging").node.querySelector<HTMLButtonElement>(".skill-foot .picks")?.hidden], [true]);
  picks?.click();
  const sheet = part.root.querySelector<HTMLDialogElement>(".prestige-sheet");
  const name = (n: HTMLElement | null | undefined) => n?.querySelector(".prestige-name")?.textContent;
  const listed = [...(sheet?.querySelectorAll<HTMLElement>(".prestige-node") ?? [])];
  expect("the picked node is listed with Move", [listed.length, name(listed[0]), listed[0]?.querySelector("button")?.textContent],
    [1, catalog.label("node.one"), text.get(UI.prestigeMove)]);
  listed[0]?.querySelector("button")?.click();
  expect("Move says what it costs", sheet?.querySelector(".prestige-intro")?.textContent, text.fill(UI.prestigeMoveTo, { node: catalog.label("node.one") }));
  const places = [...(sheet?.querySelectorAll<HTMLElement>(".prestige-node .primary") ?? [])];
  expect("each other menu node is a place, never the node moved", places.map((b) => b.dataset["node"]), ["two", "three"]);
  places[0]?.click();
  expect("a place sends move_pick", got.decided, [{ kind: "move_pick", skill: "firecraft", node: "one", to: "two" }]);
  const parked = prestigeStep("prestigeparked", AT).view;
  expect("only a parked rank: Picks still shows, to reach its line", drawn(parked).row("firecraft").node.querySelector<HTMLButtonElement>(".skill-foot .picks")?.hidden, false);
  part.update(parked, clicked);
  const lines = [...(sheet?.querySelectorAll<HTMLElement>(".prestige-parked") ?? [])].map((n) => n.textContent);
  expect("a parked rank says when it returns", lines, [text.fill(UI.prestigeParked, { node: catalog.label("node.two"), n: "2" })]);
  const soon = { ...parked, skills: parked.skills.map((s) => (s.skill === "firecraft" ? { ...s, prestige: { ...s.prestige!, parked: [{ node: "two", due: 3 }] } } : s)) };
  part.update(soon, parked);
  expect("at the next push it says so", [...(sheet?.querySelectorAll<HTMLElement>(".prestige-parked") ?? [])].map((n) => n.textContent),
    [text.fill(UI.prestigeParkedOne, { node: catalog.label("node.two") })]);
}

// Each target kind's numbers: a make per minute, a card's time per completion, a cap in items.
{
  const menu = prestige.skills.find((s) => s.skill === "firecraft")?.prestige?.menu_nodes ?? [];
  expect("a make, per minute", changeText(catalog, menu[1]!), text.fill(UI.prestigeMake,
    { store: catalog.storeTitle("warmth"), runner: catalog.cardLabel("tend"), before: format.perMinute(300_000), after: format.perMinute(330_000) }));
  expect("a card's work, as time per completion", changeText(catalog, menu[2]!), text.fill(UI.prestigeWork,
    { card: catalog.cardLabel("gather"), before: format.duration(5 / 1.2), after: format.duration(5 / 1.3) }));
}

// The return's line: a skill at its top now and below it before; none on a first view or one already at its top.
{
  const away = prestigeStep("prestigeaway", AT).view;
  expect("topped since the last view", toppedSince(away, prestige), [{ skill: "firecraft", at: AT - 5 * H }]);
  expect("no last view: nothing", toppedSince(null, prestige), []);
  expect("already at its top: nothing", toppedSince(prestige, prestige), []);
}
expect("the lesson is data like the others", PRESTIGE, "prestige");
