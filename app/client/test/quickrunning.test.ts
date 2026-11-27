// The simple view's When row offers the few running cards a rule is about (ruleoffers.quickRunning, game/relevant.ts), read
// off the cards' kept lane or side, then what feeds the rule's inputs; More options keeps every running card. A rule
// changed to another action drops a running subject that action no longer offers.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { kindsView, withKinds } from "../fixtures/kinds";
import { townStep } from "../fixtures/town";
import type { CardInfo, Content, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { QUICK_RUNNING, quickRunning, subjectChoices } from "../src/game/condition/ruleoffers";
import { defaultRule } from "../src/game/condition/storerule";
import { subjectKey } from "../src/game/condition/subjectrule";
import { draftWhenRow } from "../src/ui/condition/condwhen";
import { dropStaleRunning, type Draft } from "../src/ui/condition/conditiondraft";

install();
const failures: string[] = [];
const base = withKinds(fixtureContent);
const kept = (lane: string | null, side: string | null) => [{ lane, side, amount_bp: 1000, slot: 0 }];
const fight = { side: "gap", threat: "t", loses: [], wounds: [], won_line_keys: [], lost_line_keys: [], loss_pool: null, loss_notes: null, on_loss_key: null } as CardInfo["fight"];
const edit = (changes: Record<string, Partial<CardInfo>>): Catalog => new Catalog({ ...base, card_infos: base.card_infos.map((i) => (i.card in changes ? { ...i, ...changes[i.card] } : i)) } as Content);
const view: View = kindsView(townStep("town").view);
const tap = (card: string) => [{ kind: "tap_card" as const, card }];
const cards = (c: Catalog, doing: string, actions = tap(doing)) => quickRunning(c, view, actions, [doing]).map((r) => (r.kind === "running" ? r.card : r.kind));
const same = (name: string, got: unknown, want: unknown) => { if (JSON.stringify(got) !== JSON.stringify(want)) failures.push(`${name}: ${JSON.stringify(got)}, want ${JSON.stringify(want)}`); };

// A stew kind whose effect reaches a lane offers that lane's cards, and not another's.
const lanes = edit({ pot_a: { kept: kept("helper", null) }, pot_b: { kept: kept("mason", null) } });
same("stew on the helper's lane", cards(lanes, "pot_a"), ["chop", "haul"]);
same("stew on the mason's lane", cards(lanes, "pot_b"), ["hew", "carve"]);
// An effect on a side reaches the cards that fight on it.
const side = edit({ pot_b: { kept: kept(null, "gap") }, hew: { fight } });
same("stew on a side", cards(side, "pot_b"), ["hew"]);
// A person's card: the cards that make what it takes come first, then the ones that take what it makes.
const feed = edit({ chop: { takes: ["wood"], makes: ["roots"] } });
same("feeders then users", cards(feed, "chop"), ["gather", "smoke_roots", "pot_a", "pot_b"]);
// No more than QUICK_RUNNING, the rest left to More options.
const wide = edit({ pot_b: { kept: kept("hands", null) } });
same("capped", cards(wide, "pot_b").length, QUICK_RUNNING);
if (subjectChoices(wide, view, tap("pot_b")).running.length <= QUICK_RUNNING) failures.push("the cap cut nothing: the check looked at too few cards");
// Nothing for the hands' own rule (Running is not offered there), and nothing reached means nothing offered.
same("hands task", cards(lanes, "gather"), []);
same("no relation", cards(edit({ pot_b: { kept: [] } }), "pot_b"), []);

// The When row of a new rule on the pot: the relevant running cards in the simple view, every running card in More options.
const draft = (card: string): Draft => ({ index: null, then: { kind: "tap_card", card }, rule: defaultRule("", "below", 0), unless: [], orElse: [], scope: "camp", lane: "pot" });
const keys = (c: Catalog, full: boolean) => draftWhenRow(c, view, full, draft("pot_b"), { chip: () => undefined, store: () => undefined, subject: () => undefined })
  .filter((e) => e.dataset.subject !== undefined).map((e) => e.dataset.subject);
same("row, simple", keys(lanes, false), ["running:hew", "running:carve"]);
const everything = subjectChoices(lanes, view, tap("pot_b")).running.map(subjectKey);
if (everything.length <= 2 || !everything.every((k) => keys(lanes, true).includes(k))) failures.push(`More options lost running cards: ${keys(lanes, true)}`);
// Changing the action to one on the subject's own lane drops it; to another lane's, keeps it.
const stale: Draft = { ...draft("pot_b"), subject: { kind: "running", card: "hew", n: 1 } };
const own = { ...stale, then: { kind: "tap_card" as const, card: "carve" } };
dropStaleRunning(lanes, view, own);
if (own.subject !== undefined) failures.push("a running subject on the action's own lane stayed");
const other = { ...stale, then: { kind: "tap_card" as const, card: "chop" } };
dropStaleRunning(lanes, view, other);
if (other.subject === undefined) failures.push("a running subject on another lane was dropped");
if (failures.length > 0) throw new Error(failures.join("; "));
