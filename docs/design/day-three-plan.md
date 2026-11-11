# Day three: what engineering builds

Day three runs from B4 (day two's last beat) to B5, through chapter beats K1–K5, steps A20 and A22–A24, and a side
layer of minor beats (SL1–SL6). It also adds one sink to day two, and sets the shape of the chapters from B5 to B7. Its
design is in `content/` (`team/day-three.md` and `team/day-three-numbers.md`, never shown to the owner); this file holds only
what the code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a week or
more.

## What changed the pace

From B5 on, every spine beat lands at `beats.yaml`'s target day on the typical route, sharp no sooner than 0.83×,
scaled by one number, `pace_scale` in `beats.yaml` (1.0). A normal pace reaches B4 a day or more early, so the gap to
B5 is filled with content (the chapter's own beats plus the side layer), held by a per-visit density target, never by
slowing day one or day two. Each return must offer something to spend and something to decide (after day two).

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A trip held against a full store, with finds | Cards and Triggers, per `banked-time-plan.md` | The banked-time slice's shape; nothing new |
| A comfort built a stage at a time | Cards (a capped craft, one stage per completion), the queue's When ready | A build is already how the camp gets better |
| A build whose stages must cure between | Lanes (a side lane like the drying rack, its task installed by the build's first stage), Cards (each later stage requires the cure's count) | The rack already runs work that takes no hands; a cure is that, and the mix runs on meanwhile |
| A second townsperson | People (an arrival), Offers (the second offer kind), Cards (the make-room build on either lane) | Day two's offer and one-off idiom, with D-87's equal answers |
| The town's mix: people as shares | Mixes (one mechanism for both layers; `docs/systems.md`'s planned town layer) | Decided at the second arrival (day-two Open 3): two people is the first real split |
| A small two-answer offer whose answers install modifiers | Offers (answers' outcomes), Modifiers | An answer outcome is a trigger outcome; a modifier is one |
| The arrivals count as a gate | Gates, Stores (a tally store) | `beats.yaml` already gates B7 on arrivals; the count needs a home the engine solves for |
| A side layer of minor beats | Triggers and Offers for the content; the simulator and flat check for the counting | Minor beats are content on existing systems; only the tools learn a new list |
| A landing band from target days | Simulator only | A check, read from `beats.yaml` |

Nothing new on the wire beyond the town's mix (item 3).

## Work, by system

Item 0 ships first and alone. Items 1–6 must land before day three's content (item 7) is sized; banked-time items 1–4
must too, and banked-time item 6 (the page's trips) before day three ships, because day three opens a trip at B4.
Nothing in day three depends on combat items 1–7.

0. **Day two's sink** (**S**, content). One staged comfort in `day_two.toml`, new ids only (the release lock's
   additive rules), opened by an existing trigger's outcome so no absence gains an unlock. Accept: the loader and the
   lock pass; the day-two report shows B4 within 0.5 h of today's figure on every route and the per-visit and
   per-absence verdicts unchanged; the day-two policies build it after the chapter's two builds.
1. **The absolute landing band** (**S**, tests). A verdict `abs_band` on the routes that reads `pace_scale` and each
   spine beat's target day from `beats.yaml` (the one place) and checks, for every beat from B5 on that a route
   reaches: typical in [(d − 1) × S, d × S] days from the save's start, sharp no sooner than 0.83 × (d − 0.5) × S.
   Lazy is reported, not checked. Accept: planted fixture histories landing a beat early and late each go red; the
   verdict asserts it read `pace_scale` and at least one target day; a fixture with `pace_scale` changed moves the
   band (a control that the number is read, not copied).
2. **The side layer in the tools** (**S**, tests and `content/team/flatcheck.py`). Read `beats.yaml`'s `side_layer:`
   list: validate its fields (kind, chapter, thread, `offers`), refuse a turn field on a side entry, refuse any spine or
   chapter gate that names a side id, and count side beats in the simulator's new things per visit and per week by
   kind. Accept: each refusal has a planted failing entry; the per-week report shows spine, chapter and side counts.
3. **The town's mix** (**L** in all, engine, api, client). At the second arrival, the townsfolk's lanes become one mix
   whose shares are people's time, over each person's cards; the first person's rules keep acting, and a save past
   the join is rebased with them. The interface is written: engine `DESIGN.txt`, "THE TOWN'S MIX" (invariants 90–97),
   and `api/CONTRACT.txt`, "The town's mix". In short: a town mix is an ordinary saved mix whose cards sit on joined
   ruled lanes, a share being part of one person's time; the running one is set by the town's always rule (a
   SwitchMix order, no Save field); a rule's tap on a joined lane yields that person's shares, as a tap yields the
   hands' mix; joining is an outcome part (`joins`) that adds a `joined` unlock and turns the lane's always task into
   its share. If the content lead keeps the first person's lane until the third arrival (`day-three.md`, Open 4), the
   K5 outcome carries one join instead of two; nothing below changes. Fits into: Mixes, Lanes, Standing orders,
   Triggers, Unlocks. In order (3a and 3b in parallel worktrees; 3c and 3d after 3a; 3e after 3d; 3f after 3a):
   - **3a. Engine** (**M**). Layer, town share and its SaveMix refusals, the running town mix and per-layer Order
     mix, yield on joined lanes, dry-pause order, the engine's XP refusal on ruled-lane cards, Join and JOINED, the
     view fields, the loader's `joins`. Accept: the existing engine-contract and day-one/day-two playthrough suites
     pass unchanged (no hands route moves; a moved held counter is reported, never raised); the save-fields ledger is
     unchanged; function and file gates hold without a raise.
   - **3b. Blind contract tests** (**M**), by an agent that never reads 3a's code: invariants 90–97 from `DESIGN.txt`
     and the contract alone, on fixture rules with two ruled lanes and a cure-shaped ruled lane that never joins,
     with a `MUTANTS.txt` of planted wrong engines (shares summed across people; a tap that does not yield; town
     orders read into the hands' running mix; a join that drops a non-always rule; a capped card accepted). Accept:
     each mutant goes red; ambiguities logged to a gaps file and answered in `DESIGN.txt` before 3a merges.
   - **3c. Rebase and release lock** (**S**). JOINED renamed by lane and checked in step 4; the three new lock
     refusals; a rebase fixture past the join that keeps the first person's non-always rules in order and turns its
     always task into that person's share (invariant 97); a read-only prod query that no live save holds a mix id beginning
     `town:`. Accept: each lock refusal has a planted failing release; the fixture fails against a rebase without
     step 6's join.
   - **3d. API** (**S**). `running_town_mix_id`, `town_mix_order`, the `joined` category, the 422s, the text keys;
     `openapi.json` regenerated. Accept: API tests for each 422 (nothing written) and for a view with a tap yielding
     one person's shares while the other's run.
   - **3e. Page and lesson** (**M**). The town strip under the hands strip, the editor's per-person split, the Rules
     tab's town section, the lesson on its own controls, the greyed state. Accept: renders at 390×844 and in dark
     mode, looked at, with two people (one tapping by a rule, one on shares) and with one; the lesson starts once and
     never again after skip; no ruled-lane card in the card panel.
   - **3f. Simulator** (**S**). The town's default policy (leave the join's split) and the 2 AM test on a fixture
     chapter with two joins. Accept: the 2 AM test is level with the town's mix running; a planted policy that
     re-splits by hand each visit does no better. Item 6 builds on it.
4. **Arrivals as a gate** (**S**, engine and loader). `arrivals: n` in `beats.yaml` maps to an at-least on a tally store;
   the first arrival's outcome sets it to 1, a save already past it gets 1 at rebase, and each later arrival's join adds
   1. Accept: a fixture gate on 2 fires at the second join and not before; a rebased fixture past the first arrival
   reads 1; the content check refuses a tally store any card takes.
5. **The second offer kind** (**S**, client and simulator). The Rules tab shows the answer order once a second kind of
   offer exists (day-two Open 4); offers whose answers install modifiers (a small choice between two habits) load and
   show each answer's effect in the UI register. Accept: a fixture with two offer kinds shows the order; a fixture
   answer's modifier appears in its target's explain() with the answer as source; the simulator answers both kinds by
   order.
6. **The simulator past B4** (**M**, tests). Day-three routes (day two's ten, continued); policies for the trip held at
   the visit it opens, comforts and courses queued When ready, the arrival offer and the small offer by order, the
   town's mix default; per-visit counters with two new ones, **spend** (a card affordable whose takes include a store at
   ≥ 80% of its cap) and **decide** (an answer, a choice of builds, or a mix or queue change that moves which of two
   goals lands first); per-absence counts; item 1's band; banked-time item 2's cap-loss check at day three's end; the
   2 AM test across the chapter; `--lines` state lists for the writers' brief. Needs banked-time items 1–4 and items
   1–2. Accept: each new counter has a planted fixture visit that fails it (a return with nothing affordable at a full
   store; a visit with no choice); the report prints bands, density and cap loss per route.
7. **The content file** (**M**, content). `day_three.toml`, merged after `day_two.toml` (new ids only): its trip, finds,
   comforts, the cure lane, the arrival and its offer, the small offer, clocks, order cards, side beats, aims, Camp
   levels and level finds, with `beats.yaml`'s `day_three:` and `side_layer:` lists. Needs items 1–6 and banked-time
   items 1–4. Accept: the loader and the lock pass; item 1's band holds for B5; item 6's density targets hold on
   typical; the cap-loss check passes at day three's end without a held entry; the 2 AM test is level; the flat check
   raises nothing beyond the two flags `day-three.md` names (week 1's net until the B5–B7 chapters, a thread that ends
   in a later chapter).
8. **Lines** (**M**, content). From the brief (`content/team/day-three-lines-brief.md`) once item 6's `--lines` exists:
   proposers, critic, lead, voice pass. Accept: every key filled; the code checks (length, must-not scan, echoes) pass.
9. **Art** (**M**, after item 7's ids settle). The scene states and figures `day-three.md`, "Art" lists, picked from the
   packs first (`sprite-catalog`); stages 25–31 in `tools/scene`. Accept: composites at 390×844 and 3840×2160, looked at.

## The chapters after, and where they plug in

- **B5 → B6 and B6 → B7's eve** (**M** content each, later passes): each about one real day on typical, the same
  shapes (chapter beats, a side layer, sinks), item 1's band for B6 and B7. The second needs item 4 for the third
  arrival. Arcana's first card is a trip-shaped sink (banked-time BT6); nothing new.
- **B7** is combat-plan item 8 (`b7.toml`), after combat items 1–7. Two of day three's builds become entries on the
  camp's side against week 1's pests there, so combat's content adds side entries sourced by existing builds, no new
  mechanism. B7's gate gains a step at night beside the arrivals (`beats.yaml`).
- **Later weeks** reuse the side layer as is: 4–5 spine beats a week and about as many side beats, held by item 2's
  per-week counts and item 6's density.
