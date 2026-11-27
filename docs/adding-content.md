# Adding content: the checklist

Read this before changing anything in a chapter's data (a day toml in `app/ashfall_app/opening/`, `content/beats.yaml`,
a store, card, trigger, offer, person, aim, line or scene state). Each item below is something a past change missed and
a later PR had to fix, most-missed first. Where a gate catches it, the gate is named. The rest are on you to check, so
check them.

## Before you push

1. **Docs in the same change.** If you add or change a system, put its `docs/systems.md` row change, its decision-file
   paragraph and any `app/ashfall_app/api/contract/` text in your `doc-delta.txt`; the orchestrator applies it
   before merge. No gate requires the row, and this was the most-missed item (14 follow-up PRs).
2. **The scene shows it.**
   - An outcome that joins, leaves or sets a person doing something carries `whereabouts` (gated:
     `app/tests/test_scene_people.py`).
   - A finishable build has a scene state or a `NO_SCENE` entry (gated: `app/tests/test_scene_shown.py`).
   - A card carries `site`: the scene layer its work is done at, or `no_site` and why (gated, new cards cannot be held:
     `app/tests/test_scene_sites.py`). A card and its `twin_of` name the same one.
   - A person's lane carries `by_day`: the card of theirs whose site they stand at while idle by day, or `at_fire` and
     why (gated: `app/tests/test_scene_day.py`; lanes with none are held in `people_day.HELD_UNDECIDED`, which only
     shrinks). A card named there needs a layer `site`, and the scene's table (`tools/scene/people_day.py`) names the same
     layer.
   - **Not gated:** when you remove or rename a card, store or group id, grep `tools/scene/` (poses, layers,
     conditions), lessons, journal subjects and aims for it. A folded crew's card stayed in a pose condition once.
   - Render new scene states headless by day and night and look at them.
   - **Any change that adds or moves a scene layer renders the whole composite** at the affected chapter ends, by day and
     night, and looks at it as a player would: crowding, builds the camp has outgrown, props away from their purpose, idle
     people. The new layer alone looking right has shipped a scene that did not make sense as a whole. Not gated.
3. **Read the readouts for the chapter you touched** once CI has played it: the largest absence, decide counts, cap
   loss and beat landings in `app/tests/readouts/`. These are readouts that never fail, so only a reader catches a
   week with nothing to decide or four beats landing together (nine past misses).
4. **Every answer keeps a lasting consequence** (a sourced modifier, an unlock something reads, a tally or an `echo`),
   and a one-off store is never set against a lasting change (`docs/decisions/principles.md`). The first half is gated
   (`app/tests/held/answers.json`); the one-off-against-lasting half is not.
5. **A promise is broken only by a choice, never by a clock** (`docs/decisions/principles.md`). Not gated beyond
   "something reads it".
6. **The next step is on screen with how far along it is.** Whatever holds the next beat, including a hidden store a
   trigger feeding the beat waits on, shows as the goal with its value (`app/tests/opening/test_goal_defs.py`). An aim
   whose step is done gives way.
7. **Groups and twins.** A town card on a group is on every member with their own list; a trip's town twin adds the
   same to a shared tally (`check_group_abilities`, `check_player_only`). Town view rows and crew sizes are a readout
   (`app/tests/readouts/town.txt`): read it. Moving people: rebase a copy of the owner's save under the branch and
   check the hand-over fires once and nothing goes negative (`app/tests/opening/test_hand_over_rebase.py`).
8. **Every tapped card has its own upside text.** A missing `upside_key` is gated; two cards sharing one is not.
9. **Nothing is named before it exists.** A line, chip or offer must not mention a thing the player can't have yet on
   some route (stores and actions are gated by `unlock_order_checks`; text is not).
10. **Spoilers.** Commit messages, PR text, test names and readout text name beats, lines and offers by id, never by
    what happens. Nothing checks this.

## Mechanical steps

- A loader pass that expands an authored field goes in `app/ashfall_app/opening/expansions.py::with_expansions`, so
  `app/tests/opening/edited.py` sees the same content (`app/tests/opening/test_edited_merge.py`).
- Regenerate `app/client/fixtures/real_chip_cards.json` when a card, chip or store changes; its test
  (`app/tests/test_rule_chip_cases_wire.py`) runs in CI, not in `gates.sh`, so run it.
- A new chapter goes in `CHAPTERS` (or `IN_WRITING`) in `opening/schema.py`, with its `content/beats.yaml` ids and
  `content/decisions.jsonl` rows.
- A new gate goes in `app/tools/gates.sh` **and** the "Structural gates" table in `docs/engineering.md` (via
  `doc-delta.txt`).
- A held-list entry that gains its field leaves the list in the same change; a count is never raised.
- Run the full unit shards (`python -m tools.shards a|b|c` from `app/`) and `app/tools/gates.sh`.
- Readouts: never replay locally. A pull request plays the chapters it touches; pull its readouts with
  `python -m tools.readouts_pull <run-id>` and read the diff before committing.
