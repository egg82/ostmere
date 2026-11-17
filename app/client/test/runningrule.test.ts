// A rule "while {card} is running" is a rule the Rules tab lists (orders.taskRules), on Camp, and its line words it;
// the When row lists the running cards as it lists Tasks: by section under each section's heading, each by name.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { townStep } from "../fixtures/town";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { sectioned } from "../src/game/cardsections";
import { conditionWords, taskRules } from "../src/game/orders";
import { subjectChoices } from "../src/game/ruleoffers";
import { ruleSideOf } from "../src/game/ruleside";
import { buildSubject } from "../src/game/subjectrule";
import { subjectRows } from "../src/ui/condsubject";

install();
const catalog = new Catalog(fixtureContent);
const base = townStep("town").view;
const failures: string[] = [];
const person = base.cards.find((c) => catalog.ruled(c.card))?.card;
const other = base.cards.find((c) => person !== undefined && catalog.laneOf(c.card) !== catalog.laneOf(person))?.card;
if (person === undefined || other === undefined) throw new Error("the town fixture has no person's card and another lane's: the check looked at nothing");

const when = buildSubject(catalog, { kind: "running", card: other, n: 1 });
const view: View = { ...base, orders: [...base.orders, { when, then: { kind: "tap_card", card: person }, unless: [], or_else: [], below_next: false }], orders_on: [...base.orders_on, false], order_states: [...base.order_states, "on"] };
const at = view.orders.length - 1;
if (!taskRules(view).includes(at)) failures.push("a running rule is not listed");
if (ruleSideOf(catalog, view, at) !== "camp") failures.push("a running rule on a person's task is not on Camp");
if (!(conditionWords(catalog, view, when) ?? "").includes(catalog.cardLabel(other))) failures.push(`its line reads ${conditionWords(catalog, view, when)}`);

const running = subjectChoices(catalog, view, [{ kind: "tap_card", card: person }]).running;
const want = sectioned(catalog, running, (r) => (r.kind === "running" ? r.card : null), view).flatMap((g) => [...(g.heading === "" ? [] : [`# ${g.heading}`]), ...g.items.map((r) => (r.kind === "running" ? catalog.cardLabel(r.card) : ""))]);
if (!want.some((w) => w.startsWith("# "))) failures.push("the running offers fall under no heading: the order check looked at one section");
const rows = subjectRows(catalog, view, { levels: [], tasks: [], running }, () => undefined);   // the Running head, then its rows
const got = rows.slice(1).map((r) => (r.classList.contains("cond-subhead") ? `# ${r.textContent}` : r.textContent));
if (JSON.stringify(got) !== JSON.stringify(want)) failures.push(`running rows ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
if (failures.length > 0) throw new Error(failures.join("; "));
