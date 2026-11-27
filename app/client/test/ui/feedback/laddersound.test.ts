// The ladder's sound (docs/design/sound.md, "The ladder", "Never sounded", "Landing a sound on its picture"): each rung
// names its sound as a field, a batch of arrivals plays only its highest cue, a tap's chain ticks on the audio clock,
// and under the Null locator nothing plays and the pictures are the same. A recording stands in for the player.
import { expect, fire, rig, stepWith, ALL } from "../book/journalrig";
import { testContext } from "../../context";
import { fixtureStep } from "../../../fixtures/steps";
import type { Card, View } from "../../../src/api/types";
import { KNOCK_CYCLE_SEMITONES, KNOCK_GAP_MS, resetCues, sing, TICK_RATIOS } from "../../../src/audio/cues";
import { hasSound, registerSound, resetSound } from "../../../src/audio/locator";
import { LINK_GAP_MS } from "../../../src/game/story/arrivals";
import { NewMarks } from "../../../src/game/lessons/marks";
import { Cards } from "../../../src/ui/cards/cards";
import { Flight } from "../../../src/ui/asks/flight";
import { LADDER, play } from "../../../src/ui/feedback/ladder";
import { Reveal } from "../../../src/ui/feedback/reveal";
import { StripGlow } from "../../../src/ui/story/stripglow";

let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });
Object.assign(window, { innerWidth: 400, innerHeight: 800, matchMedia: () => ({ matches: false, addEventListener: () => undefined }) });

interface Played { slot: string; pitch: number; delay: number }
let played: Played[] = [];
let cuts = 0;
function record(): void {
  played = [];
  cuts = 0;
  resetCues();
  registerSound({ play: (slot, pitch = 1, delay = 0) => { played.push({ slot, pitch, delay }); return () => { cuts += 1; }; }, loop: () => ({ setLevel: () => undefined }), piece: () => ({ setLevel: () => undefined, stop: () => undefined, onEnd: () => undefined }) });
}
const slots = (): string[] => played.map((p) => p.slot);

const node = (): HTMLElement => {
  const n = document.createElement("div");
  Object.assign(n, { rect: { left: 10, top: 100, width: 200, height: 50, right: 210, bottom: 150 } });
  return n;
};
const LEVEL = (r: Reveal, n: HTMLElement, link?: "level") => r.effect(n, "skill", (quiet) => { if (!quiet) sing("level"); }, link, "level");

// Each rung names its sound as a field.
expect("the rungs' sounds", [LADDER.background.sound, LADDER.tap.sound, LADDER.first.sound, LADDER.level.sound], [null, "knock", "new", "level"]);

{  // the ladder on a card: a tap knocks, a mix's and a rule's completions are silent, a failed tap is its own sound
  const AT = 100;
  const ID = "take_stock";
  const base = fixtureStep("restrule", AT).view;
  const card = (completions: number, by: Card["by"]): Card => ({
    card: ID, completions, cap: null, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 20, by,
    completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, full_store: null, gained: [], crew: null, tap_s: 20, speed: 1, needs: [],
    });
  const viewOf = (c: Card): View => ({ ...base, cards: [...base.cards, c] });
  const complete = (by: Card["by"], rule: boolean, times: number): { cards: Cards; view: View } => {
    const { ctx } = testContext();
    const cards = new Cards(ctx, new NewMarks());
    document.body.replaceChildren(cards.root);
    if (rule) ctx.fires.running.add(ID);
    let prev = viewOf(card(0, by));
    cards.update(prev, null);
    cards.update(prev, prev);
    record();
    for (let k = 1; k <= times; k += 1) {
      clock += 1000;
      const next = viewOf(card(k, by));
      cards.update(next, prev);
      prev = next;
    }
    return { cards, view: prev };
  };
  complete("mix", false, 3);
  expect("a routine mix completion makes no sound", played, []);
  complete("tap", true, 3);
  expect("a rule's completion makes no sound", played, []);
  const tap = complete("tap", false, 3);
  expect("a tap's completion knocks, once each", slots(), ["tap", "tap", "tap"]);
  expect("a repeat never grows: the third plays the first's gain and delay", [played[2]!.delay, played[0]!.delay], [0, 0]);
  played = [];
  tap.cards.failed(ID, tap.view);
  expect("a failed tap sounds its own", slots(), ["failed"]);
}

{  // taps within 0.1 s play one; the pitch steps through the five offsets; none grows
  record();
  for (const t of [0, 40, KNOCK_GAP_MS - 1]) sing("knock", 0, t);
  expect("taps within 0.1 s play one", slots(), ["tap"]);
  sing("knock", 0, KNOCK_GAP_MS);
  expect("a tap 0.1 s on plays", slots(), ["tap", "tap"]);
  record();
  for (let i = 0; i < 200; i += 1) sing("knock", 0, i * 500);
  const semis = played.map((p) => 12 * Math.log2(p.pitch));
  expect("two hundred repeats: each within a third of a semitone, the cycle of five", [played.length, semis.every((s) => Math.abs(s) <= 1 / 3), KNOCK_CYCLE_SEMITONES.length],
    [200, true, 5]);
  expect("the hundredth sounds as the first (the cycle comes round)", [played[100]!.pitch, played[100]!.delay], [played[0]!.pitch, 0]);
}

/** A batch: `members` say what arrives, drawn into one collected batch, then shown. */
function batch(members: Array<"new" | "level" | "beat" | "end">): string[] {
  record();
  const r = new Reveal();
  r.collect();
  members.forEach((m, i) => {
    if (m === "new") r.arrive(node(), "card", `n${i}`);
    else if (m === "level") LEVEL(r, node());
    else r.line([node()], `l${i}`, 0, m);
  });
  r.start(0);
  r.tick(10_000);
  document.body.dispatchEvent(new Event("click"));
  return slots();
}

{  // one cue per batch, picked in the order opening's end, story beat, level, new
  expect("new alone", batch(["new"]), ["first"]);
  expect("several new: one", batch(["new", "new", "new"]), ["first"]);
  const L3 = ["level", "level", "level"];
  expect("a level over new", batch(["new", "level", "new"]), L3);
  expect("a level plays its three rising notes", [played.map((p) => p.pitch), played.map((p) => p.delay)], [[1, 5 / 4, 3 / 2], [0, 110, 220]]);
  expect("a beat over a level and new", batch(["new", "level", "beat"]), ["story"]);
  expect("the end over all", batch(["beat", "new", "level", "end", "new"]), ["strike"]);
  expect("two beats: one", batch(["beat", "beat"]), ["story"]);
  record();
  const r = new Reveal();
  r.collect();
  r.line([node()], "side", 0);
  r.start(0);
  r.tick(10_000);
  expect("a line that opens no beat is silent", played, []);
  record();
  const out = new Reveal();
  out.collect();
  const below = node();
  Object.assign(below, { rect: { left: 10, top: 5000, width: 200, height: 50, right: 210, bottom: 5050 } });
  out.arrive(below, "card", "far");
  out.start(0);
  out.tick(10_000);
  expect("what is out of sight makes no sound", played, []);
}

{  // a tap's chain: the first link is the tap's knock; link n ticks at the start + n x 90 ms, rising; a level takes its link's tick
  const chain = (tapped: boolean, levelAt: number | null): Reveal => {
    record();
    const r = new Reveal();
    r.cascade();
    const links = ["finish", "store", "store", "level", "rule", "rule", "rule"] as const;
    links.forEach((link, i) => {
      if (i === levelAt) LEVEL(r, node(), "level");
      else r.effect(node(), "card", (quiet) => { if (i === 0) play(document.createElement("div"), tapped ? "tap" : "background", quiet); }, link, i === 0 && tapped ? "tap" : undefined);
    });
    r.start(1000);
    return r;
  };
  clock = 1000;
  const first = chain(true, null);
  const ticks = played.filter((p) => p.slot === "tick");
  expect("five ticks at 90 ms steps from the start", ticks.map((p) => p.delay), [1, 2, 3, 4, 5].map((n) => n * LINK_GAP_MS));
  expect("rising through the pentatonic", ticks.map((p) => p.pitch), [...TICK_RATIOS]);
  expect("the first link is the tap's own knock, at once", played.filter((p) => p.slot === "tap").map((p) => p.delay), [0]);
  first.tick(clock + 9999);
  chain(false, null).tick(clock + 9999);
  expect("a chain the mix started stays silent", played, []);
  chain(true, 3).tick(3000);
  expect("a level in the chain takes its link's tick", [played.filter((p) => p.slot === "tick").map((p) => p.delay), slots().includes("level")],
    [[1, 2, 4, 5].map((n) => n * LINK_GAP_MS), true]);
  const set = chain(true, null);
  cuts = 0;
  played = [];
  clock = 1000 + LINK_GAP_MS + 10;
  fire(document.body, "click");
  expect("a tap that sets off the links stops the ticks not yet begun and plays one", [cuts, slots()], [4, ["tick"]]);
  void set;
}

{  // a served line's own flag says it opens a beat: only that line carries the story cue
  record();
  const strip = node();
  const [plain, opens] = [node(), node()];
  strip.append(plain, opens);
  document.body.replaceChildren(strip);
  const r = new Reveal();
  r.collect();
  new StripGlow(strip).lead(r, [plain, opens], false, (() => { let i = 0; return () => String(++i); })(), [false, true]);
  r.start(0);
  r.tick(10_000);
  expect("the line that opens a beat sounds the story cue, once", slots(), ["story"]);
  record();
  const r2 = new Reveal();
  r2.collect();
  new StripGlow(strip).lead(r2, [plain, opens], false, () => "x", [false, false]);
  r2.start(0);
  r2.tick(10_000);
  expect("lines that open none are silent", slots(), []);
}

{  // a live step's arrivals show at once and are one batch too
  record();
  const r = new Reveal();
  r.cascade();
  r.arrive(node(), "card", "a");
  r.arrive(node(), "skill", "b");
  r.start(0);
  expect("two arrivals in one step: one First note", slots(), ["first"]);
  record();
  const r2 = new Reveal();
  r2.cascade();
  r2.arrive(node(), "card", "a");
  LEVEL(r2, node(), "level");
  r2.effect(node(), "card", () => undefined, "finish");
  r2.start(0);
  r2.tick(1000);
  expect("a level link outranks an arrival", slots(), ["level", "level", "level"]);
}

{  // flight: the rule's landing on the Rules tab settles in place of the First note
  record();
  new Flight({ effect: (_n, _k, run) => run(false), arrive: () => undefined, line: () => undefined, busy: false }).land(node());
  expect("a rule's landing settles", slots(), ["settle"]);
}

{  // a page turned
  const r = rig({ notes: ALL, read: [] });
  r.open();
  record();
  r.next().click();
  expect("a page turned", slots(), ["page"]);
  void stepWith;
}

{  // under the Null locator nothing plays and the pictures are the same
  const run = (): string => {
    const r = new Reveal();
    const nodes = [node(), node(), node()];
    r.cascade();
    const rungs = ["tap", "first", "level"] as const;
    nodes.forEach((n, i) => r.effect(n, "card", (quiet) => play(n, rungs[i]!, quiet), (["finish", "store", "level"] as const)[i], rungs[i]));
    r.arrive(node(), "card", "x");
    r.start(0);
    r.tick(1000);
    return nodes.map((n) => n.className).join("|") + document.querySelectorAll(".pop").length;
  };
  record();
  const loud = run();
  resetSound();
  played = [];
  expect("the Null default is not a sound", hasSound(), false);
  expect("the pulses are drawn at all", loud.includes("landed") && loud.includes("burst"), true);
  expect("the pictures do not change", run(), loud);
  expect("nothing plays", played, []);
}
console.log("laddersound: ok");
