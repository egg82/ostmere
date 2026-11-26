// The scene's conditions against the fixture's mid-game view: wood 14 items falling 120 an hour, stone 3 items
// steady, the bench lane running "shelter", the cold chip showing.
import { Q, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { SceneFacts } from "../src/scene/conditions";

const AT = 1_000;
const facts = new SceneFacts();
facts.observe(fixtureStep("mid", AT).view);

function expect(condition: string, t: number, want: boolean): void {
  const got = facts.holds(condition, t, Q);
  if (got !== want) throw new Error(`holds("${condition}", t=${t}) = ${got}, want ${want}`);
}

expect("store:wood", AT, true);
expect("store:wood@14", AT, true);
expect("store:wood@15", AT, false);
expect("store:stone@3", AT, true);
expect("store:stone@4", AT, false);
expect("store:nothing@1", AT, false);
expect("store:wood@14", AT + 60, false);   // sampled at t: a minute on, two items have gone
expect("store:wood@12", AT + 60, true);
expect("store:wood@10..15", AT, true);        // a window: at least 10 and fewer than 15
expect("store:wood@14..15", AT, true);
expect("store:wood@10..14", AT, false);       // 14 is not fewer than 14
expect("store:wood@10..14", AT + 60, true);
expect("store:wood@15..20", AT, false);
expect("store:nothing@0..9", AT, false);

expect("store:stone@4|running:shelter", AT, true);
expect("running:shelter|store:stone@4", AT, true);
expect("store:stone@4|chip:warm", AT, false);
expect("chip:warm|chip:cold", AT, true);

// A store the page never lists is read off view.levels, falling at its own rate; a ledger line wins when there is one.
{
  const base = fixtureStep("mid", AT).view;
  const clock = { store: "hidden_clock", segment: { start: AT, start_value: 10 * Q, rate: -Q, limit: 0 } };
  const f = new SceneFacts();
  f.observe({ ...base, levels: [clock] });
  const want = (condition: string, t: number, ok: boolean): void => {
    const got = f.holds(condition, t, Q);
    if (got !== ok) throw new Error(`levels: holds("${condition}", t=${t}) = ${got}, want ${ok}`);
  };
  want("store:hidden_clock", AT, true);
  want("store:hidden_clock@10", AT, true);
  want("store:hidden_clock@10", AT + 1, false);
  want("store:hidden_clock@9", AT + 1, true);
  want("store:hidden_clock", AT + 10, false);
  want("store:wood@14", AT, true);
}

// A card running on the hands lane: `running:<id>` holds for that card and for no other, so the figure's pose follows it.
{
  const hands = new SceneFacts();
  hands.observe(fixtureStep("standing", AT).view);
  const check = (condition: string, want: boolean): void => {
    const got = hands.holds(condition, AT, Q);
    if (got !== want) throw new Error(`hands running stand: holds("${condition}") = ${got}, want ${want}`);
  };
  check("running:stand", true);
  check("running:gather_hand", false);
  check("running:gather_hand|running:stand", true);
}

// A mix share: true while the active mix runs the card (by: mix) with a share above 0; paused or yielded, nobody runs it.
{
  const base = fixtureStep("mid", AT).view;
  const template = base.cards.find((c) => c.card === "gather")!;
  const bar = (card: string, share_bp: number, run: "full" | "paused" | "yielded") =>
    ({ ...template, card, share_bp, run, by: run === "full" && share_bp > 0 ? ("mix" as const) : null });
  const holds = (cards: ReturnType<typeof bar>[], condition: string): boolean => {
    const f = new SceneFacts();
    f.observe({ ...base, cards });
    return f.holds(condition, AT, Q);
  };
  const want = (got: boolean, ok: boolean, what: string): void => { if (got !== ok) throw new Error(`${what}: ${got}, want ${ok}`); };
  want(holds([bar("woodcutting", 3000, "full")], "mix:woodcutting"), true, "running share");
  want(holds([bar("woodcutting", 3000, "full")], "mix:scavenging_share"), false, "another action");
  want(holds([bar("woodcutting", 0, "full")], "mix:woodcutting"), false, "no share");
  want(holds([bar("woodcutting", 3000, "paused")], "mix:woodcutting"), false, "paused");
  want(holds([bar("woodcutting", 3000, "yielded")], "mix:woodcutting"), false, "yielded");
  want(holds([bar("scavenging_share", 2000, "full")], "running:x|mix:scavenging_share"), true, "any-of with a mix");
  // Two cards in the mix take turns at the figure, each for its share of a round (30 s): 60% is the first 18 s.
  const two = [bar("woodcutting", 6000, "full"), bar("scavenging_share", 4000, "full")];
  const turn = (t: number, card: string): boolean => {
    const f = new SceneFacts();
    f.observe({ ...base, cards: two });
    return f.holds(`mix:${card}`, t, Q);
  };
  for (const [t, card, other] of [[0, "woodcutting", "scavenging_share"], [17, "woodcutting", "scavenging_share"],
    [18, "scavenging_share", "woodcutting"], [29, "scavenging_share", "woodcutting"], [30, "woodcutting", "scavenging_share"]] as const) {
    want(turn(t, card), true, `turn at ${t}`);
    want(turn(t, other), false, `not the turn at ${t}`);
  }
}

// A card's skill-level need, through the fixture's own text table.
{
  const { Format } = await import("../src/game/format");
  const { Text } = await import("../src/game/text");
  const { fixtureContent } = await import("../fixtures/content");
  const text = new Text(fixtureContent);
  const got = new Format(text, fixtureContent.scales).needSkill("Foraging", 2, 3);
  if (got !== "Foraging level 2/3") throw new Error(`needSkill = "${got}"`);
}

// `end:showing` reads view.ended_at, the end the server recorded, and nothing live: all covered with no end recorded is
// not it, and a line gone red (all_covered false) after the end keeps it, so the dusk survives a reload.
{
  const covered = fixtureStep("covered", AT).view;
  if (covered.ended_at === null) throw new Error("the fixture's covered view should carry the end");
  const showing = (view: typeof covered): boolean => {
    const f = new SceneFacts();
    f.observe(view);
    return f.holds("end:showing", AT, Q);
  };
  const want = (got: boolean, ok: boolean, what: string): void => { if (got !== ok) throw new Error(`${what}: ${got}, want ${ok}`); };
  want(showing(covered), true, "the end recorded");
  want(showing({ ...covered, ended_at: null }), false, "all covered, no end recorded");
  want(showing({ ...covered, all_covered: false }), true, "the end recorded, a line red again (a fresh page, as after a reload)");
}

// `project:` and `pushes:` read a card's completions, from the card panel or the Completed tab.
expect("project:stand", AT, true);      // completed: 3 in the Completed tab
expect("pushes:stand@3", AT, true);
expect("pushes:stand@4", AT, false);
expect("project:shelter", AT, true);    // in play, completed once
expect("pushes:shelter@2", AT, false);
expect("project:stool", AT, false);     // in play, never completed

// `&` needs every part to hold, and binds tighter than `|`: the figure sits on the stool when doing a job AND the stool
// is built. In the mid view `feature:mix` is unlocked, `running:shelter` and `chip:cold` hold, `feature:stool` does not.
expect("running:shelter&feature:mix", AT, true);
expect("running:shelter&feature:stool", AT, false);
expect("feature:stool&running:shelter", AT, false);
expect("running:shelter&chip:cold&feature:mix", AT, true);
expect("running:shelter&chip:cold&feature:stool", AT, false);
expect("running:shelter&feature:stool|chip:cold", AT, true);     // (a and b) or c
expect("feature:stool&running:shelter|chip:warm", AT, false);
expect("feature:stool|running:shelter&feature:mix", AT, true);   // a or (b and c), not (a or b) and c
expect("store:wood@15&running:shelter", AT, false);

// `answered:`, `answer:`, `joined:` and `left:` read the unlocked entry of that category and id, and no other category's:
// an answer is not its offer, and a lane's join is not its leaving.
{
  const base = fixtureStep("mid", AT).view;
  const entries = [
    { category: "answered" as const, id: "o_x" },
    { category: "answer" as const, id: "o_x_no" },
    { category: "joined" as const, id: "n8" },
    { category: "left" as const, id: "n9" },
  ];
  const f = new SceneFacts();
  f.observe({ ...base, unlocked: [...base.unlocked, ...entries] });
  const want = (condition: string, ok: boolean): void => {
    const got = f.holds(condition, AT, Q);
    if (got !== ok) throw new Error(`unlock kinds: holds("${condition}") = ${got}, want ${ok}`);
  };
  want("answered:o_x", true);
  want("answered:o_x_no", false);
  want("answer:o_x_no", true);
  want("answer:o_x", false);
  want("answer:o_x_yes", false);
  want("joined:n8", true);
  want("left:n8", false);
  want("left:n9", true);
  want("joined:n9", false);
  want("answered:o_x&joined:n8", true);
  want("answered:o_x&left:n8", false);
  const none = new SceneFacts();
  none.observe(base);
  if (none.holds("answered:o_x", AT, Q)) throw new Error("answered holds with no such entry");
}
