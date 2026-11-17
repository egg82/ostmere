// A rule on a store a lost fight adds to (Catalog.isLevel; hurt) is in the whole items its chip shows, rounded up
// (#218): "reaches 2" is on whenever the chip reads 2 or more, which is raw above one item, where a ledger store's
// amount is shown rounded down. The crossings sit on the amount the page shows (CONTRACT.txt, "a store rule").
import { fixtureContent, Q } from "../fixtures/content";
import { buildRule, readRule, ruleWhen, valid, type StoreRule } from "../src/game/storerule";
import { conditionWords } from "../src/game/orders";
import { Catalog } from "../src/game/catalog";
import { withHurtChip } from "../fixtures/fights";
import { fixtureStep } from "../fixtures/steps";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(withHurtChip(fixtureContent));
const rule = (test: StoreRule["test"], n: number, m: number): StoreRule => ({ store: "hurt", test, n: { items: n }, m: { items: m } });
const chip = (raw: number): number => Math.ceil(raw / Q);   // View.levels' reading

const reaches = buildRule(rule("reaches", 2, 1), Q, true);
expect("reaches 2, until under 1 builds above one item and above none", reaches.kind === "at_least" ? [reaches.value, reaches.release] : null, [Q + 1, 1]);
const on = (raw: number): boolean => reaches.kind === "at_least" && raw >= reaches.value;
for (const raw of [0, 1, Q / 2, Q, Q + 1, Q * 1.5, 2 * Q, 2 * Q + 1]) expect(`reaches 2 at ${raw}: on exactly when the chip reads 2 or more`, on(raw), chip(raw) >= 2);
expect("it is on at 1.5 hurt and off at 1", [on(Q * 1.5), on(Q)], [true, false]);

const below = buildRule(rule("below", 2, 3), Q, true);
const under = (raw: number): boolean => below.kind === "at_most" && raw <= below.value;
const letGo = (raw: number): boolean => below.kind === "at_most" && raw > below.release;
for (const raw of [0, 1, Q, Q + 1, 2 * Q, 2 * Q + 1, 3 * Q]) expect(`under 2 at ${raw}`, [under(raw), letGo(raw)], [chip(raw) < 2, chip(raw) >= 3]);

for (const r of [rule("reaches", 2, 1), rule("below", 2, 3), rule("reaches", 3, 2)]) expect(`${r.test} ${JSON.stringify(r.n)} reads back`, readRule(buildRule(r, Q, true), Q, () => true), r);

expect("the band rule is the one a ledger store has", [valid(rule("reaches", 2, 1), 3), valid(rule("reaches", 1, 1), 3)], [true, false]);
expect("worded in items", ruleWhen(catalog, rule("reaches", 2, 1)), "2 or more hurt, until under 1");
expect("a saved rule on hurt is read and worded in the same items", conditionWords(catalog, fixtureStep("full", 100).view, buildRule(rule("reaches", 2, 1), Q, true)), "2 or more hurt, until under 1");
