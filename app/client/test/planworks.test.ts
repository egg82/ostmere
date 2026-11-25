// Every option Plan offers works as worded (docs/decisions/principles.md): a card already running adds an entry that
// pops at its landing and a card on a ruled lane is refused by the server (CONTRACT.txt, "A LANE RUN BY RULES"), so
// neither is listed or taken.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { planCards, whenReady } from "../src/game/queue";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const ended = fixtureStep("restoffer", 100).view;
const listed = (v: View) => planCards(catalog, v).map((c) => c.card);

const stool = ended.cards.find((c) => c.card === "stool")!;
expect("control: the idle stool is listed and taken", [listed(ended).includes("stool"), whenReady(catalog, ended, "stool") !== null], [true, true]);
const lane = catalog.laneOf("stool");
const running: View = { ...ended, lanes: ended.lanes.map((l) => (l.lane === lane ? { ...l, running_card: "stool" } : l)) };
expect("a card running on its lane is not listed", listed(running).includes("stool"), false);
expect("nor taken", whenReady(catalog, running, "stool"), null);

const fetch: Card = { ...stool, card: "fetch", cap: null, completions: 0 };
const fetchView: View = { ...ended, cards: [...ended.cards, fetch] };
expect("control: fetch is a step on a lane", [catalog.cards.get("fetch")?.presentation, catalog.ruled("fetch")], ["narrative", true]);
expect("a card on a ruled lane is not listed", listed(fetchView).includes("fetch"), false);
expect("nor taken", whenReady(catalog, fetchView, "fetch"), null);
