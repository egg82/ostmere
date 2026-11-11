// The split a mix runs now (CONTRACT.txt, "SPENT", THE CLIENT MUST): under the hands strip's bar while a card of the
// running mix is paused or spent, each card at share_bp plus its gains with the source named, the stopped card greyed
// and at 0; nothing of it while the splits match, its room kept once it has come. The bar the player set never moves.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { runningNow } from "../src/game/spent";
import { fixtureContent } from "../fixtures/content";
import { Hands } from "../src/ui/hands";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const hands = new Hands(testContext().ctx);
const strip = (): HTMLElement => {
  const node = hands.root.querySelector(".running-now");
  if (!node) throw new Error("the hands strip holds no running-now row");
  return node as HTMLElement;
};
const keys = (): string[] => [...strip().querySelectorAll(".town-key-item")].map((n) => n.textContent ?? "");
const setBar = (): string => hands.root.querySelector(".share-track")?.textContent ?? "";
const base = fixtureStep("mid", 100).view;
const [stop, other] = base.cards.filter((c) => c.share_bp > 0);
if (!stop || !other) throw new Error("fixture: the running mix holds fewer than two cards");
const name = (card: string): string => catalog.cardLabel(card);
const pct = (bp: number): string => catalog.format.share(bp);

const stopped = (run: "paused" | "spent"): View => ({
  ...base,
  cards: base.cards.map((c) => (c.card === stop.card ? { ...c, run, spent_store: run === "spent" ? "wood" : null }
    : c.card === other.card ? { ...c, gained: [{ card: stop.card, share_bp: stop.share_bp }] } : c)),
});

expect("control: no card stopped, the splits match", runningNow(catalog, base, "hands"), null);
hands.update(base);
expect("matching splits: the row takes no room before it first comes", strip().hidden, true);
const before = setBar();

hands.update(stopped("paused"));
expect("a paused card: the row shows", [strip().hidden, strip().classList.contains("matched")], [false, false]);
const line = (c: (typeof base.cards)[number]): string => (c.card === stop.card ? `${name(c.card)} waiting`
  : c.card === other.card ? `${name(c.card)} ${pct(c.share_bp + stop.share_bp)} · +${pct(stop.share_bp)} from ${name(stop.card)}`
    : `${name(c.card)} ${pct(c.share_bp)}`);
expect("each line names its source; the paused card waits at 0", keys(), base.cards.filter((c) => c.share_bp > 0).map(line));
expect("the stopped card's slice is greyed", strip().querySelectorAll(".town-seg.stopped").length, 1);
expect("the bar the player set is unchanged", setBar(), before);

hands.update(stopped("spent"));
expect("a spent card reads the same in the split", keys(), base.cards.filter((c) => c.share_bp > 0).map(line));

hands.update(base);
expect("matched again: the row shows nothing but keeps its room", [strip().hidden, strip().classList.contains("matched")], [false, true]);
