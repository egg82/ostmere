# Open work

The queue, top first. Delete an item when it ships; design rules live in `docs/decisions/`, indexed by `decisions.md`.

The host, the CI runners and the cluster are shared with whatever other sessions are working:
before a suite, a test container, a pipeline or an API burst, check who else is busy and coordinate only on real
contention (method and limits in the `fanout-craft` skill, `references/shared-resources.md`). Research that lands under `docs/research/` is sent to the habits session too,
the parts that apply to it.

**Focus now:** new content stops at day fifteen, which stays in `IN_WRITING`. Prestige and its
follow-ups shipped; choice, not protection (item 15) is next.

**Before resubmitting to galaxy.click.** They declined until the game is complete or nearly so; what their reviewer
hit and what the feedback asks is in `docs/research/galaxy-review.md`. Its work, first two first:
- **Teach the mix system where it is first needed** (a seasoned reviewer still didn't use it).
  One system at a time, mixes before rules, since a rule switches the hands to a mix. In progress: the first
  mix is built by the player, guided, where the first-mix offer shows; then the first rule is built by the player, guided on the real editor, where the first rule offer shows; later a quiet dot marks what the player keeps doing (a card tapped by hand often, the same manual
  switch made again), counted from the decision log; and the
  walkthrough as a reusable mechanism (lessons as data), all shipped. No further mix lessons: the mix
  lesson introduces mixes and the mix tutorials end there; no offer builds a mix or a rule for the player. Judged by a cold tester who doesn't play
  idle games, never the owner.
- **Sounds re-picked by a human ear.**
- **Game design 101's proposals** (`docs/research/design-101.md`, §3, ranked): running the rounds of the tester protocol
  (`docs/tester-protocol.md`, which also holds the gapped cold session), what the rules did lately (the Rules tab's
  reason line and its `Lately` block, both built; Fits into: Chronicle and unwrap), judged in the tester protocol's
  rounds by asking a returning tester why this mix is running, and, done, the motion and sound rule (`decisions.md`) and the phone audit
  (`research/a11y-audit.md`, its clear failures fixed). The general findings became the cross-project `game-design` skill.
  Left from the audit: short viewports and the mix editor's keyboard (unverified on a real device), the remaining
  hover-revealed affordances, and the lesson note's overlap with the mix editor.
- Research behind these, each ending on a proposal to test: `teach-automation.md` (a new card says once it can join
  the mix), `waits-and-ends.md` (a wait states its length; the end of current content gets a plain out-of-fiction
  card), `human-readers.md` (where to find blind readers and an editor, and costs), `venues.md` (share early builds
  on a hidden itch.io page and Feedback Friday; galaxy.click rejects heavy generative-AI use). AI use is disclosed
  wherever a venue asks, not on the game's own site.

**Day twelve's whenever replays doubled after #15 and sit near the plays' 600 s timeout.** On CI the babysitter
pair's setup went from 150-290 s to 347-511 s (#20 now runs its two replays side by side), and
`tests/weektwo/test_ladder_readouts.py::test_a_route_ladder_readout_is_reported[whenever]` from about 210 s to
300-420 s. Find what the replays now recompute (#15 moved B3 earlier for some routes) and carry state forward;
never raise the timeout.

**An order-dependent test.** `tests/db/test_failover.py::test_the_site_is_logged_at_startup` fails when run alone: it
leans on an earlier test's logging setup (same on main before the overhaul). Give it its own logging setup.

**A card tap that never lands at phone width, in the headless harness.** At 390x844 a Playwright click on a card
button sent no decision; `elementFromPoint` at the button's centre returned the `.card-list` wrapper. Same on main
before the redesign. Find whether the wrapper covers the buttons on a real phone or the probe misses; fix it if real.

0. **The opening's follow-ups.** Every card is mixable: shipped (one kind of card, tapped or mixed; a one-off is a
   card with a cap that moves to Completed). The screen is `docs/design/opening-screen.md`, the story and timeline
   `content/team/opening-v2.md` (never shown to the owner).
   - **A pull forward** (the story didn't show enough to make anyone want to see where it goes). The first
     fifteen minutes should raise at least one question the player wants answered. The preview may (2026-10-13) reveal a little more if that is what it takes; the specifics stay below the line.
   - **How the story reaches the eyes:** a tap's line in the strip only (redesign step 1) and one thing at a time, line first, shipped
     (`docs/design/opening-screen.md`, "Cards" and "One thing at a time"; research in `docs/research/story-to-the-eyes.md`).
     Fits into: Cards (a second view of the line the Step carries; the story strip stays the record) and Chronicle and unwrap
     (the arrival queue's second use, live). The "was it seen" probe is `app/tools/seen/` (README in run.sh's header).
     Left: the research's rec 3 (on a desktop, the newest line at the top of the card column) as its own test, with
     the probe's distance condition and the card line off; a lazy route (taps spaced out, mostly the mix) through the
     probe; one tester session per change, asked afterwards to pick seen lines from real and invented ones (never
     the owner).
   - **Away-time unlocks revealed one at a time:** shipped (`docs/design/opening-screen.md`, "Coming back"). Fits into:
     Chronicle and unwrap (`systems.md`), as its first piece: the arrival queue is the Event Queue its announcements
     were planned as, and the cursor is the kept state re-read at its own time. Left: the view carries no unlock
     times, so arrivals are ordered by kind; when the chronicle's events carry times, pass them to the queue. Not
     yet seen in a real browser: a tab hidden and shown again (headless never hides a tab; the same path was driven
     by its event).
   - **The screen arrives when it means something:** shipped (`decisions.md`; the page's rules in
     `app/client/src/game/shown.ts`). Fits into: Unlocks (`systems.md`): the engine still says what exists, the page
     when its part first means something; the chip's `offered_after` is the order cards' field and reader. Left: a
     later first hunger (a Safe rate retune, measured with its costs in the slow-reveal findings), held until the
     reveal has been played live; and the cold chip shows for the few seconds between the fire's arrival and the
     chip clearing, beside the ledger's arrival, held back by the reveal queue behind the fire's lines (watch for it
     in that play).
   - **Stated aims:** shipped (`decisions.md`, "Every stretch of play has a stated aim"). Fits into: Unlocks
     (`systems.md`) and the content file, read by the page the way a chip's `offered_after` is: each aim is a content
     entry keyed to the unlock that starts it, and the next one's start ends it. Not the Camp bar's next marker, which
     says what a level pays, and not the day-one goals (`tests/dayone/goals.py`), which are skill levels a setup reaches
     sooner, not what a stretch is for.
   - **Tuning pass.** "Tuned" is defined in `docs/decisions.md`, "Tuned means checked". Done: rates show the fewest
     digits that tell them apart (no sign on zero, none read as zero); a store's name is capitalised leading a ledger
     line, a totals row, a card's need or a condition-editor store button. Left: a rate of 1.33/min keeps two decimals
     (the contract's cut). An audit of every label and figure call site (2026-10-25) found no other store leading a row
     in lowercase and no shown figure bypassing the formatter beyond the contract's "as they are" slots; one call is
     open: in the mix editor, a card's contributions ("damp wood +2/min · …") follow the card's name, so they are not
     capitalised (`ui/editorrows.ts`).
   - The lying figure at the start still leans gold, and testers found the face odd: look when the scene is next touched.
   - **The condition editor's known limit** (`covered` ignores a rule's condition): `design/opening-screen.md`, "The
     condition editor".
1. **Pacing simulator past the opening**, before any content is tuned. It drives the real engine (`docs/systems.md`,
   "The engine"); the opening already has the 2 AM test and its readouts (`app/tests/dayone/`). Left, for the whole
   game, as readouts: weeks to each beat, new things per week to the end, and time to max per skill. Math notes:
   `docs/research/pacing-math-notes.txt`. Output names beats by number only (`CLAUDE.md`).
   - **The ladder readout** is built (`python -m tests.ladder.readout`, from `app/`; `app/tests/ladder/`): per route, each
     skill's level times and phase top, each card's share of the mixes by day with the cards that went quiet, each skill's
     XP by source per band of days, and whether one saved mix shape always wins (the dominance readout; its definition is
     in `ladder/dominance.py`). It reports only, and its text is committed and compared like the other readouts (`design/sim-invariants.md`). Weeks
     to each beat and the back half wait for content past day fifteen.
   - **What a re-mix is worth**: the readout is built (`python -m tests.worth.readout`, from `app/`; `app/tests/worth/`,
     measure and routes in `design/worth-a-change.md`, "What the simulator measures"). Left: own rules against offers
     only, once goal stints exist.
   - **Experiment on the engine part after projects: who implements**. One reviewed interface, then three
     implementers given the interface plus the designer's written rationale (a "Rejected, and why" section the
     designer's brief asks for in DESIGN.txt) against three given the interface alone. Judge:
     the same blind contract suite (failures on first finish, planted mutants still caught), questions asked and
     interface misreadings, pyright and size gates, lines, tokens, and a smell rating by a reviewer blind to the arm.
     Three a side is directional: act on a clear gap across several measures, call a narrow one a tie.
   - **World and story, first pass** (`content/`): written. Its review waits for the next item.
2. **Code, on habits' modules**, when the town's content needs it (after day two and the build-toward work). Read
   habits' `docs/systems.md` first and extend rather than copy; follow `docs/engineering.md`. What lifts, per a
   read of habits' main: `game/map` (pathing, MapAuthority; the cleanest) and `game/talk` (Conversations behind a
   Null Object, line sources as frozen candidates; its Claude pool is DB-bound and only feeds candidates) first;
   `game/town` and `game/tales` (plain events in; not `llm/stories`, which is DB and queue bound); `game/planner`
   only after habits' P9d moves the ground/pathing API. Every entry point must call its `wiring.wire()` (unwired,
   the town is empty and silent, not broken), the content YAML and the baked `plan.json` come along, and determinism
   rests on the Python/TS RNG parity (`game/town/rand.py`, `rand.ts`). The kit loader is not needed: art is served by
   web here. Accounts take only the session parts of habits' (no Authentik, so not its OIDC or
   hearths); saves are the server's (`decisions.md`, "Saves never die with a device"). Transfer codes, their QR
   and recovery words are built, and so are several saves on the page (the Games sheet) and the merge: a device with
   games of its own is asked, then its games move into the other account, numbered after its games, refused past the
   cap (POST /api/join's `merge`, CONTRACT.txt).
3. **Runtime writing prompts** per `docs/research/llm-writing.md`: facts as attributes, shuffle-bag pools, seeded
   lenses, the implied-turn rule; arrival lines on Sonnet. Then a blind model test per new kind of line.
4. **Journal entries** from `docs/research/sketch-test/process.md`. The sheet, its loader and its notes as data are built
   (`CONTRACT.txt`, "JOURNAL"); what remains is each entry's notes and sketch. Look at every new entry before it
   ships; commission art where the method slips.
5. **Art still untested:** movement, a daytime grade, eerie tiles, monsters (`decisions.md`, Open).
6. **The human-paced model** (`python -m tests.dayone.report --human`) ends a visit once nothing is left to act on
   and nothing is unread, and flags a leave whose screen names no payoff as a bored leave; the 180 s dead gap holds
   within a visit, up to the leave. On seeds 0 to 5 no visit flags. The
   first session now ends about 30 s after the opening's end, so the night's first lines are met on the next return.
   The opening's own stretch near 21 minutes is gone.
   **Content** lives in `content/` (design and story notes in `content/team/`; the shipped opening is
   `app/ashfall_app/opening/opening.toml`) and is never shown to the owner. Before day one is shared: the fixes from the desktop
   playthrough (`docs/research/desktop-playthrough.md`, ranked at its end; the phone pass is done; its first two fixes, the
   Add-row chip's lesson step and a held lesson ending, are shipped, and so are 3, 4, 5, 6, 7 and 8 (7 went with the card line itself). Day two started once the fixes and polish on this
   list were worked through, without waiting on testers, and takes in their feedback as it arrives.
   Day two ships (`app/ashfall_app/opening/day_two.toml`, in `CHAPTERS`; what it built is `docs/design/day-two-plan.md`).
   The model's active-play threshold is an observed habit (a few minutes with nothing notable and the player leaves; no
   source gives a gap, `app/tests/dayone/human_thresholds.toml`). Notifications wait: first see whether testers come
   back without them, from the returns in the telemetry; if built later, opt-in, one per absence for something the
   player chose to wait for, quiet hours, and a Notifier system behind a Null Object.
10. **Week two** (B8 to night 14): the plan and its items are `docs/design/week-two-plan.md`. Built: items 2-4 and
    6-8, item 5's first slice and item 9's rows, items 10, 11 and 12, and days eight, nine, eleven and twelve (item
    13's chapters and item 15's batches), which ship in `CHAPTERS`; day twelve ends at night 14, where the content's end card sits.
    Item 16's art is built: the scene's stages 41-52 and the journal's sketches.
    Left: day one's sink costs the typical route about four hours by day eight, and its returns there now run two
    with nothing new, then four beats in one absence (`weektwo-eight-typical.txt`, V36 to V39), against "never a flood" of new
    things while away (`decisions.md`). Respace them in the content fit pass (item 16), not by tuning the sink.
    Day twelve has the same shape since n1 joined the camp mix: typical's V53->V54 and whenever's V49->V50 each
    hold four (t_b12, t_lamps, t_broth_open, offer_o_shaft) after an empty return. The time-based spacing that once
    separated them gave way when the camp sped up; gate them on each other's landing instead.
    Accepted, not open: week one's per-stage head start at 2 AM carries into day eight's 2 AM strict
    xfail; week two avoids per-stage queuing by design.
12. **Serving from both sites** (asked by the cluster repo's session, 2026-11-05):
    ostmere runs on two sites and keeps serving when either dies; one writable Postgres reached by a multi-host
    `DATABASE_URL` with `target_session_attrs=read-write`, a 3-site etcd as referee. The contract is
    `docs/cross-site-apps.md` in the cluster repo (which that session owns: tell it what the manifests
    need, never edit it); Ashley's `app/ashley/referee/` and `app/ashley/db/pool.py` are the reference. Work: an
    inventory of singletons, site-local state and single-DB-host assumptions; failover-tolerant DB access (drop a
    connection on SQLSTATE 25006 or a lost connection, retry the request); singletons, if any, under an etcd lease
    behind the locator with a Null default; tests against a real Postgres switch and a real TLS etcd, proven able to
    fail. Protocol: report to the cluster session as "done, nothing armed" or "done, waiting on X"; send it the manifests'
    needs (env, secrets, volumes, singletons) in about 25 lines; tell habits about any reusable piece (lease
    client, pool) so both apps solve it one way. A decision only the owner can make is parked here and the rest carries on.
    Inventory (2026-11-05, sent to the cluster session): no singletons in the app (no background tasks, threads or
    LISTEN/NOTIFY; pruning is inline and idempotent under row locks; migrations take `pg_advisory_xact_lock`), so no
    lease. Site-scoped: the `assets-rwx` seed and the pre-backup dump. A failover that loses an acked decision answers
    409 `stale` with the server's step and the page redraws it (`saves/service.py` `Stale`). Built in the app
    (`docs/decisions.md`, "A database failover is replayed once, or answered 503"): the pool check, the replay, the
    checkout budget and the failover log line; habits copies `db/writable.py`.
    The cluster session has ashfall's go to serve from the second site, whose `assets-rwx` is seeded from the first. One run of
    `app/tools/seed_assets.sh` now seeds the first site from the local tree and then the second from the first's live pod, stopping at the
    first failure, so the volumes cannot drift through a hand seed. Half the
    requests cross sites at ~11 ms each. Measured warm against postgres:17: each request takes one
    checkout, a returning player's first paint is 14 sequential round trips (`/api/me` 6, open 8), a decision 7 (11 when
    the session renews), and the save's row lock is held over four (method and output kept outside the repo). Dropping the pool's read-only check for the 25006 replay would save one more per
    checkout but changes the failover design habits shares: agree it with habits first.
13. **Week three** (B13 to night 21): the plan and its items are `docs/design/week-three-plan.md`. Items 1-5 are
    built (a spent share yields, chores retire, a person leaves; blind suites joined, every planted mutant red) and the
    page words them: a spent card's note on the strip, an ended rule's line in Lately, and a leaver kept in the town
    strip until the moment's lines are dismissed. Items 8-10 are checked and built as tests and one client change: an order card
    on a ruled lane taps its staged card, a stage's finish raises a standing's rate, and a chip's several order cards
    are offered side by side (the loader and engine needed no change). Left of item 10: the second skill's own row,
    cure card and first-use lesson are the chapter's content (item 12), and the lesson is not built. The simulator (item 6) plays on from week
    two's saved ends beside each chapter, so item 11's job grows by four chapters: measure it before adding routes.
    Item 12's first chapter, `day_fifteen.toml` (B13 to B14), is reworked and held in `IN_WRITING`; it ships when
    the owner says so. Its two asks are gated on their own moments, outside day twelve's chain (item 16), and the table,
    `meals` and `aim_table` open with B14 as week three's design has it, so smoked has its sink. Item 6's slice for it
    plays week two's push routes on from day twelve's saved end to B14 (`tests/weektwo/test_weektwo_fifteen.py`,
    readouts `weektwo-fifteen*`), and every check passes: each route reaches B14, B13 lands on the calendar, no
    gathered store loses over half its making from the chapter's end, every chip has a cure, the 2 AM test holds
    across the chapter, and a save from day twelve's end loads and plays on. When it ships (moves into `CHAPTERS`), the
    content's one end card moves to its `end_feature` (`belonging`) by itself; the rest of week three waits (Focus now).
    No route runs day twelve's `catch_broth`, `stone_ring` or `spar` (Cooking, Arcana and Melee at 300 XP an hour), so
    the week-three numbers read off typical's levels assume none is run; item 6 decides which routes run them.
    **The dry-store yield** (decisions.md, "A mix keeps going without a dry store") is built. It turned five week-two
    checks red on typical (cap loss of `stew`, `roots` and `smoked`, and twelve's bloom at A32), all traced to
    `n3_ash_ground` starving on `ash` about 16.5 h a day and handing its share to `n3_pick` and `n3_forage`. Its
    `work_s` is now 7200 (day_eight.toml), so it draws `ash` no faster than `n2_clear_roofs` brings it: the pause is
    gone and the five pass, with no beat on the push routes moving more than 0.4 h against main.
14. **Hunt 2026-11-05, wave one's confirmed findings not yet fixed** (verdicts and probes kept outside the repo; each lands as a strict xfail, then the fix):
    - **A heavy chapter-five save's day away costs about 8.9 CPU-s** with the roots rule widened: 4,418 instants, of
      which hands completions are 2,072, order-2 latches 1,400 and the energy store's limit 718 (probe and output kept outside the repo). The hands stay excluded from repeating taps: each landing lets the mix run
      (engine `DESIGN.txt`, "REPEATING TAPS"), and dropping the exclusion livelocks the settle. Coalescing them would
      need a mechanism that runs the mix at each skipped landing; the latches are the other lever. Not urgent while
      the rule stays narrow.
15. **Choice, not protection** (decided in `design/choice-not-protection.md`, with the mixes-and-rules
    work of `design/worth-a-change.md`). Build in this order; each item's gate is its own tests:
    - (g) **Chores and quests with real bounded costs, no suggested rule.** A chore arrives with its problem and a hint
      dot; declining a quest costs the light tier, a store or a slower arrival, never a spiral. Content-gated: waits on
      the chores' and quests' writing under `content/`. Fits into: seasons' chores and the quest offers; costs are
      ordinary flows and light-tier effects.
    - (h) **Defences damage buildings** (a repair cost, a slowed building), never destroy. Content-gated: waits on
      building states and repair content. Fits into: the raid flows (`combat-plan.md`) and a building's modifiers.
    - Goal stints are built: the mix editor's "Run until…" and Next's "+ Plan" queue the mix until a goal row's `until`,
      a queued switch runs over the player's mix until it pops, Next states the running stint's time or "never", and
      Lately lists a stint that popped with how long it ran, when its goal landed and what the save gained in the
      stores its mix makes while it ran (CONTRACT.txt "Goal stints", "Rule runs"; engine DESIGN.txt "Queue mix"). A
      rule's entry does not yet say what its mix made while on (`design/worth-a-change.md`).
    - **From the fun-from-choice research, ranked there:** prestige picks that change what a card does, exclusive
      within a tier (after (e)); saved mixes compared on separate numbers against the player's own earlier best; fights
      as a loadout choice with the forecast shown before committing. Each gets a "Fits into:" line when picked up.
    The +4% later-phase level pay stays until the ladder readout (item 1) shows how phases play.
16. **Content fit pass: less structured beats, more game**: more fun, whimsical and game-like (whether, how and when
    is delegated). Content whose shape exists only to satisfy a
    threshold that is now a readout (beats pinned to a band, ask chains spaced to a per-absence count, unlocks rationed
    per visit) is loosened so the player's own play sets the pace; gates stay where the story needs an order (a
    calendar day, a night, a prior beat). Left:
    - `t_posts` (SL19): four hours after Z1 only so that no absence brings Z1 and SL19. Moved onto O-guard's answer,
      typical's roots lost over half their making 8 h away from day eleven's end (the cap-loss invariant), so it stays
      until day eleven's roots have a sink or typical's rules cover them.
    - Roots at day three's end: the lane foragers (`n1_forage`, `n2_forage`) fill roots faster than `field_track` takes
      them, and typical loses over half their making 8 h away (H4, a strict xfail) until day three's roots have a sink.
    - The camp's shown name can grow with the story (Camp, then Town, then Village).
      The town strip's heading, the Rules tab's section and the town mix's label read one key, `ui.town.title`
      ("Camp"); the camp level (`store_camp`, `ui.games.camp`), the end card, the clock lesson and many lines say camp
      in their own text. A later name at a beat needs later labels keyed on unlocks, as a lane's `later_labels`, and
      a slot in those texts; not built, because the mix label is read where no view is at hand (`mixLabel` in
      `app/client/src/game/orders.ts`, under every rule sentence).
    The week-one floors on dusk 5 and dusk 6 (`day_four.toml`, `day_five.toml`) hold nights, so they stay.
    Fits into: chapters under `content/` and the beats' gates; no new system.
18. **Opt-in reminders to play**: optional, opt-in and configurable reminders for a player who hasn't visited in a
    while, like habits has. Built and armed on both sites (`docs/design/reminders.md`): the
    setting, the single mention, the job and its keys. Left: the note's step 6, a real delivery seen once and not
    twice (subscribe on a desktop browser, the shortest absence, a test account), and the Home Screen test on an iPhone;
    until then delivery is unproven. Fits into: Accounts, the locator's Null Object convention for the sender, and a
    compare-and-set job as the first `python -m ashfall_app.jobs` entry.
24. **The slow skills wait on content** (`decisions.md`, "Finite, and the walls are the world",
    which names the shared rate, each slow skill's held rates and the check each turns red at 900). At game day 13.8 on
    the typical route woodcutting and scavenging are at level 21, foraging 12, arcana 10, cooking 7 and melee 5 (the
    ladder readout). Numbers alone cannot close it: at 900 XP an hour pelt (melee) and smoked (cooking) overflow
    their caps away from chapter ends, damp wood does at day two's end (foraging), stew leaves the babysitter no cure
    for the cold chip on day five, and with arcana at 900 story gates are met before the page states them (one by a
    level find). What lets the rates rise: sinks that keep up with pelt and smoked, finds that cannot meet a gate, or
    late methods and places for each skill. Fits into: the chapters' stores, sinks and finds; no new system.
    Gaps that fail today at a chapter's end, each a strict xfail (W7, K6):
    - Pelt: no sink in reach once `pelt_bedding` and `hide_flaps` are built, so `hunt_wolf` overfills it 24 h away
      from the ends of days six and twelve (`hall` waits on beams).
    - Dry wood: no sink past the fire, the watches and the stews, so `hand_on_stone` overfills it away from the ends
      of days four and fifteen.
    - The track's input ratio: `field_track` takes about 5400 roots an hour at its full share against about 1330
      made, so it is held to a share where it takes about 110 stones an hour of about 260 made; stones overfill away
      from the ends of days eight to twelve, and roots from day eleven's.
25. **The redesign**: every in-game screen gets a new look and feedback language; the front page only restyles to
    match. `docs/design/redesign.md` is the plan and the build order, and `docs/design/redesign/merge.html` is the
    design. Step 1 (routing: a refusal is red plus the missing need with no text, a success a story line only) shipped;
    step 2 (the look: hairlines, four sizes, ember's two jobs) and step 3 (the mix bar's legend, the merge's hues, the
    ledger's groups) shipped; step 4's first half (the chronicle replacing the Log, causes, the kind filter) shipped;
    "Since you left" is next. Left from step 3: the ledger's Town
    and Outposts groups wait for a served store-group field (through the contract) when the first such store lands;
    the Mixes list's small bars drop their initials for a legend in step 6. Left from step 4: a line shared by several
    levels of one skill names the skill, not the level. For step 6: at 390 wide the camp bar's store readout
    overlaps the Chronicle button (it overlapped the Log button before). Fits into: the feedback ladder,
    Chronicle and unwrap, and Offers; no new system. Load `writing-craft` for every player-facing string.

## Where things are

| What | Where |
|---|---|
| Repo, CI | GitHub, Actions; pipeline and deploy in `docs/engineering.md` |
| Live site | https://ostmere.yggdrasil.pub (deploy: the cluster repo, via Flux) |
| Research downloads (Widman map stamps, Gessner scans) | outside the repo |
| Design canvas (six phone screens) | https://claude.ai/artifact/H6Foqa7diKmwDS1KGKJuxC, source in `docs/design/canvas/` |
| Redesign comparison (six designs and the merge) | https://claude.ai/artifact/3zBFvQDBec1J6UWPqCuc6s, the chosen design in `docs/design/redesign/` |
| Look test canvas | https://claude.ai/artifact/1EDLESML2xgre6iuvonRt1, source in `docs/design/look-test-canvas/` |
| Writing and model tests | https://claude.ai/artifact/WbXhGSQedRy2SnN2gM3rNd, source in `docs/research/writing-test/` |
| Strawman doc (superseded by `decisions.md` where they differ) | https://claude.ai/code/artifact/571817bb-99df-498c-be29-3202fe5ef76e |
