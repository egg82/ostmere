# Decisions

**North star: an Idle Fantasy replacement.** The game that lives on the owner's phone for spare moments, with the OSRS-style
skill web and the town, without its demands on attention, and with the story it lacks: Melvor, Idle Fantasy and Idle
Awakening refined for a player with little time who dislikes notifications and active play. A complete-in-a-weekend clicker
(Tower Wizard, a favourite) is a different game, maybe a later one; it doesn't steer this one.

What it lacks, to gain here: a feeling of going somewhere (levels rise, the world doesn't move; here progress
changes the world and moves the story), and more than one path (its loop converges on combat, so finishing combat
finishes the game; here combat is one path among crafting, the town, exploring and magic, each feeding the story).

What it keeps of Idle Fantasy is the role it plays: a solid, familiar progression loop in a high-fantasy world,
always something worth doing on opening it, never asking for more than the player has. Story there comes only from item
descriptions and OSRS lore; here the story is direct, with that kind of lore as a second layer for whoever feels like
reading.

A single-player idle game with clicker moments, made for the owner (friends may play too, each their own account and
save): a web app like `habits.yggdrasil.pub`, with its own accounts ("A plain browser game", below). Purely for fun, unrelated to habits. Played in spare minutes at any hour: a few on a workday,
more in evenings and on weekends.

**Reuse a mechanic before adding one** (game design 101). Where it is reasonable, a new thing the player
meets is an existing mechanic and visual with a variation (a one-off is a card with a cap), not a new control to
learn: less to confuse the player, less to build. Reuse, never abuse: when a mechanic has to be bent into something it
isn't, so the new system becomes a pile of special cases on the old one (WoW's habit: spaghetti and edge
cases), it gets its own. The code-side twin is the fit pass in `CLAUDE.md`.

A decision says how a part of the game works now and why, with what was rejected. They live in `docs/decisions/`, one
file per system or group of systems (the systems are `systems.md`). Read this index, then the files for the systems a
change touches; `principles.md` binds every change. A new decision goes in the file for its system, with a line here.
Code and docs cite a decision by its title, quoted after a mention of `decisions.md`: the title is an entry below, or a
`###` heading or bold lead inside one of the files, found with `grep -rn "Title" docs/decisions/`.
`app/tests/test_decision_citations.py` fails when a cited title resolves to nothing.

## Principles

- [Words used here](decisions/principles.md): card, mix, hands strip, ledger, rule, camp bar and unwrap.
- [Fun, but never vying for attention](decisions/principles.md): attention earns nothing; the 2 AM test, no offline cap, no daily resets, no notifications unless asked, calm shown in the design.
- [Cascades are the peak](decisions/principles.md): the best moment is a good build setting off a deterministic chain reaction.
- [Progress is stated, never hinted](decisions/principles.md): every gate on progress, and the next step with how far along it is, is on screen in plain words.
- [No blind permanent choices](decisions/principles.md): every choice is a tradeoff; a weight that can't be seen when chosen is free to change later.
- [Built on habits](decisions/principles.md): what comes from habits and what is new code here.
- [Never](decisions/principles.md): store-shaped mechanics, card framing, and the lines the story never crosses.
- [Open](decisions/principles.md): art still to test, the name, tower defense.
- [Why the engine's contract reads as it does](decisions/principles.md): the reason behind each rule of the engine's contract in `systems.md`.

## Chance

- [Chance decides how nice, never how far](decisions/chance.md): randomness picks flourishes and which mini-story, never progress; a chance effect shows the moment it is earned.

## Clock

- [Day and night run on the story's clock](decisions/clock.md): the scene's night and day follow the story, not the player's real clock.
- [Seasons change the game, more than slightly](decisions/clock.md): seasons add play, threats and chores on a cycle of real days, never lower a mix, and nothing is missable.

## Pacing curve

- [Finite, and the walls are the world](decisions/pacing.md): everything is capped; the opening's hooks and pace, idle time paying in the old, the screen arriving when it means something, and one shared target for every skill.
- [Prestige is per skill, and finite](decisions/pacing.md): a skill pushes past its top by the player's click; a building's prestige is its fall and rebuilding; no bonus needs remembering.
- [Stores, caps, the pacing curve and the forecast, as built](decisions/pacing.md): caps lose production to sinks, one curve for every skill, a forecast that only draws what comes true.

## Mixes and standing orders

- [You and the town: two layers, joint projects](decisions/mixes.md): you run one mix, the town works in parallel under your orders, and big things need both.
- [The mix: several actions at once](decisions/mixes.md): one card tapped or mixed, shares and an exact ledger, saved mixes that nest, rules the player writes, editors that open simple.
- [Automation is designed, not clicked](decisions/mixes.md): rules built by tapping, a priority list of "when X, do Y" lines.
- [Cards, mixes, lanes, orders and modifiers, as built](decisions/mixes.md): the two layers' mixes, dry-store pauses, cut-ins, ruled lanes, installed rules and the queue as they run.

## Combat

- [Combat is a large pillar](decisions/combat.md): threats ramp by region and time, never by your defences; a fight costs what you put in; chance shows, preparation decides.
- [Combat and expeditions, as built](decisions/combat.md): a fight on a card with tally stores and no event of its own; a trip is a card with inputs.

## Simulator

- [Length: about 3 months, set by play, not playtime](decisions/simulator.md): the length a typical route takes, a back half that never slows, goals in view, promises on screen kept, bad states with a cure in reach.
- [Tuned means checked](decisions/simulator.md): a check fails only on an invariant; rhythm is a readout; figures round and display one way; the UI speaks in numbers.
- [The simulator, as built](decisions/simulator.md): the invariants it fails on, the readouts it prints and how they are approved.

## Story

- [Story is the spine](decisions/story.md): the story carries the whole game; a real ending, tropes used knowingly, and no spoilers for the owner.
- [Tone: gritty survival, dark story, dry humor](decisions/story.md): grimdark; the premise at the owner's level, a nobody in way over their head, magic with rules, the voices and the humor.
- [Catalogue, gates, triggers, unlocks and offers, as built](decisions/story.md): chapter files as spoiler boundaries, one gate vocabulary, what the next beat waits on, offers answered by rule.

## Knowledge

- [What the mods added is built in](decisions/knowledge.md): odds, ETAs and rates first-class; the registers; what can be tapped looks tappable; story lines stay until read; no verdicts; blind until learned; the journal.

## People and the town

- [Nothing appears; everything is made](decisions/people.md): people arrive for a reason you made, by the needs the town meets, and rise into roles.
- [The town](decisions/people.md): a town from nothing, gritty but never a spiral; souls, social lives and quests, deaths on the light tier, outposts and supply lines.
- [People, as built](decisions/people.md): arrival policy, notables, and a person's name filled into text by lane.

## Living world and maps

- [Something to watch, any time, for hours](decisions/world.md): something to watch, read and think about whenever it is opened, and watching earns nothing extra.
- [A world map](decisions/world.md): a front-of-the-book map at two scales, from engraved stamps placed by code.
- [Art: a drawn, living town over bars](decisions/world.md): Time Fantasy packs graded dark in code, warm means yours, the type, and sourced art for the map and journal.
- [The chronicle and unwrap, as built](decisions/world.md): the arrival queue, what the rules did lately, fights since the last view, the visits record.

## Writer

- [Public, eventually: every save its own, on one budget](decisions/writer.md): four layers, cheapest first, under one global daily Claude budget.
- [Content is a pipeline](decisions/writer.md): authored, Claude-written and generated content; a line is written for every moment it can appear.

## Saves

- [Multiple saves, each its own run](decisions/saves.md): several saves, each its own seed and clock, around the same spine.
- [Developed live, forward-only by preference](decisions/saves.md): changes apply forward with no per-change machinery, and a deploy never resets a game.
- [Saves never die with a device](decisions/saves.md): the server writes the save on every decision; the page never holds the only copy.
- [A database failover is replayed once, or answered 503](decisions/saves.md): how a request survives a Postgres failover between the two sites, and what was rejected.
- [Saves and the page shell, as built](decisions/saves.md): rebase at load, manifests stored once, bounded catch-up, several games; the front page, boot guard and self-update.

## Accounts and sign-in

- [A plain browser game: the account is the browser](decisions/accounts.md): an anonymous cookie account joined across devices by a code or recovery words, playable inside another site's frame.
- [Accounts, logs and reminders, as built](decisions/accounts.md): devices and joins, owner-read tables pruned on insert, and why reminders are not a system yet.

## Feedback

- [Rewarding at any moment](decisions/feedback.md): juice on every visit and every touch, with a ceiling written as a ladder, and the motion, flash, sound and reach rule.
- [Feedback and lessons, as built](decisions/feedback.md): the ladder as data, the failed tap's pulse, lessons as data with one runner.
