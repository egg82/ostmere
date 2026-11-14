# Systems

The inventory an agent checks before building something new (`CLAUDE.md`, the fit pass): what kind of thing is this,
and which row below already answers that question? Extend or combine that system; add a row only when none fits, and
say why in the open-work item's "Fits into:" line. Update this file in the same change that adds, merges or retires a
system, and when a "Duplicates / planned" cell is resolved (delete the cell's text, not the row).

Each cell is about a sentence; how a system works and why lives in its file under `docs/decisions/` (the index is
`decisions.md`) or in engine `DESIGN.txt`, which "Where" names. A row naming no code is still planned. The Pattern cell
names what a row comes over from in habits, the owner's earlier agent-built app (its `docs/systems.md`), and a row's kind
when it is not a system. Rows were planned from `decisions.md` and `core-loop.md` before the first line of code.
Content (what the systems carry) stays in `content/`; nothing here names it.

## What counts as a system

A **system** sits behind the service locator, so its implementation can be swapped: an A/B variant, a Null Object for
tests and tools, a fast stand-in for the simulator. That costs an interface and a registration, so a thing earns it
only by passing all four:

1. **Many callers, across packages.** One caller is a function call, not a system.
2. **One question, behind a narrow interface.** If the interface keeps widening, it is two systems.
3. **A second implementation is plausible.** An A/B rule, a null (Claude off, sound off, an empty catalogue), a faster
   variant. If nothing could ever replace it, it is a plain import.
4. **It owns a policy or state**, not a data shape. "Which beat comes next" is a policy; "what a beat looks like" is
   data.

The test is strict at the boundary and silent about the inside: split a system when its inside keeps growing or its
interface answers a second question. Everything else is a **model** (the engine's own types), **data** (authored Type
Objects in the catalogue) or a **module** (a pure helper), each a plain import. The usual A/B targets are the policies
(pacing curve, threat schedule, arrivals, the next beat, the writer's route, placement), so a variant is one
registration away and the simulator can run both.

## The engine

Most of what `decisions.md` asks (the 2 AM test, no offline cap, time away earning what time present earns, every
number showing its source, odds before you commit) is a property of one deterministic engine. Its contract:

- **State advances event to event.** Between events every rate is constant; the engine jumps to the next event (a
  store empties or fills, a bar or card completes, an order fires, a season turns), applies it, and recomputes rates.
- **Values are segments, never sums of steps:** (start time, start value, rate), with event times by exact integer
  division, so splitting a span at a decision or a snapshot cannot round differently.
- **Same-instant events resolve in one total order** (time, priority, sequence), with a cap on firings per instant, so
  every chain ends.
- **Reading never writes engine state.** What the player has seen lives in a presentation store the engine cannot
  import (an import test); state changes only at a decision and at snapshots, which a test proves change nothing. A
  tap bonus, if any, is linear in time since the last tap.
- **Every verb has an order**, queued or standing, and the simulator fails any verb without one: a babysitter can act
  at 03:00 and an order can't. Prestige alone is by hand, its carry window doing the order's job
  (`docs/design/prestige-phases.md`).
- **Order conditions are ones the engine can solve for:** thresholds on stores, levels and time, and discrete state; a
  boundary-chasing order gets hysteresis or a "hold" target. Content gates use the same vocabulary.
- **Chance never touches the engine.** Losses from threats are flows (an expected drain, whole losses landing as the
  total crosses a unit); seeded chance picks only when the story shows a raid and what kind.
- **What-if is a fork of what the player knows:** odds, ETAs and "runs 7 h" run the engine forward on a copy of the
  known view, future seeded events masked. The editors' goal rows are the exception: one dry run per edit, each goal's
  time read off the rates as set, no saved mix marked as having a better option.
- **Claude's output is input, never a rate:** recorded in the save's log at an engine time and replayed from there.
- **The client samples; it never simulates.** The server serves the current segment and the next events; the page
  interpolates against the clock. No rule exists twice.
- **A new engine part adds its own state type, never fields on `Save`.** Today's fields are the held list in
  `app/tests/held/save_fields.json`; `app/tests/test_save_fields.py` fails on a new field and on a removed one listed.
- **The pacing simulator drives this engine** with scripted players (babysitter, whenever, sharp and typical, held;
  `by_hand`, `lazy` and `keeper`, reported), and a deliberately weakened order language must turn the 2 AM test red.

## Time and chance

| System | Owns (the question it answers) | Where | Pattern | Who asks, how | Duplicates / planned |
|---|---|---|---|---|---|
| Clock | What time is it for this save: real day, season, part of day, night? | | Value object; one injectable time source (habits' clock) | Each save runs its own clock; the simulator swaps in a fast one; real night feeds flavour only | None |
| Chance | Which flourish, rarity or mini-story, and when is a raid shown? | | Draws hashed from (seed, stream, key), not a running counter, so adding a draw never shifts another (habits' `rand`) | The engine cannot import it (an import test) | None |

## The engine's parts

| System | Owns | Where | Pattern | Who asks, how | Duplicates / planned |
|---|---|---|---|---|---|
| Engine core | What is true at time t, and when is the next event? | engine `DESIGN.txt` | Module: discrete-event simulation over piecewise-linear segments; pure functions | Everything, under the contract above | None |
| Cards | What work can be done, what it makes and costs, which skill it trains, how many times | engine `DESIGN.txt`, "CARDS"; `decisions/mixes.md` | Data + model. Type Object: lines while it runs, lumps per completion, an optional completion cap; Command for the tap | Tapped by hand or run in a mix; a one-off is a card with a cap | Standing actions (a fire burning) are not cards |
| Mixes | Which cards run continuously, at what shares | `app/ashfall_app/engine/mixruns.py`, `app/ashfall_app/engine/spent.py`, `engine.plan.mix_layer`; DESIGN "THE TOWN'S MIX", "SPENT" | Model. Composite (saved mixes nest); one mechanism for the hands and the town | The player switches the hands' mix; the town's always rule switches the town's | Buildings running cards: pooled work is a known gap |
| Stores and caps | How much of each thing, and its limit | `docs/design/banked-time-plan.md`; DESIGN "BANKED TIME" | Model. Segments; a cap reached is an event | Finite everywhere; past a cap production is lost on purpose, to sinks sized so a day away loses at most half | None |
| Standing orders and the queue | When X, do Y; what happens next when this finishes | `app/ashfall_app/engine/installs.py`, `engine.plan.order_states`, `app/client/src/ui/rulewhy.ts`, `app/client/src/ui/stint.ts`, `app/client/src/game/queue.ts`; DESIGN "Queue mix" | Model. Ordered (condition, verb) rules, first match wins within a kind; an order's mix is a pushdown over the player's, per layer; a queue of verbs | The player's rules, the queue and story outcomes; the Rules tab shows where each stands and the queue as Next | Evaluation applying every verb that can act at an instant (DESIGN "Evaluation applies every verb") |
| Modifiers | What changes a rate or a store's cap, and why is it that number | `app/ashfall_app/engine/heldentries.py` | Model. One stack per rate or cap, each entry with its source | Buildings, tools, spells, prestige, seasons, injuries, supply; "where does this come from" is a query | Combat's strengths and odds in the stack (DESIGN "FIGHTS") |
| Pacing curve | XP to level, the shared target, prestige timing | `app/tests/dayone/growth.py`; `decisions/pacing.md` | Data tables behind one interface | The engine; the simulator runs two curves side by side as an A/B | None |
| Forecast | When does each next level and fill land if the player changes nothing? | `app/ashfall_app/engine/forecast.py`; CONTRACT.txt "Forecast" | Module (read). Instant-by-instant replay with nobody deciding, bounded | The page, when a save opens or its plan changes; kept across plain advances | None |
| Lanes | Where taps run, and whose time they take | `app/ashfall_app/engine/decisions.py`, `app/ashfall_app/engine/cure_reading.py`, `app/ashfall_app/engine/plan.py`, `app/ashfall_app/engine/retap.py`; `decisions/mixes.md` | Model. One tap at a time per lane; the hands lane is the player's own time | Taps by the player on the hands lane; a townsperson's ruled lane runs the task its rules set | None |
| Chips | Which statuses (cold, hungry, tired) show now, and what they change | | Model + data. A latched condition in the order vocabulary; while shown, its effects are modifiers sourced by the chip | Read off an ordinary store; nothing sets a chip directly | None |
| Triggers | Which content gates have fired, and what the next beat waits on | `app/ashfall_app/engine/pending.py`, `app/ashfall_app/opening/goals.py`, `app/ashfall_app/api/goals.py`, `app/ashfall_app/api/goalrows.py`, `app/ashfall_app/api/setrates.py`, `app/ashfall_app/opening/phase_pays.py`, `app/client/src/game/story.ts`, `app/client/src/ui/waitline.ts`, `app/client/src/ui/goaltimes.ts`, `Save.ended_at` | Model + data. A condition that fires once per save and applies an outcome | The engine fires Gates' vocabulary; the view's goals and the editors' goal times read the pending ones | None |
| Unlocks | What the player can see and use | `app/ashfall_app/engine/joins.py`, `app/ashfall_app/engine/leaves.py`, `app/ashfall_app/engine/gone.py`, `app/ashfall_app/opening/aims.py`, `app/client/src/game/shown.ts`; `decisions/story.md` | Model. A set in the save, grown only by outcomes | The client never decides what exists, only when an unlocked part is first drawn (`decisions.md`, "The screen arrives when it means something") | None |
| Combat | How a fight, raid or supply-line attack goes | `docs/design/combat-plan.md`, `app/ashfall_app/api/CONTRACT.txt` "FIGHTS"; DESIGN "FIGHTS" | Model + data, a system once a second threat schedule runs beside the first. Component: a fight on a card or a standing action; odds as Modifiers entries; losses as flows; Type Object rosters | Preparation decides, chance shows; only the threat schedule is a policy worth A/B | None |
| Spells | Which rules combine into which spell, and its effects | | Model + data. Rules as data combined by a small interpreter; effects are modifiers and events | Deterministic from the build; cascades are chains of same-instant events under the firing cap | None |
| Expeditions | Who goes, where, what returns | `docs/design/banked-time-plan.md`; DESIGN "BANKED TIME"; `decisions/combat.md` | Data on Cards, a model once a second member goes. A trip is an uncapped card with inputs; finds are triggers on its completion count | Run in the mix like any card | Backup, stance and wide expeditions (that part's KNOWN GAPS) |
| Regions | Which regions are open, time spent in each, their outpost sites | | Model. State in the engine | Time in a region drives its threat strength | None |
| Simulator | Do the invariants hold over a whole run, and how does it play? | `app/tests/dayone/routes.py` (`TOOL_USERS`), `app/tests/dayone/human_flags.py` (`lands_behind`), `app/tests/dayone/caploss.py`, `app/tests/weektwo/routes.py`, `app/tests/weektwo/counters.py`, `app/tests/readout_snapshot.py`, `app/tests/readouts/`; `docs/design/sim-invariants.md` | Tool. Scripted players driving the engine; each `report.py` readout reported against its committed text | CI; fails only on an invariant, readouts are reported, never failed; `python -m tests.readout_snapshot --write` commits them | `docs/open-work.md`, "Pacing simulator past the opening" |

## The world and its people

| System | Owns | Where | Pattern | Who asks, how | Duplicates / planned |
|---|---|---|---|---|---|
| Catalogue | What authored data exists, and is it valid? | `app/ashfall_app/opening/town.py`, `app/ashfall_app/opening/chapters.py`; `decisions/story.md` | Registry loaded once, validated at start; each chapter a file merged on, so a file boundary is a spoiler boundary (habits' content loader) | Everything that reads content; null is an empty catalogue. **Checks name ids and fields, never text:** the owner reads CI output | None |
| Gates | May this line, beat, arrival or offer appear now? | | Module. Specification over the engine's condition vocabulary; one vocabulary, where habits grew six or seven | A trigger's `when` and an offer's gate | None |
| Story | Which beat is due, and what it changes | | Beats as data with gates; effects as engine events (habits' storyteller and sagas, rebuilt on gates) | A twist the plan couldn't foresee pauses only its own branch | None |
| Offers and quests | What is on offer, accepted or declined, and what declining changes | `app/ashfall_app/engine/offerstate.py`, `app/ashfall_app/engine/answering.py`, `app/ashfall_app/engine/answers.py` (`AnswerKind`), `app/ashfall_app/opening/convert.py`, `app/ashfall_app/api/CONTRACT.txt` "OFFERS"; DESIGN "Offers" | Model + data. Type Object (an offer and its answers); its state three only-growing unlocks | Answering is a Command, so the player, a rule or the queue answers, a rule by offer kind | None |
| Knowledge | What the player knows exactly; what is still unknown | `app/ashfall_app/api/CONTRACT.txt` "JOURNAL" | Model. A known set per save; unknown is a value | Forks run on it; the journal renders it, first as a page reading of `View.fights` (known means fought above 0); an entry and its notes are unlocks | The stored known set, when a fork needs one |
| People | Who lives here, their role and tier, who arrives next | `app/ashfall_app/opening/name_checks.py` (`name_key`, filling a text's `{<lane>}` slot); `decisions/people.md` | System (arrivals) + model. Arrivals as engine events from the needs met; roster as engine state (habits' roster, lives and souls) | Arrival policy is the A/B target | One name per person in every save; the per-save draw from a pool |
| Social ties | Friendships, feuds, cliques becoming gangs | | Model. State fed by the living world's history (habits' bonds) | Feeds emergent offers; never a rate | None |
| Living world | Where everyone is in the day; chatter, visitors, scenes | | Day planner (Double Buffer), Event Queue for appends (habits, as modules after its cleanup) | Shows the engine's state, never changes it | None |
| Town map and world map | What stands where; which regions are revealed | | Map authority (claims with rules); stamps placed by code (habits' map authority; world map new) | You choose what; the town chooses where | None |
| Writer | What Claude writes, when, from which facts | `docs/research/llm-writing.md` | Registry of job kinds, a queue, caps; seeded lenses, shuffle-bag pools (habits' writer) | Code decides the kind of line, Claude the words; null is Claude off, authored lines standing in | None |
| Lessons | Which system is taught now, and which step of it | `app/client/src/game/lessons.ts`, `app/client/src/ui/lessons.ts`; `decisions/feedback.md` | Module (page). Lessons as data, one runner; the glow as its highlight | The page; done or skipped kept in SavePresentation, off by AccountSettings | Not a system: one caller, nothing to swap |
| Chronicle and unwrap | What happened and what caused it, and since the last visit | `app/client/src/game/chronicle.ts`, `app/client/src/ui/chroniclesheet.ts`, `app/client/src/game/rulerows.ts`, `app/ashfall_app/api/line_causes.py`, `app/client/src/game/chapter.ts`, `app/client/src/ui/chapter.ts`, `app/client/src/game/arrivals.ts`, `app/ashfall_app/engine/rulelog.py`, `app/ashfall_app/saves/ruleruns.py`, `app/client/src/ui/rulelately.ts`, `app/client/src/game/keeps.ts`, `app/ashfall_app/accounts/presentation.py`, `app/client/src/game/fights.ts`; `decisions/world.md` | Module + presentation store. Events re-derived from the snapshot, rendered to lines; announcements as an Event Queue (habits' chronicle and announcements) | The page on a return; the cursor lives in the presentation store | None |

## The app

| System | Owns | Where | Pattern | Who asks, how | Duplicates / planned |
|---|---|---|---|---|---|
| Saves | Several per account, each with its own seed, clock and log | `app/ashfall_app/saves/interface.py`, `app/ashfall_app/saves/load.py`, `app/ashfall_app/saves/service.py`, `app/ashfall_app/saves/games.py`, `app/ashfall_app/saves/manifest.py`, `app/ashfall_app/saves/strip.py`, `app/ashfall_app/db/tables.py`, `app/ashfall_app/db/manifests.py`, `app/client/src/ui/games.ts`, `app/client/src/ui/places.ts`, `app/client/src/ui/gamedelete.ts`; `decisions/saves.md` | Append-only decision log plus segment snapshots (Memento), rebased at load (habits' replay; Minecraft's data fixers, Factorio's migration files) | The api, through the Saves interface (null: no database); `GET /api/saves/{save_id}/view` reads a stored view without opening it | None |
| Accounts and sign-in | Who is asking | `app/ashfall_app/accounts/interface.py`, `app/ashfall_app/accounts/limits.py`, `app/ashfall_app/accounts/moving.py`, `app/ashfall_app/accounts/join.py`, `app/ashfall_app/api/device_routes.py`; `decisions/accounts.md` | Session from a device cookie (habits' sessions only, `docs/signin-proposal.md`<!--external--> there) | Every request; an anonymous account per browser, joined across devices by a transfer code (`decisions.md`, "A plain browser game") | None |
| Service locator | Which implementation answers each system | | Module. Service Locator with Null Object defaults (habits' `services.py`<!--external-->) | The systems above register here | None |
| Logs, job runs, retention | What happened, and what piles up | `docs/engineering.md`, `app/ashfall_app/feedback/service.py`, `app/client/src/telemetry.ts`, `app/ashfall_app/page_config.py`; `decisions/accounts.md` | Module. One logfmt setup; a run table; owner-read tables whose writer deletes past a limit on insert | the owner, with `python -m ashfall_app.feedback list`, Loki and Umami | None |
| Reminders | Is this device due a reminder now, and did one go? | `app/ashfall_app/reminders/`, `app/ashfall_app/jobs/`, `app/ashfall_app/db/reminders.py` (`reminder_devices`); `docs/design/reminders.md` | Module. Specification (a pure `due`) polled by a CronJob, a compare-and-set claim before the send; the sender a Strategy with a Null Object default | Only the job asks `due`, so it fails the many-callers test | A locator row once a second caller of `due` (the story digest) exists |
| Feedback | What plays when something happens | `app/client/src/ui/ladder.ts`, `app/client/src/ui/cards.ts`, `app/client/src/game.css`; `docs/design/opening-screen.md`, "The feedback ladder" | System (page). Observer of served events; effects and sounds as data (habits' tap ladder and reward sounds) | Served events, a failed tap (`api.models.Step`) among them; null is silent | None |
| Page shell | The page's state and views; which build it runs | `app/client/src/begin.ts` (`entry`), `app/client/src/app/selfupdate.ts`, `app/client/src/app/straight.ts`, `app/client/src/api/api.ts` (`REQUEST_TIMEOUT_MS`), `app/client/src/ui/frontdress.ts`, `app/ashfall_app/web/app.py`, `app/ashfall_app/web/page.py`; `decisions/saves.md` | Module (page). Pushdown state stack: page, sheet, ceremony (habits' `Mode`, not its 21-mixin `App`; its self-update and boot guard) | The browser; served at /build/<build>/, so a page only runs its own build's bundle | None |
