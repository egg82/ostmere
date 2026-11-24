// Hurt is a level the player can see (docs/decisions/combat.md): a store a fight wounds shows its level, whole items
// rounded up (any hurt at all reads at least 1), through the chip's own words ("hurt 2"), on the fight card's loss line
// ("lose, and you're hurt +1"). A chip on a store no fight wounds, and a store a loss only spends, read as they did.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { Q, fixtureContent } from "../fixtures/content";
import { fightsStep, withHurtChip } from "../fixtures/fights";
import { fixtureStep } from "../fixtures/steps";
import type { Content, FightInfo, StoreLevel, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { FightPanel } from "../src/ui/fightpanel";
import { Story } from "../src/ui/story";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const wound: FightInfo = { side: "hands", threat: "wolves", loses: [], wounds: [{ store: "hurt", quantity: Q }], won_line_keys: [], lost_line_keys: [], loss_pool: null, loss_notes: null, on_loss_key: null };
const content: Content = withHurtChip(fixtureContent);
const catalog = new Catalog(content);

/** The hurt level as the server serves it: `items` of hurt at AT, falling `perHour` items an hour. */
function hurtLevel(items: number, perHour: number): StoreLevel {
  return { store: "hurt", segment: { start: AT, start_value: items * Q, rate: Math.round(-perHour * Q / 3600), limit: 0 } };
}

function withHurt(items: number, perHour = 0): View {
  const base = fixtureStep("mid", AT).view;
  return { ...base, chips: [...base.chips, "hurt"], levels: [hurtLevel(items, perHour)] };
}

const chipWords = (story: Story): string[] => Array.from(story.head.querySelectorAll(".chip"), (n) => n.textContent ?? "");

// The chip: its word and the level beside it; the level follows the store as it heals.
{
  const story = new Story(testContext(undefined, catalog).ctx);
  story.update(withHurt(1.5), null);
  expect("hurt shows its level beside its name, cold none", chipWords(story), ["Cold-20% hands speed", "hurt 2"]);
  story.update(withHurt(0.25), null);
  expect("a quarter hurt reads 1, never 0 while the chip is on", chipWords(story), ["Cold-20% hands speed", "hurt 1"]);
  story.update(withHurt(2.5, 1), null);
  expect("a level at the view's clock", chipWords(story), ["Cold-20% hands speed", "hurt 3"]);
  story.tick(AT + 2 * 3600);
  expect("and as the heal runs on between views", chipWords(story), ["Cold-20% hands speed", "hurt 1"]);
}

// The fight card's loss line says what happens to you in the chip's measure; what a loss spends stays a cost.
{
  const line = (info: FightInfo): string => { const p = new FightPanel(catalog, info); return p.root.querySelector(".fight-loss")?.textContent ?? ""; };
  expect("a wound is a level", line(wound), "lose, and you're hurt +1");
  expect("a bigger one", line({ ...wound, wounds: [{ store: "hurt", quantity: 2 * Q }] }), "lose, and you're hurt +2");
  expect("a spend is still a cost", line({ ...wound, wounds: [], loses: [{ store: "wood", quantity: 3 * Q }] }), "a loss costs 3 Dead wood");
  expect("both, each in its own words", line({ ...wound, loses: [{ store: "wood", quantity: 3 * Q }] }), "a loss costs 3 Dead wood; lose, and you're hurt +1");
}
