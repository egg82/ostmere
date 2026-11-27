// "When 1 or more hurt, until under 1" can be built (owner: "it's '2 or more' which I then forget to check before
// tapping a project card, so I'm always 15% slower"). A store rule needs a band of an item so it never flips at one
// level on a flow; a store only events raise (StoreInfo.rises_in_steps: nothing that runs makes it) cannot flip that way,
// so a rule on it may let go where it came on. The quick add on hurt: ui/rules/hurtrule.test.ts.
import { install } from "../../fake-dom";
import { fixtureContent } from "../../../fixtures/content";
import { fightsStep, withHurtChip } from "../../../fixtures/fights";
import type { View } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { tryRule } from "../../../src/game/condition/storerule";
import { draftWhen, editDraft } from "../../../src/ui/condition/conditiondraft";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(withHurtChip(fixtureContent));
const one = { items: 1 };

expect("control: hurt rises only in steps, wood does not", [catalog.risesInSteps("hurt"), catalog.risesInSteps("wood")], [true, false]);
expect("reaches 1, until under 1, on hurt", tryRule({ store: "hurt", test: "reaches", n: one, m: one }, 3, true), { store: "hurt", test: "reaches", n: one, m: one });
expect("control: on a store a flow raises it is held at reaches 2", tryRule({ store: "wood", test: "reaches", n: one, m: one }, 40, false)?.n, { items: 2 });
expect("under 1, until 1, on hurt", tryRule({ store: "hurt", test: "below", n: one, m: one }, 3, true)?.m, one);

// The owner's rule as saved reads back with no band; the editor reopens it as it is, not moved to a band.
const hurt: View = fightsStep("fighthurt", 100).view;
const when = { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "hurt" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false };
const saved: View = { ...hurt, orders: [{ when, then: { kind: "tap_card", card: "poultice" }, unless: [], or_else: [], below_next: false }] };
const draft = editDraft(catalog, saved, 0);
expect("reopened at reaches 1, letting go where it came on", draft && [draft.rule.n, draft.rule.m], [one, one]);
expect("and saved again as it was", draft && draftWhen(draft.rule, draft.opened, catalog.content.scales.quantity_per_item, catalog.isLevel("hurt")), when);
