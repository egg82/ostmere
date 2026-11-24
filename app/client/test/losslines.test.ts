// A fight card that tells its losses from its own pools (CONTRACT.txt, "LOSS LINES"): its on-loss line is its own key's
// words, its lost entries in the chronicle come only from loss_pool, and a runner without one never draws from it; a
// fold note's count is drawn beside its words on its own day.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fightsStep } from "../fixtures/fights";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import { lostPool } from "../src/game/fights";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";
import { Story } from "../src/ui/story";
import type { FightInfo, JournalDay } from "../src/api/types";
import { rig, text as rigText } from "./journalrig";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const DEATHS = ["line.death.a", "line.death.b"];
const pooled = {
  ...fixtureContent,
  card_infos: fixtureContent.card_infos.map((c) => c.fight === null ? c
    : { ...c, fight: { ...c.fight, loses: [], wounds: [], lost_line_keys: [], loss_pool: DEATHS, loss_notes: ["note.gone.a"], on_loss_key: "line.on_loss" } }),
  standing_infos: fixtureContent.standing_infos.map((a) => a.fight === null ? a : { ...a, fight: { ...a.fight, lost_line_keys: ["line.lost.r"] } }),
  text_entries: [...fixtureContent.text_entries,
    { key: "line.death.a", text: "death a" }, { key: "line.death.b", text: "death b" }, { key: "line.lost.r", text: "raid lost" },
    { key: "line.on_loss", text: "a loss, the card's own way" }, { key: "note.gone.a", text: "gone a" }],
};

/** Every entry the story's chronicle holds, in order: the sheet opened on All and read. */
function chronicled(story: Story): string[] {
  story.book.opened();
  story.root.querySelector<HTMLButtonElement>('.chron-filter[data-filter="all"]')?.click();
  const got = [...story.root.querySelectorAll(".chron-all .chron-text")].map((n) => n.textContent ?? "");
  story.book.sheet.close();
  return got;
}

// The pool a runner's lost entries are worded from.
{
  const plain: FightInfo = { side: "s", threat: "t", loses: [], wounds: [], won_line_keys: [], lost_line_keys: ["a"], loss_pool: null, loss_notes: null, on_loss_key: null };
  expect("a plain fight: its lost_line_keys", lostPool(plain), ["a"]);
  expect("a pooled fight: its loss_pool", lostPool({ ...plain, lost_line_keys: [], loss_pool: ["x", "y"], loss_notes: ["n"], on_loss_key: "k" }), ["x", "y"]);
  expect("no fight: none", lostPool(null), []);
}

// The card's on-loss line is its own key's words, and nothing of ui.fight.on_loss or on_wound.
{
  const { ctx } = testContext(undefined, new Catalog(pooled));
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  const view = fightsStep("fight", 100).view;
  cards.update(view, null);
  const loss = cards.root.querySelector<HTMLElement>(".fight .fight-loss");
  expect("the on-loss line", loss?.textContent, "a loss, the card's own way");
  expect("drawn", loss?.hidden, false);
}

// The chronicle: the pooled card's lost entries come only from loss_pool, the standing fight's never do.
{
  const { ctx } = testContext(undefined, new Catalog(pooled));
  const story = new Story(ctx);
  const view = fightsStep("fight", 100).view;
  const later = fightsStep("fightlater", 110).view;   // three more fought, one more lost, each runner
  story.update(later, view);
  const lines = chronicled(story);
  const deaths = lines.filter((l) => l.startsWith("death "));
  expect("the hunt's one loss reads from its pool", deaths.length, 1);
  expect("the hunt reads nothing of ui.fight.lost", lines.filter((l) => l === "Hunt the ridge: lost").length, 0);
  expect("the raid's one loss is its own pool's, never a death", lines.filter((l) => l === "raid lost").length, 1);
}

// A fold note: its count beside its words, as digits in a node of its own; every other note has none.
{
  const folded: JournalDay = { day: 2, marks: [], day_notes: [
    { subject: "hunt", slot: "loss", key: "wk_rain", hand: "pencil", sketch: null, count: null },
    { subject: "hunt", slot: "fold", key: "wk_roof", hand: "pencil", sketch: null, count: 4 }] };
  const r = rig({ notes: [], days: [folded], newestDay: null });
  r.open();
  const notes = [...r.sheet().querySelectorAll<HTMLElement>(".journal-note")];
  expect("both notes, in pencil", notes.map((n) => n.className), ["journal-note hand-pencil", "journal-note hand-pencil"]);
  expect("the count beside the fold's words only", notes.map((n) => n.querySelector(".journal-count")?.textContent ?? null), [null, "4"]);
  expect("never inside the words", notes[1]?.querySelector(".journal-words")?.textContent, rigText("wk_roof"));
}
