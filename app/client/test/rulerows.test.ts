// A rule's entries in the chronicle (game/rulerows.ts): from Step.rule_runs, each run's last start and last let-go at
// their game seconds, the rule in the player's words, the store's level then as the cause (none for a chip's rule), and
// an id that stays the same while later Steps repeat the run.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { ruleWords } from "../src/game/orders";
import { ruleEntries } from "../src/game/rulerows";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const step = fixtureStep("rulestab", 200_000);
const [tired, wood] = step.rule_runs;
if (!tired || !wood) throw new Error("rulestab's runs: the tired rule and the wood rule");
const words = (i: number): string => { const w = ruleWords(catalog, step.rule_runs[i]!.order)!; return `${w.when} → ${w.action}`; };

const got = ruleEntries(catalog, step.rule_runs);
const of = (rule: string): Array<[string, number, string | null]> =>
  got.filter((e) => e.entry.text.startsWith(rule)).map((e) => [e.entry.text, e.entry.at, e.entry.cause]);
expect("a rule that came on and has not let go: one entry, no cause for a chip's rule", of(words(0)),
  [[`${words(0)} came on`, tired.on_at, null]]);
expect("a store rule that came on and let go: two entries, each with the store's level then", of(words(1)),
  [[`${words(1)} came on`, wood.on_at, `2 ${catalog.storeLabel("wood")}`], [`${words(1)} let go`, wood.off_at, `20 ${catalog.storeLabel("wood")}`]]);
expect("every entry is a rule's", [...new Set(got.map((e) => e.entry.kind))], ["rule"]);
expect("the ids are the same from one Step to the next", ruleEntries(catalog, step.rule_runs).map((e) => e.id), got.map((e) => e.id));
expect("and differ from each other", new Set(got.map((e) => e.id)).size, got.length);
expect("no runs, no entries", ruleEntries(catalog, []), []);
