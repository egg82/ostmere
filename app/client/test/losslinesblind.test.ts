// LOSS LINES, from api/contract/ alone (docs/design/week-four-plan.md, item 2; mutants in MUTANTS.txt beside the
// composer tests): the pool a runner's lost entries read from, the chronicle's wording of them, and the card's own
// on-loss line.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fightsStep } from "../fixtures/fights";
import type { Content, FightInfo, View } from "../src/api/types";
import { lostPool } from "../src/game/ledger/fights";
import { Catalog } from "../src/game/page/catalog";
import { FightPanel } from "../src/ui/ledger/fightpanel";
import { Story } from "../src/ui/story/story";
import { fixtureContent } from "../fixtures/content";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const POOL = ["line.loss.a", "line.loss.b", "line.loss.c"];
const plainFight = (fixtureContent.card_infos.find((c) => c.card === "hunt")?.fight ?? null) as FightInfo;
const pooledFight: FightInfo = { ...plainFight, loses: [], wounds: [], lost_line_keys: [], loss_pool: POOL, loss_notes: ["note.a", "note.b"], on_loss_key: "line.on_loss" };

// lostPool: loss_pool when set, else lost_line_keys, nothing for no fight.
expect("a pooled fight's pool", lostPool(pooledFight), POOL);
expect("a plain fight with lines", lostPool({ ...plainFight, lost_line_keys: ["x", "y"] }), ["x", "y"]);
expect("a plain fight with none", lostPool(plainFight), []);
expect("no fight", lostPool(null), []);
expect("an unset fight", lostPool(undefined), []);

const lineText = (k: string): string => `text of ${k}`;
const withText: Content = {
  ...fixtureContent,
  card_infos: fixtureContent.card_infos.map((c) => c.card === "hunt" ? { ...c, fight: pooledFight } : c),
  standing_infos: fixtureContent.standing_infos.map((s) => ({ ...s, fight: { ...(s.fight as FightInfo), lost_line_keys: ["line.lost.r"] } })),
  text_entries: [...fixtureContent.text_entries.filter((e) => e.key !== "ui.fight.since"),
    ...[...POOL, "line.on_loss", "line.lost.r"].map((key) => ({ key, text: lineText(key) })),
    { key: "ui.fight.since", text: "{runner}: {won} won, {lost} lost of {fought}" }],
};

// The chronicle: the pooled runner's lost entries come only from its pool, each key once per round of the pool; the
// plain runner's never do.
{
  const first = fightsStep("fight", 100).view;
  const grown = (hunt: [number, number], raiders: [number, number]): View => ({
    ...first, fights: first.fights.map((f) => f.runner === "hunt" ? { ...f, fought: hunt[0], lost: hunt[1] } : { ...f, fought: raiders[0], lost: raiders[1] }),
  });
  const { ctx } = testContext(undefined, new Catalog(withText));
  const story = new Story(ctx);
  const v0 = grown([4, 1], [31, 2]);
  const v1 = grown([7, 4], [34, 5]);
  const v2 = grown([10, 7], [37, 8]);
  story.update(v1, v0);
  story.update(v2, v1);
  story.book.opened();
  story.root.querySelector<HTMLButtonElement>('.chron-filter[data-filter="all"]')?.click();
  const lines = [...story.root.querySelectorAll(".chron-all .chron-text")].map((n) => n.textContent ?? "");
  const poolTexts = POOL.map(lineText);
  const huntLines = lines.filter((l) => poolTexts.includes(l));
  expect("six lost hunt entries, all from the pool", huntLines.length, 6);
  expect("no other line is a hunt entry", lines.filter((l) => l.startsWith("text of line.loss")).length, 6);
  // The hunt had one lost fight already, so these are its lost fights k = 1..6: round 0 holds k = 1, 2; round 1 k = 3..5.
  expect("round 0's two draws differ", new Set(huntLines.slice(0, 2)).size, 2);
  expect("round 1 uses each key once", new Set(huntLines.slice(2, 5)).size, 3);
  const plain = lines.filter((l) => l === lineText("line.lost.r"));
  expect("the plain runner's six lost entries read its lost_line_keys", plain.length, 6);
  expect("nothing reads ui.fight.lost for either", lines.filter((l) => l === "Hunt the ridge: lost" || l === "Raiders at the stores: lost").length, 0);
}

// The card's own on-loss line: its words, once, in place of the costs and wounds line; a plain fight's is as before.
{
  const { ctx } = testContext(undefined, new Catalog(withText));
  const catalog = ctx.catalog;
  const own = new FightPanel(catalog, pooledFight);
  const node = own.root.querySelector(".fight-loss");
  expect("the card's words", node?.textContent, lineText("line.on_loss"));
  expect("drawn once", own.root.querySelectorAll(".fight-loss").length, 1);
  const plain = new FightPanel(catalog, plainFight);
  expect("a plain fight keeps FIGHTS' line", plain.root.querySelector(".fight-loss")?.textContent, "a loss costs 3 Dead wood; lose, and you're hurt +1");
}
