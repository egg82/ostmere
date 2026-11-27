// Share levels in a store rule (contract/endpoints.txt, "Share levels"; game/storerule.ts): each condition the editor writes
// (fixtures/share_cases.json, which tests/test_share_levels_wire.py sends through the engine) built from its rule and
// read back to it; the words for each form on the rule's line, the strip and the why line; and the levels a store of
// a given cap allows, read as the engine reads a share (the store's whole items against the exact share).
import { readFileSync } from "node:fs";
import { fixtureContent, Q } from "../fixtures/content";
import type { Condition } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { buildRule, levelWords, needsKey, readRule, ruleUntil, ruleWhen, switchForm, valid, type StoreRule } from "../src/game/storerule";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
type Case = { name: string; rule: Omit<StoreRule, "store">; when: Condition };
const shareCases = JSON.parse(readFileSync("fixtures/share_cases.json", "utf8")) as { cap_items: number; cases: Case[] };
const cases = shareCases.cases;
expect("the fixture's cap is the one its numbers assume", shareCases.cap_items, 12);
expect("every case was read", cases.length, 5);
for (const c of cases) {
  const rule: StoreRule = { store: "s", ...c.rule };
  expect(`${c.name}: built`, buildRule(rule, Q), c.when);
  expect(`${c.name}: read back`, readRule(c.when, Q), rule);
  expect(`${c.name}: a rule the page builds on its cap`, valid(rule, shareCases.cap_items), true);
}

const wood = (n: StoreRule["n"], m: StoreRule["m"], test: StoreRule["test"] = "below"): StoreRule => ({ store: "wood", test, n, m });
expect("the five named shares", [0, 2500, 5000, 7500, 10000].map((share) => levelWords(catalog, { share })), ["empty", "a quarter", "half", "three quarters", "full"]);
expect("any other share as a percentage", [levelWords(catalog, { share: 3500 }), levelWords(catalog, { share: 1250 })], ["35%", "12.5%"]);
expect("down to, until", ruleWhen(catalog, wood({ share: 2500 }, { share: 10000 })), "Dead wood down to a quarter, until full");
expect("under an amount, until a share", ruleWhen(catalog, wood({ items: 12 }, { share: 10000 })), "Under 12 Dead wood, until full");
expect("up to, until down to", ruleWhen(catalog, wood({ share: 10000 }, { share: 0 }, "reaches")), "Dead wood up to full, until down to empty");
expect("up to, until under an amount", ruleWhen(catalog, wood({ share: 8000 }, { items: 3 }, "reaches")), "Dead wood up to 80%, until under 3");
expect("an amount or more, until down to a share", ruleWhen(catalog, wood({ items: 30 }, { share: 2500 }, "reaches")), "30 or more Dead wood, until down to a quarter");
expect("strip: filling to a share", ruleUntil(catalog, wood({ share: 2500 }, { share: 7500 })), "until Dead wood is up to three quarters");
expect("strip: emptying to a share", ruleUntil(catalog, wood({ share: 10000 }, { share: 0 }, "reaches")), "until Dead wood is down to empty");
expect("strip: an amount until stays as it was", ruleUntil(catalog, wood({ share: 2500 }, { items: 20 })), "until 20 Dead wood");
expect("why off: a share's own words", [needsKey(wood({ share: 2500 }, null)), needsKey(wood({ share: 10000 }, null, "reaches"))], ["ui.rule.needs_down_to", "ui.rule.needs_up_to"]);

// A share is reached at the share itself: a quarter of 10 holds "down to" at 2 and under, "up to" at 3 and over.
expect("down to a quarter of 10, until 3: no band (on at 2, off at 3)", valid(wood({ share: 2500 }, { items: 3 }), 10), false);
expect("down to a quarter of 10, until 4: one item of band", valid(wood({ share: 2500 }, { items: 4 }), 10), true);
expect("up to a quarter of 10, until under 2: one item of band (on at 3, off at 1)", valid(wood({ share: 2500 }, { items: 2 }, "reaches"), 10), true);
expect("up to a quarter of 10, until under 3: none", valid(wood({ share: 2500 }, { items: 3 }, "reaches"), 10), false);
expect("down to empty, until full", valid(wood({ share: 0 }, { share: 10000 }), 10), true);
expect("up to empty is always true", valid(wood({ share: 0 }, { share: 0 }, "reaches"), 10), false);
expect("a share over full is refused", valid(wood({ share: 2500 }, { share: 10001 }), 10), false);

// Switching a level's form keeps where it reads now; items become the nearest five-point share.
expect("under 10 of 40 is down to a quarter", switchForm({ items: 10 }, "below", "on", 40), { share: 2500 });
expect("down to a quarter of 40 is under 11 (on at 10 and under)", switchForm({ share: 2500 }, "below", "on", 40), { items: 11 });
expect("until three quarters of 40 is until 30", switchForm({ share: 7500 }, "below", "off", 40), { items: 30 });
expect("until down to half of 40 is until under 21", switchForm({ share: 5000 }, "reaches", "off", 40), { items: 21 });
expect("13 of 40 rounds to the nearest step", switchForm({ items: 13 }, "below", "off", 40), { share: 3500 });
