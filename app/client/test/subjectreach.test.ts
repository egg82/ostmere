// A subject rule offers only numbers still ahead (docs/decisions/principles.md, "Every option offered works as worded"):
// a level is the one the engine's skill_level counts, across prestige phases (contract/prestige-phases.txt, "PRESTIGE PHASES"); a
// slider starts past where the count or level stands, save for the number a rule being changed already holds; the
// Camp is not offered once no level a rule can name is left; and a person's copy of a task reads apart from the hands'.
import { fixtureContent, Q } from "../fixtures/content";
import { prestigeStep } from "../fixtures/prestige";
import { fixtureStep } from "../fixtures/steps";
import { townStep } from "../fixtures/town";
import { install } from "./fake-dom";
import type { Content } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { subjectChoices } from "../src/game/condition/ruleoffers";
import { buildSubject, defaultSubject, subjectNow, subjectRange, subjectWords, type SubjectRule } from "../src/game/condition/subjectrule";
import { RulesTab } from "../src/ui/rules/rules";
import { testContext } from "./context";

install();
const failures: string[] = [];
const expect = (label: string, got: unknown, want: unknown): void => {
  if (JSON.stringify(got) !== JSON.stringify(want)) failures.push(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
};

// After a prestige the bar's level restarts at 1 while the engine counts on: firecraft at level 7 of phase 2 is 17.
{
  const catalog = new Catalog(fixtureContent);
  const view = prestigeStep("prestigeclicked", 100).view;
  const bar = view.skills.find((s) => s.skill === "firecraft");
  if (!bar?.prestige || bar.prestige.level_counted === bar.level) throw new Error("the fixture's firecraft is not past a prestige: the check looks at nothing");
  const rule: SubjectRule = { kind: "level", skill: "firecraft", n: 1 };
  expect("firecraft's level is the counted one", subjectNow(catalog, view, rule), bar.prestige.level_counted);
  expect("a new rule on it starts one past the counted level", defaultSubject(catalog, view, rule).n, bar.prestige.level_counted + 1);
  expect("and cannot slide below it", subjectRange(catalog, view, rule)[0], bar.prestige.level_counted + 1);
}

// Every slider starts one past where its subject stands; a rule being changed keeps its own number reachable.
{
  const catalog = new Catalog(fixtureContent);
  const view = fixtureStep("full", 100).view;   // foraging at level 2, shelter done once of 3
  expect("a level starts past the level now", subjectRange(catalog, view, { kind: "level", skill: "foraging", n: 3 })[0], 3);
  expect("a count starts past the count now", subjectRange(catalog, view, { kind: "count", card: "shelter", n: 2 }), [2, 3]);
  expect("a kept number below that stays reachable", subjectRange(catalog, view, { kind: "level", skill: "foraging", n: 3 }, 1)[0], 1);
  const { ctx } = testContext(undefined, catalog);
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  const then = { kind: "switch_mix" as const, mix_id: view.mixes[0]!.id };
  tab.update({ ...view, orders: [{ when: buildSubject(catalog, { kind: "level", skill: "foraging", n: 1 }), then, unless: [], or_else: [], below_next: false }], orders_on: [true], order_states: ["on"] });
  tab.root.querySelector<HTMLElement>(".rule-cond")!.click();
  const slider = (): Element | null | undefined => Array.from(tab.root.querySelectorAll<HTMLElement>(".cond-subject-control .cond-level")).find((s) => !s.hidden)?.querySelector('[role="slider"]');
  expect("an old rule at level 1, changed, keeps level 1 on its slider", [slider()?.getAttribute("aria-valuemin"), slider()?.getAttribute("aria-valuenow")], ["1", "1"]);
  tab.root.querySelector<HTMLElement>('.cond-subject[data-subject="task:shelter"]')!.click();
  expect("another subject picked starts past its count", slider()?.getAttribute("aria-valuemin"), "2");
}

// The Camp at its last nameable level (the next one held, not yet lifted) is not offered; one below it is.
{
  const levels = fixtureContent.camp!.camp_levels;
  const camp = (at: number[]): Content => ({ ...fixtureContent, camp: { ...fixtureContent.camp!, camp_levels: at.map((a, i) => ({ ...levels[i === at.length - 1 ? 1 : 0]!, at: a * Q, held: i === at.length - 1 })) } });
  const view = fixtureStep("full", 100).view;   // the camp holds 80 items
  const offers = (content: Content): boolean => subjectChoices(new Catalog(content), view).levels.some((r) => r.kind === "camp");
  expect("a level still to reach: the Camp is offered", offers(camp([50, 200, 400])), true);
  expect("no level left to name: the Camp is not offered", offers(camp([50, 400])), false);
}

// A person's copy of a hands task shares its label; the rule's words name the person's lane for the copy.
{
  const gather = fixtureContent.card_infos.find((c) => c.card === "gather")!;
  const catalog = new Catalog({ ...fixtureContent, card_infos: [...fixtureContent.card_infos, { ...gather, card: "helper_gather", lane: "helper" }] });
  const view = townStep("town").view;
  const hands = subjectWords(catalog, view, { kind: "running", card: "gather", n: 1 });
  const copy = subjectWords(catalog, view, { kind: "running", card: "helper_gather", n: 1 });
  if (hands === copy) failures.push(`the hands' and the helper's gather both read "${hands}"`);
  if (!copy.includes(catalog.laneLabel("helper", view))) failures.push(`the helper's copy does not name its lane: "${copy}"`);
  const count = subjectWords(catalog, view, { kind: "count", card: "helper_gather", n: 2 });
  if (!count.includes(catalog.laneLabel("helper", view))) failures.push(`a count on the copy does not name its lane: "${count}"`);
}

if (failures.length > 0) throw new Error(failures.join("; "));
