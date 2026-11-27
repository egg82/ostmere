// A working's chain on the page (contract/spells.txt, "SPELLS"): its reach on its face from View.chains, the number a
// button whose sources open the base first; nothing drawn while the view serves no chain for it; and each link line in
// the chronicle only, live or on a return, one entry per line, read from ChainInfo and never from the text.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fightsStep } from "../fixtures/fights";
import type { Content, LogLine, View } from "../src/api/types";
import { NewMarks } from "../src/game/lessons/marks";
import { awayLines, liveLines } from "../src/game/book/awaylines";
import { Cards } from "../src/ui/cards/cards";
import { Catalog } from "../src/game/page/catalog";
import { fixtureContent } from "../fixtures/content";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const LINKS = ["l_link_1", "l_link_next"];
const content: Content = {
  ...fixtureContent,
  card_infos: fixtureContent.card_infos.map((c) => (c.card === "hunt" ? { ...c, fight: null, chain: { runner: "raiders", link_line_keys: LINKS } } : c)),
  text_entries: [...fixtureContent.text_entries, { key: "ui.chain.up_to", text: "reaches up to {n}" }, { key: "ui.chain.base", text: "base reach" },
    ...LINKS.map((key) => ({ key, text: `[fixture] ${key}` }))],
};
const catalog = new Catalog(content);
const base = fightsStep("fight", 100).view;
const reach = { value: 3, sources: [{ source: null, form: "base" as const, amount_bp: 2, share_bp: null }, { source: "foraging", form: "add_bp" as const, amount_bp: 5000, share_bp: null }] };
const view: View = { ...base, chains: [{ card: "hunt", runner: "raiders", up_to: reach }] };
const text = (n: Element | null | undefined): string => n?.textContent ?? "";

{
  const { ctx } = testContext(undefined, catalog);
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  cards.update({ ...view, chains: [] }, null);
  expect("no chain served: nothing drawn", cards.root.querySelector<HTMLElement>(".chain")?.hidden, true);
  cards.update(view, null);
  const line = cards.root.querySelector<HTMLElement>(".chain");
  expect("the reach as served", text(line?.querySelector(".chain-up-to")), "reaches up to 3");
  expect("beside the tap, not inside it", cards.root.querySelector(".card-tap .chain"), null);
  const entries = line?.querySelector<HTMLElement>(".fight-entries");
  expect("sources closed until tapped", entries?.hidden, true);
  line?.querySelector<HTMLButtonElement>(".fight-strength")?.click();
  expect("a tap opens them, the base first", Array.from(entries?.querySelectorAll(".fight-entry") ?? [], text), ["base reach2", "Foraging+50%"]);
  cards.update({ ...view, chains: [{ card: "hunt", runner: "raiders", up_to: { ...reach, value: 4 } }] }, view);
  expect("a raised reach redraws from the view", text(line?.querySelector(".fight-strength")), "4");
}

{
  const line = (key: string, card: string | null): LogLine => ({ at: 700, seq: 0, key, card, opens_beat: false });
  const lines = [line("l_link_1", "hunt"), line("l_link_next", "hunt"), line("l_link_next", "hunt"), line("l_link_1", null), line("l_other", "hunt")];
  const want = ["chronicle", "chronicle", "chronicle", "band", "band"];
  expect("live: each link in the chronicle, other lines on the band", liveLines(catalog, lines), want);
  const capped: View = { ...view, cards: view.cards.map((c) => (c.card === "hunt" ? { ...c, cap: 5 } : c)) };
  expect("on a return too, though the working is capped", awayLines(catalog, lines, capped, null), want);
}
