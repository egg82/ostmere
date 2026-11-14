// The page's fights (docs/design/opening-screen.md, "Fights"): a fight card's odds, strengths and on-loss line; a
// strength's entries opened by a tap (never by hover); a standing fight in the ledger with its tally; the arrival
// fight entries in the chronicle, never the strip. All of it off while the `combat` feature is.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fightsStep } from "../fixtures/fights";
import type { View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";
import { Ledger } from "../src/ui/ledger";
import { Story } from "../src/ui/story";
import { Catalog } from "../src/game/catalog";
import { fixtureContent } from "../fixtures/content";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const view = fightsStep("fight", 100).view;
const off: View = { ...view, unlocked: view.unlocked.filter((u) => u.id !== "combat") };
const text = (n: Element | null | undefined): string => n?.textContent ?? "";

// The fight card: odds as the smallest exact pair, the two strengths as buttons, the cost of a loss.
{
  const { ctx } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  cards.update(off, null);
  const hidden = cards.root.querySelector<HTMLElement>(".fight");
  expect("the feature off: the fight's parts are hidden", hidden?.hidden, true);
  cards.update(view, off);
  const fight = cards.root.querySelector<HTMLElement>(".fight");
  expect("the fight shows once combat is on", fight?.hidden, false);
  expect("odds", text(fight?.querySelector(".fight-odds")), "2 in 5 lost");
  expect("vs", text(fight?.querySelector(".fight-vs")), "Your hands 8, Wolves 9");
  expect("what a loss costs and adds", text(fight?.querySelector(".fight-loss")), "a loss costs 3 Dead wood, 1 Energy");
  expect("the odds sit beside the tap, not inside it", cards.root.querySelector(".card-tap .fight"), null);
  const entries = fight?.querySelector<HTMLElement>(".fight-entries");
  expect("entries are closed until tapped", entries?.hidden, true);
  const [power, threat] = Array.from(fight?.querySelectorAll(".fight-strength") ?? []);
  expect("two strength buttons", [text(power), text(threat)], ["8", "9"]);
  (power as HTMLButtonElement).click();
  expect("a tap opens the entries, the base first", Array.from(entries?.querySelectorAll(".fight-entry") ?? [], text), ["base6", "Hatchet+50%", "Foraging+25%", "Stool50%+12.5%", "Cold×0.8"]);
  expect("and says so", power?.getAttribute("aria-expanded"), "true");
  (threat as HTMLButtonElement).click();
  expect("the other strength replaces it", Array.from(entries?.querySelectorAll(".fight-entry") ?? [], text), ["base9"]);
  (threat as HTMLButtonElement).click();
  expect("a second tap closes it", entries?.hidden, true);
  cards.update({ ...view, fights: view.fights.map((f) => ({ ...f, loss_bp: 2000 })) }, view);
  expect("a redraw with new odds shows them", text(cards.root.querySelector(".fight-odds")), "1 in 5 lost");
}

// Blind until learned: a runner never fought shows its odds as unknown on the card, in its open strength sheet and in
// the ledger; from the first fight on, the served odds.
{
  const oddsFigure = /\d+ in \d+ lost|% lost/;
  const fought = (n: number): View => ({ ...view, fights: view.fights.map((f) => ({ ...f, fought: n, lost: 0 })) });
  for (const [n, card, standing] of [[0, "odds unknown until fought", "odds unknown until fought"], [1, "2 in 5 lost", "7.5% lost"]] as const) {
    const { ctx } = testContext();
    const cards = new Cards(ctx, new NewMarks());
    const ledger = new Ledger(ctx);
    document.body.replaceChildren(cards.root, ledger.root);
    cards.update(fought(n), null);
    ledger.update(fought(n), null);
    const fight = cards.root.querySelector<HTMLElement>(".fight");
    fight?.querySelector<HTMLButtonElement>(".fight-strength")?.click();
    const row = ledger.root.querySelector(".threat");
    expect(`fought ${n}: the card's odds`, text(fight?.querySelector(".fight-odds")), card);
    expect(`fought ${n}: the ledger's odds`, text(row?.querySelector(".fight-odds")), standing);
    const strengths = (x: Element | null | undefined) => Array.from(x?.querySelectorAll(".fight-strength") ?? [], text);
    expect(`fought ${n}: the card's strengths`, [text(fight?.querySelector(".fight-vs")), strengths(fight)], n === 0 ? ["Your hands 8, Wolves unknown", ["8"]] : ["Your hands 8, Wolves 9", ["8", "9"]]);
    expect(`fought ${n}: the ledger's strengths`, [text(row?.querySelector(".fight-vs")), strengths(row)], n === 0 ? ["Your hands 8, Raiders unknown", ["8"]] : ["Your hands 8, Raiders 40", ["8", "40"]]);
    expect(`fought ${n}: an odds figure on the card, its sheet or the ledger`, [fight, row].map((x) => oddsFigure.test(text(x))), n === 0 ? [false, false] : [true, true]);
  }
}

// The strength sheet: every served entry of every strength, in order, each with its source's label (the base none), under
// the label of the side or threat it belongs to. Expected labels are written out here, not read from the page's code.
{
  const { ctx } = testContext();
  const labelOf: Record<string, string> = { hatchet: "Hatchet", foraging: "Foraging", stool: "Stool", cold: "Cold", dusk_ramp: "Dusk" };
  const cards = new Cards(ctx, new NewMarks());
  const ledger = new Ledger(ctx);
  document.body.replaceChildren(cards.root, ledger.root);
  cards.update(view, null);
  ledger.update(view, null);
  const panels: Array<[Element | null, string]> = [[cards.root.querySelector(".fight"), "wolves"], [ledger.root.querySelector(".threat .fight"), "raiders"]];
  let seen = 0;
  for (const [panel, threat] of panels) {
    const fight = view.fights.find((f) => f.threat === threat);
    const sides = [["Your hands", fight?.power], [threat === "wolves" ? "Wolves" : "Raiders", fight?.threat_strength]] as const;
    const buttons = Array.from(panel?.querySelectorAll<HTMLButtonElement>(".fight-strength") ?? []);
    sides.forEach(([owner, strength], i) => {
      buttons[i]?.click();
      const rows = Array.from(panel?.querySelectorAll(".fight-entries .fight-entry") ?? [], (r) => [text(r.querySelector(".fight-source")), text(r.querySelector(".fight-amount"))]);
      const want = (strength?.sources ?? []).map((s) => (s.source === null ? "base" : labelOf[s.source]));
      expect(`${threat} ${owner}: the sheet is named`, text(panel?.querySelector(".fight-entries .fight-owner")), owner);
      expect(`${threat} ${owner}: every served entry is a row`, rows.map((r) => r[0]), want);
      seen += rows.length;
      buttons[i]?.click();
    });
  }
  expect("the check saw the entries (control: it cannot pass on nothing)", seen >= 8, true);
}

// A share has its place between source and amount: a partial share on an entry held while a card runs shows it, a whole
// share and a permanent entry show none. The expected rows are written out here.
{
  const { ctx } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  const held = (source: string, amount_bp: number, share_bp: number | null) => ({ source, form: "add_bp" as const, amount_bp, share_bp });
  const sources = [{ source: null, form: "base" as const, amount_bp: 6, share_bp: null }, held("hatchet", 5000, null), held("stool", 1250, 5000), held("rest", 500, 10000), held("foraging", 2500, null)];
  cards.update({ ...view, fights: view.fights.map((f) => (f.threat === "wolves" ? { ...f, power: { value: 8, sources } } : f)) }, null);
  const panel = cards.root.querySelector(".fight");
  panel?.querySelector<HTMLButtonElement>(".fight-strength")?.click();
  const rows = Array.from(panel?.querySelectorAll(".fight-entries .fight-entry") ?? [], (r) => [text(r.querySelector(".fight-source")), text(r.querySelector(".fight-share")), text(r.querySelector(".fight-amount"))]);
  expect("a partial share sits in its row; a whole share and a permanent entry have none", rows.map((r) => [r[0], r[1]]), [["base", ""], ["Hatchet", ""], ["Stool", "50%"], ["Rest", ""], ["Foraging", ""]]);
  const order = Array.from(panel?.querySelectorAll(".fight-entries .fight-entry")[2]?.children ?? [], (c) => c.className);
  expect("the share is between source and amount", order, ["fight-source", "fight-share", "fight-amount"]);
}

// The standing fight, in the ledger with its tally.
{
  const { ctx } = testContext();
  const ledger = new Ledger(ctx);
  document.body.replaceChildren(ledger.root);
  ledger.update(off, null);
  expect("no threats while the feature is off", ledger.root.querySelector(".threat"), null);
  ledger.update(view, off);
  const row = ledger.root.querySelector(".threat");
  expect("the threat's name", text(row?.querySelector(".threat-name")), "Raiders at the stores");
  expect("its odds", text(row?.querySelector(".fight-odds")), "7.5% lost");
  expect("its tally", text(row?.querySelector(".fight-tally")), "31 fought, 2 lost");
  expect("the group shows the ledger", ledger.root.hidden, false);
}

/** Every entry the story's chronicle holds, in order: the sheet opened on All and read. */
function chronicled(story: Story): string[] {
  story.book.opened();
  story.root.querySelector<HTMLButtonElement>('.chron-filter[data-filter="all"]')?.click();
  const got = [...story.root.querySelectorAll(".chron-all .chron-text")].map((n) => n.textContent ?? "");
  story.book.sheet.close();
  return got;
}

function causesOf(story: Story): string[] {
  story.book.opened();
  story.root.querySelector<HTMLButtonElement>('.chron-filter[data-filter="all"]')?.click();
  const got = [...story.root.querySelectorAll(".chron-all .chron-cause")].map((n) => n.textContent ?? "");
  story.book.sheet.close();
  return got;
}

// The chronicle: a window's entries, exactly the lost count of them reading lost; a long one a summary. None reaches the
// strip.
{
  const { ctx } = testContext();
  const stripped: string[] = [];
  ctx.arrivals = { ...ctx.arrivals, line: (nodes) => { stripped.push(text(nodes[0])); } };
  const story = new Story(ctx);
  const later = fightsStep("fightlater", 110).view;   // three more fought, one more lost, each runner
  story.update(later, view);
  let lines = chronicled(story);
  expect("three entries a runner", lines.length, 6);
  expect("one of each runner lost", [lines.filter((l) => l === "Hunt the ridge: lost").length, lines.filter((l) => l === "Raiders at the stores: lost").length], [1, 1]);
  expect("a line that names its runner has no cause beneath it", causesOf(story).length, 0);
  story.update(fightsStep("fightmany", 120).view, later);
  lines = chronicled(story).slice(6);
  expect("a long window is one summary line each", lines, ["37 fought, 4 lost", "37 fought, 4 lost"]);
  story.update(later, null);
  expect("the first view writes nothing", chronicled(story).length, 8);
  expect("no fight reaches the strip", stripped, []);
}

// A runner with pools: its entries are its own lines, the losses exactly the lost count, no line twice before the
// pool is spent; a runner without keeps ui.fight.*; the summary carries the won count and the runner.
{
  const pooled = {
    ...fixtureContent,
    card_infos: fixtureContent.card_infos.map((c) => c.fight === null ? c
      : { ...c, fight: { ...c.fight, won_line_keys: ["line.won.a", "line.won.b", "line.won.c"], lost_line_keys: ["line.lost.a"] } }),
    text_entries: [...fixtureContent.text_entries.filter((e) => e.key !== "ui.fight.since"),
      { key: "line.won.a", text: "won a" }, { key: "line.won.b", text: "won b" }, { key: "line.won.c", text: "won c" },
      { key: "line.lost.a", text: "lost a" }, { key: "ui.fight.since", text: "{runner}: {won} won, {lost} lost of {fought}" }],
  };
  const { ctx } = testContext(undefined, new Catalog(pooled));
  const story = new Story(ctx);
  const later = fightsStep("fightlater", 110).view;
  story.update(later, view);
  let lines = chronicled(story);
  const hunt = lines.filter((l) => l.startsWith("won ") || l.startsWith("lost "));
  expect("the hunt's three entries come from its pools", hunt.length, 3);
  expect("one reads lost, from the lost pool", hunt.filter((l) => l === "lost a").length, 1);
  expect("the two wins are two different lines", new Set(hunt.filter((l) => l.startsWith("won "))).size, 2);
  expect("the raiders keep ui.fight.*", lines.filter((l) => l.startsWith("Raiders at the stores: ")).length, 3);
  expect("a pool's line names no runner, so its cause does", causesOf(story), ["Hunt the ridge", "Hunt the ridge", "Hunt the ridge"]);
  story.update(fightsStep("fightmany", 120).view, later);
  lines = chronicled(story).slice(6);
  expect("the summary names the runner and the wins", lines[0], "Hunt the ridge: 33 won, 4 lost of 37");
}
