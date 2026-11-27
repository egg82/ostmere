// The Mixes list holds the player's own mixes and never the town's (contract/the-towns-mix.txt, "The town's mix"): a town mix can't be
// run by the player, and it is changed in the town's own editor, never the mix editor. The view is the engine's own
// (fixtures/townwire.ts) over the day-two page, whose hands mixes stay listed.
import { fakeDocument, type FakeEl, install } from "../../fake-dom";
import { testContext } from "../../context";
import { fixtureContent } from "../../../fixtures/content";
import { townStep } from "../../../fixtures/town";
import type { PartContext } from "../../../src/ui/part";
import { MixSelector } from "../../../src/ui/mixes/selector";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const view = townStep("town").view;
const hands = view.mixes.filter((m) => !fixtureContent.game_mix_ids.includes(m.id)).map((m) => m.id);
const s = new MixSelector(testContext().ctx as PartContext);
s.show(view);
document.body.replaceChildren(s.root);
const root = fakeDocument.body.firstElementChild as FakeEl;
const rows = root.querySelectorAll(".selector-name").map((n) => n.textContent);
expect("the hands' mixes are listed", hands.length > 0 && hands.every((id) => rows.includes(id)), true);
expect("and nothing else: no town mix", rows.length, hands.length);
