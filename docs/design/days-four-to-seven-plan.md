# Days four to seven: what engineering builds

The rest of week 1, after day three: four chapter files from B5 to the end of story day 7. Its design is in `content/`
(`team/days-four-to-seven.md`, `-numbers.md` and `-lines-brief.md`, never shown to the owner); this file holds only what the
code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a week or more.

## The chapters

| File | Spans | Lands | Carries |
|---|---|---|---|
| `day_four.toml` | B5 → B6 | B6 at A21 in night 5 | chapter beats L1-L3, a staged build, a chip on a side lane, side beats SL7-SL8 |
| `day_five.toml` | B6 → B7's eve | night 6 | Arcana's cards and level pays, the third arrival (two people, one offer), M1-M2, SL9-SL11 |
| `b7.toml` | B7 | A29 in night 6 | combat-plan item 8: B7's moment, a one-off story fight (A27), the combat feature, the week's fights, gear, the lost-fight state and its cure, the ramp's clock |
| `day_six.toml` | B7 → night 7 | night 7, held to the calendar | G1-G2, a staged build taking a fight's drop, a small offer, SL12-SL14, Camp 12 |

Each is merged after the one before it (new ids only, the release lock's additive rules). Landing bands are D-93's:
B6 typical 96-120 h, sharp ≥ 90; B7 typical 120-144 h, sharp ≥ 110. Week 2 opens on B8, the season's turn on the
calendar's day 8, so story day 7 ends by save time, not by B7.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A story day whose length is a clock with a floor in save time | Gates (`after_time`, which the loader already turns into `AfterTime`), Triggers | Day two's and day three's evening clocks plus one existing condition; no engine change |
| A chip on a side lane that an existing build prevents | Chips (a latched all-condition reading two unlocks and a card count) | Day one's chip shape; the cure is an existing card, so "a cure in reach" holds by construction |
| Arcana's first cards: a card converting one store into another, a staged build trained by the skill, level pays aimed at other lanes | Cards, Skills and the pacing curve, Modifiers | An ordinary skill. The Spells row (rules combined by an interpreter) is not needed until Spellcraft opens at B15; nothing in week 1 combines anything |
| An arrival of two people from one offer | Offers (an offer of the arrival kind, so the kind's answer rule answers it: item 10), Cards (the bay on either lane), Triggers (one outcome with two `joins`), Stores (arrivals +2) | Day three's arrival idiom; the town's mix already takes a list of joins (day-three item 3) |
| A share that makes nothing yet (a townsperson's second card) | Cards on a ruled lane | A card with no makes; it gains them in week 2 |
| A one-off story fight that opens combat | Cards (a one-off with lines, no FightDef), Triggers | C2's answer: a beat never rolls |
| Odds shown as unknown until the first fight | Fights view (read only), the page | `decisions.md`, "Blind until learned"; the engine already serves the fought count |
| A small two-answer offer that takes one unit of a store | Offers (an answer outcome that takes a store) | If the answer outcome cannot take a store, it is a one-off card the answer starts (the queued one-off idiom); item 5 decides |
| A day's end held to the calendar | Gates (`after_time` again) | The same condition as the day-length floors |

**New engine work for Arcana: none.** Nothing in week 1 needs the Spells row. **New engine work for the third
arrival: offer kinds** (item 10).

## Work, by item

Items 1-6 must land before the chapters ship; item 7 can follow; 8 and 9 follow the content. Day three ships first
(its items 0-9), and nothing here changes a released day-three id. Items 10-14 come from the chapter files' first
pass (below, "Gaps the chapter files found"): 13 before day three ships, 14 before item 2, 10-12 before item 3.

1. **The simulator past B5** (**M**, tests). Day-three item 6's routes continued through day four and day five to B7's
   eve: policies for the staged builds queued When ready, the Arcana card held against its supply store at the visit
   it opens and the trip's hold moved to another of its supplies (item 13), the arrival offer by the kind's answer
   rule where the route set one after day three's offer (item 12), the town's mix default after a join of two (keep the join's split), the
   chip's cure built when it shows; the per-visit counters (spend, decide), per-absence counts, item 1's band for B6
   and B7, banked-time item 2's cap-loss check at each chapter's end, the 2 AM test across both chapters, and `--lines`
   state lists. Needs day-three items 1, 2, 3f and 6. Accept: B6 and B7 inside their bands on typical and above the
   floor on sharp; a planted fixture day with the save-time floor removed lands sharp's B6 under its floor (the floor is
   read, not copied); a planted visit with nothing affordable at a full store fails the spend counter.
2. **`day_four.toml`** (**M**, content). Its clocks with save-time floors, the staged build, the chip, the chapter
   beats, the side layer, Camp 11, the aims, the end card; `beats.yaml`'s twin (item 6). Needs item 1 and day-three
   item 7. Accept: the loader and the lock pass; the chip check (cost words with effects, its cure a card at every
   sampled moment) passes; item 1's band holds for B6; density targets hold on typical; the cap-loss check passes at
   the chapter's end or names the store that fails, with the content's lever (the trip's bar, then the Arcana card's
   input) applied before any sink is added.
3. **`day_five.toml`** (**M**, content). Arcana's cards and pays, the arrival offer and its two builds, the join of two,
   the two new townsfolk's cards, the side layer, the aims, the end card. Needs item 2 and day-three items 3, 4 and 5
   (the town's mix, arrivals as a gate, the second offer kind's answer order) and items 10-12. Accept: as item 2,
   plus: a fixture save that set the arrival kind's answer rule after answering day three's offer has this chapter's
   offer answered by it at the instant it shows; the arrivals tally
   reads 4 after the join and B7's arrivals gate is met.
4. **`b7.toml`** (**M**, content; this is combat-plan item 8, settled by `team/days-four-to-seven.md`, "B7"). B7's
   outcome (a standing drain with a clock store on one side lane's stores only, the one-off story fight, the aim);
   the combat feature at the one-off's completion; one hunt card, one gear card, two standing fights against the
   camp's stores whose sides take entries from two day-three builds, a lost-fight bad state with a self-heal standing
   action and a cure card, Melee and its pays, a ramp clock store with no step in week 1. Needs combat items 1-7,
   item 3 and item 6 here. Accept: combat item 8's acceptance (the loader and combat item 6's checks pass; combat item
   9's report shows B7 inside its band), and no week-1 trigger aims at a threat strength.
5. **`day_six.toml`** (**M**, content). Its clock held to the calendar, the staged build taking a fight's drop, the
   small offer, G1-G2, the side layer, Camp 12 lifted by G2, the end card at the edge of week 1's content. If an
   answer outcome cannot take a store, the offer's take is a one-off its answer starts (no engine change). Needs item
   4 and combat item 9. Accept: the loader and the lock pass; night 7 falls before the season's turn on every route;
   density targets hold on typical and on sharp's longer day; the cap-loss check at week 1's end.
6. **Odds unknown until the first fight** (**S**, client). A fight runner whose fought count is 0 shows its odds as
   unknown, never a number (`decisions.md`, "Blind until learned, perfect once known"); from the first fight on, the
   served odds. Reads `FightView.fought`; nothing on the wire changes. Fits into: the Fights view and the page; the
   Knowledge row's first use, as a page reading, not a model. Must ship with or before combat item 7. Accept: a client
   test that a view with fought 0 renders no odds figure anywhere on the card, the strength sheet or the ledger, and
   one with fought 1 renders the served odds; a render at phone width and in dark mode, looked at.
7. **`beats.yaml` and the flat check** (**S**, content and `content/team/flatcheck.py`). The chapters' twin lists
   (`day_four:`, `day_five:`, `day_six:`, as `day_three:`), side entries SL7-SL14, and the two spine entries that gain a
   `pays` (B6, B7). The flat check reads every chapter list, not only `day_one:` (day-three item 2 adds the side layer;
   this adds the later chapter lists). Accept: the flat check on the authored order raises nothing for week 1 (no
   `week_net_up`, no run flags); a planted chapter entry with a third turn in a row is flagged.
8. **Lines** (**M**, content, one batch per chapter). From the brief once item 1's and combat item 9's `--lines` exist:
   proposers, critic, lead, voice pass. Accept: every key filled; the code checks (length, must-not scan, echoes) pass.
9. **Art** (**M**, after items 2-5's ids settle). The scene states, world layers and figures the content's "Art" lists,
   picked from the packs first (`sprite-catalog`); stages 32-40 in `tools/scene`. Overlaps combat item 11 (its
   figures and changed world states) and banked-time item 8 (the comforts' scene states): one agent takes all three
   lists. Accept: composites at 390×844 and 3840×2160, looked at.

## Gaps the chapter files found

The first pass at `day_four.toml` and `day_five.toml` hit four places where this plan assumed something the code does
not do. Two share a cause: the simulator's policies set an answer order and a hold through the engine, and no page
builds either (the client sends `holds: []` in every mix and builds no answer rule; `api/CONTRACT.txt`, "OFFERS",
forbids one). So the bands, the cap-loss check and the 2 AM test measured a player who cannot exist. Items 10-13 give
the player both, and the policies then use only what the page offers.

- **G1, answering a later offer by rule.** Intended: the answer rule set at day three's arrival offer answers day
  five's arrival offer, so the town grows while the player is away (`DESIGN.txt`, "BANKED TIME", "Arrival";
  `docs/systems.md`, Offers, "by kind once there is a second kind of offer"). `AnswerOffer` names one offer, so it
  cannot. Options: content (an answer installing the next offer's answer: the first answer would silently decide the
  second, and installs are tap rules only); per-offer rules on the page (the player cannot name an offer not yet
  shown); offer kinds in the engine (the shape `DESIGN.txt` already deferred to this moment). Decided: offer kinds,
  items 10-12. Without them an arrival shown while away waits for a visit, which is something lost *because* the
  player was away (`decisions.md`, "The town").
- **G2, two holds on one store.** Intended: the Arcana card and the trip both drink the store past a level, the
  shares setting which gets more. The engine allows one hold per store per mix (`mixes.Hold`). Options: several holds
  per store (two consumers at one level have no defined split: the passes resolve them in declaration order, not by
  share, and the joint solve is deferred in `DESIGN.txt`, "Hold"); content. Decided: content. The
  Arcana card takes the hold on the shared store when it joins the mix and the trip's hold moves to another of its
  supplies (`team/days-four-to-seven.md`, "Arcana"); the shares still cap each card's draw. One hold per store stays,
  as `decisions.md`'s one target control per resource line has it. The page's hold is item 13.
- **G3, level finds on levels that already pay a find.** Decided: content, no code. A find goes only on a level whose
  row pays speed alone, restating that row (day three's idiom for its finds), never on one that already has a find;
  the levels are in `team/days-four-to-seven.md`, "Levels and finds".
- **G5, a chip whose cure works through a count store.** Intended: the cure is an existing build, so a cure is in
  reach by construction. The chip has to read a count store (it must turn off at a story moment as well as at the
  build, and a chip reads one condition), which the build adds to through a trigger on its completion count. The cure
  reading (`app/ashfall_app/engine/cure_reading.py`) sees only what a card's own outcome puts up, and the cures gate
  gives a cure 600 s, less than one stage. Options: content (put the count in the build's own outcome: day three's
  build would then name a day-four store, and the 600 s still fails); mark the chip `no_cure` (false: it has a cure);
  teach the reading the trigger. Decided: the reading, item 14. It reads more, and checks no less.

10. **Offer kinds** (**M**, engine and loader; interface first, in `DESIGN.txt`, "Offers", where the rejected entry
    "AnswerOffer by offer kind" gains a dated note that this supersedes it). `OfferDef` gains an optional kind and
    each answer of a kinded offer a role; every offer of one kind has the same roles. A new order verb, the kind's
    answer (kind, role): it can act while an offer of that kind is open, and applies `AnswerOffer` to the first open
    one in rules order with its answer of that role; evaluation runs on as after any answer, so two open offers of
    the kind are answered at one instant. Never dead (a kind may always offer again); refused from the player (the
    player answers an offer) and in `SetQueue` (a queue head that never pops). Codec: the manifest's offers carry kind
    and roles, with a format upgrade that adds none. Release lock: giving a kind to an offer that had none is Safe;
    changing a released offer's kind or answer's role is Forbidden. The loader's `[[offers]]` gain `kind`, answers
    `role`; day three's arrival offer and day five's carry the arrival kind. Fits into: Offers (Type Object: the kind
    is data on the offer), Standing orders (one more order verb, as `AnswerOffer` was). Accept: the engine-contract
    and playthrough suites pass unchanged; the save-fields ledger is unchanged; a fixture with two offers of a kind
    and the kind's rule set while the first is open answers both, the second at the instant it shows; the result
    equals the same save given `AnswerOffer` with that answer at each instant (invariant 62's shape); a planted kind
    whose second offer lacks a role fails the loader.
11. **Blind contract tests for offer kinds** (**S**, tests), by an agent that never reads item 10's code: from
    `DESIGN.txt` and the contract alone, with a `MUTANTS.txt` of planted wrong engines (the rule goes dead after its
    first offer; it answers with the first offer's answer id; it matches roles by position; it acts on an offer not
    yet shown; a player may send it). Accept: each mutant goes red; ambiguities logged and answered in `DESIGN.txt`
    before item 10 merges.
12. **The answer rule on the page** (**M**, api, client and simulator). The wire's order verb and
    `Content.offer_infos` gain kind and role; `CONTRACT.txt`, "OFFERS", lets the page build one answer rule per kind,
    in the Rules tab's answers section, once an offer of that kind has been answered, offering the kind's roles by
    that answer's labels, and edit or remove it (the page still builds no `answer_offer` rule). The simulator's
    policies set the kind's rule only after answering the kind's first offer, in place of today's per-offer orders
    set ahead. Fits into: the Rules tab's answers section (day-three item 5), Standing orders. Accept: API tests for a
    422 on a role not of the kind (nothing written); a client test that the builder is absent before any offer of the
    kind is answered and present after, with a planted page offering it earlier going red; a render at 390×844 and
    in dark mode, looked at; the day-three and day-five 2 AM tests rerun under the restricted policies, a red at a
    kind's first offer reported to content, never cured by restoring an order set ahead.
13. **A hold on the page** (**M**, client, contract and simulator; day three's trip needs it too, so it lands before
    day three ships). `decisions.md`, "The mix": a resource line carries a control to hold it steady by an action the
    player picks. On a ledger line whose store a card of the player's own running mix costs, a Hold control picks
    that card and a level (the line's cap by default) and saves the mix with the hold; one hold per store, so a line
    already held offers a change of card or level, not a second hold. The simulator's sink policies
    (`app/tests/dayone/sinks.py`) set only holds this control offers at that view. Fits into: the ledger line and the
    mix editor (`save_mix` already carries holds), the engine's Hold unchanged. Accept: a client test that the
    control's `save_mix` carries the hold for a card that costs the store and offers none for a card that does not;
    a planted policy holding a store with no ledger line fails the policy's own check; a render at 390×844 and in dark
    mode, looked at; day three's cap-loss check rerun with the restricted policies.
14. **The cure reading through a completion count** (**S**, `app/ashfall_app/engine/cure_reading.py` and
    `app/tests/dayone/cures.py`). `puts_up` also returns the stores added by a trigger whose `when` is an at-least on
    the card's own completion count (the fight checks share the reading and get it too). For a cure card with a cap,
    the gate passes when the fork has started the card's next stage within `CURE_S` and the chip is off by the landing
    of the completion that trigger counts; a card without a cap keeps today's `CURE_S`. Accept: on fixture rules, a
    chip on a count store that a build's count trigger adds to is cured; planted controls go red: the trigger adds
    another store, its count is past the card's cap, the build cannot start within `CURE_S`; day one's cures gate and
    the fight checks' tests pass unchanged.

## Where this meets the other plans

- **Day three** (`day-three-plan.md`): items 1 (bands), 2 (side layer in the tools), 3 (the town's mix, which must take
  a join of two in one outcome), 4 (arrivals), 5 (the second offer kind), 6 (the simulator) and 7 (its content) all
  come first.
- **Combat** (`combat-plan.md`): items 1-7 before item 4 here; item 8 *is* item 4 here; item 9 (the simulator past B7)
  covers day six's routes and needs item 5's content to run on; item 10 (the day-one and 2 AM tests past B7) runs on
  `b7.toml` and `day_six.toml` together; item 11 is folded into item 9 here.
- **Banked time** (`banked-time-plan.md`): item 6 (the page's trips) shipped with day three; item 7 (the day-one tests
  past the sinks) must cover this chapter's staged builds and the Arcana card before item 2 ships; item 8 (art) folds
  into item 9 here; item 9 (a trip that fights) is not needed in week 1: no week-1 trip fights.

## After week 1, where it plugs in

- **B8** is a season beat (`clock: true`, `season: drift`): the season clock is week 2's to build; nothing here reads a
  season.
- **B9** gates on journal entries; the journal is week 2's to build. Nothing in week 1 writes a journal entry.
- The week-1 shares that make nothing yet gain their makes in week 2 as entries on a camp side against week 2's
  roster, no new mechanism.
