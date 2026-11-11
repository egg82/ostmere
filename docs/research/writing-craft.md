# Writing craft: rules for the game's player-facing text, by voice

What a writer (human or model) and a human editor check when writing or revising any line a player reads. It answers
galaxy.click's complaint (`galaxy-review.md`): samey vocabulary, florid text that obscures meaning, and notation like
"Camp level 2 → the wall takes more 5 → 7". Runtime generation (facts per call, pools, which model) is
`llm-writing.md`; this doc does not repeat it. The general method grew into a cross-project `writing-craft` skill,
with measured tells, the knowing-narrator and appended-beat findings, and blind
tests against people and detectors; load it for any writing pass. This doc keeps the game's own voices.

Sources are in `writing-craft/`, one notes file per topic, each row with its URL and whether it was read in full or
only as a snippet. Failbetter and Wikipedia pages were read through a summarizer, so their quotes are secondhand.
Evidence is marked in a word: **verbatim** (a game's own strings), **measured** (counted over many texts),
**practitioner** (a working writer's or editor's rule), **opinion** (critics, forums), **snippet** (seen only in a
search result). As of 2026-10-21.

## 1. Game UI

The voice most at risk: labels, controls, costs and effect lines are written in the model's own register by default,
and the reviewer's example came from here (`ui-text-notes.jsonl`).

**Finding: terse labels hold; a line that says what a change does needs one short sentence.** Every game read keeps
labels as bare nouns ("Eternity gain multiplier", "Inserter capacity bonus") and writes an effect as a plain clause or
sentence. None of them puts an arrow or "from X to Y" in a game string. No published UX-writing guidance on arrow
phrasing was found, so this rests on the games, not on a style guide (verbatim; the null search is in the notes).

- **Say what the thing now does, subject first.** "the rickety cart will carry more wood from the forest"; "The mouse
  and cursors are twice as efficient." (verbatim, A Dark Room; Cookie Clicker snippet)
- **Name the consequence the player cares about, not the stat.** "carrying more means longer expeditions to the
  wilds" (verbatim, A Dark Room)
- **A changed number keeps the sentence and changes only the number,** highlighted by the UI. "Deal 6 damage." becomes
  "Deal 9 damage."; no arrow, no "from 6 to 9" (verbatim, Slay the Spire). A Dark Room drops the number entirely and
  lets a tooltip carry the rate, but incremental players ask how big an effect is before buying ("+25%, +50%";
  opinion, snippet), so show the amount.
- **Notation belongs in totals and compact lists, a sentence in the single choice.** Antimatter Dimensions writes one
  effect three ways: "Multiply Eternity gain by {value}" for one source, "Eternity gain ×{value}" for the total, a bare
  noun for the label. A Dark Room's rates are "+1 per 10s" in a tooltip because the prose is elsewhere (verbatim).
- **A cap is a consequence, not "max".** "more traps won't help now"; "no more room for huts." (verbatim)
- **A count that changes is shown by the counter, not repeated in text.** "a weathered family takes up in one of the
  huts." while the population number ticks (verbatim, A Dark Room)
- **Direction can ride on colour and position** (gains green, losses red, always in the same place) instead of words
  (practitioner, Terraria wiki, snippet).
- **Numerals in UI, a percent sign with numerals, exactly as the screen shows them** (practitioner, Microsoft style
  guide, snippet).

**The reviewer's line, rewritten.** "Camp level 2 → the wall takes more 5 → 7" puts two arrows on two different
axes (level reached, amount changed) and drops the noun the number counts. As one sentence with the new number
highlighted: *"Camp level 2: the warm wall dries 7 wood at a time instead of 5."* A Dark Room's form, if the amount
moves to a tooltip: *"the warm wall dries more wood at once"*.

`decisions.md`, "Two registers", now holds this rule.

## 2. World lines (log, journal, arrivals, aims)

Line-level rules from writers of short game text and fiction (`worldbuilding-notes.jsonl`). They sit under
`llm-writing.md`'s rule that curated lines land a turn the reader completes: the one detail below can be the turn.

- **Cap length hard, per kind of line.** Failbetter caps its storylet parts at 30, 20 and 100 words and replaces
  summary phrases ("All across X...") with one person, place or act (practitioner, secondhand). Each kind of line here
  gets its own cap where the kind is defined.
- **One vivid concrete detail, then stop.** Don't describe its surroundings; one image implies the room. Don't write
  the connective tissue between beats: "the player's imagination is your ally" (practitioner, Failbetter, secondhand).
- **The trace, not the feeling.** Make a state visible through what can be seen, never name it; show the aftermath
  (an object, its state, its position) and let the reader infer the event (practitioner: Failbetter; Smith and Worch,
  GDC 2010, snippet). Time and mood come through what people are doing, not through light.
- **Name odd concrete things and don't explain them.** "molluscs from the slime banks", "city of fallen pylons":
  ordinary goods, food and trade imply a world better than history does. Unexplained is fine only when the detail is
  physically specific (opinion, on Vance).
- **Omit only what you know.** A line may leave out what the writer could state (a private canon behind it); a line
  that withholds with nothing behind it is vagueness, not implication (practitioner, Hemingway, secondhand).
- **Details do work, not survey.** No line after line of setting, and no details that fit together into a neat
  catalogue (opinion, Harrison via a secondary article).
- **The swap test.** Change a few nouns; if the line reads the same in another setting, or as a modern thriller line,
  it is generic (opinion, Le Guin, snippet).
- **One register.** No modern idiom or managerial vocabulary in the world voice; Le Guin's objection is to register
  that wobbles, and the excerpt read does not settle plain against elevated (opinion, snippet).

No primary source was found on how A Dark Room's or Kentucky Route Zero's writers write a line; the house voice in
`decisions.md` stands on its own.

## 3. People talking

The notes support little here. What there is: text-game players flag dialogue that is polished but has no human
voice, and their fix is to give a speaker only the details that person would notice, vary sentence shapes and read it
aloud (practitioner, Sindome forum). Le Guin names "wrong conversational tone" as the instant giveaway of fake fantasy
(opinion, snippet). A sarcastic in-world voice in a log was praised in Spaceplan (opinion, one review). The decision to
start from habits' third register stands; this research adds nothing to it.

## 4. Story beats and tropes

From `tropes-notes.jsonl` and `audience-notes.jsonl`. The evidence is weak: listicles, essays, a few Hacker News
threads and Steam reviews; r/incremental_games, the obvious audience, was not read because the fetch tool refused
reddit. Read it as a map of what readers already file as template, not as a verdict on any one beat.

**The rule the evidence does support: a familiar beat is not the problem; an unturned one is.** The praised examples
keep the convention and take a left turn (Midsommar against The Wicker Man; The Dog Stars on the endless journey).

- **Worn:** the fire-then-stranger opening with building unlocks (A Dark Room, from Candy Box; players name the
  lineage); the stark-UI, slow-reveal, lore-through-progression template itself; "people are the real monsters" said
  as a parable; raiders and gangs in wasteland costume, zombies, cannibals, chosen ones, villains evil for no reason;
  hard moral choices staged as dilemmas; an ending that loops back to the start ("All this for...this!?").
- **Usable with a turn:** fragmentary environmental storytelling (the backstory implied, never said: the most praised
  thing in the reviews), whose risk is pacing, since slow reveals let players drift off; the journey with no
  destination; survivors in a safe zone, or one tightly held rule of survival; the friendly village with a sinister
  belief, where the stock sacrificial finale is what reads stale; the dying world, whose appeal is voice, not setting;
  moral choices only when they cost something and ask "was it worth it".
- **Fresh:** escalation that changes the kind of play (Universal Paperclips, Kittens Game), against escalation where
  "a few words change, a few colors change, an old meter fills more often"; a shift of scale that is funny and
  shocking; a destination the title gives away, with the twists on the way as the pleasure; a short game that doesn't
  overstay its welcome; more than one ending (one comment).

## 5. The tells checklist

A flag list for a human reader, never a pass/fail gate or a regex in CI (the project does not gate prose
programmatically). One or two tells in a passage are coincidence; many together are the signal. Fix the vagueness under
a tell, not just its words: swapping "delve" for "explore" leaves the same sentence (`llm-tells-notes.jsonl`). The
fiction tells already in `llm-writing.md` (exposition, tidy endings, morals, softened dark registers) still apply.

Strongest evidence first:

1. **"Not X, but Y" and its kin** ("It's not just X, it's Y", "not because X but because Y", "It's not bold. It's
   backwards."). The heaviest-weighted pattern in EQ-Bench's slop score and the tell editors and players name most
   (measured, practitioner). Fix: state Y.
2. **Stock body beats and scene furniture:** voice barely a whisper, heart pounding in chest, breath caught in throat,
   words hung in the air, dust motes danced, door creaked open, casting long shadows, a chill down the spine
   (measured, slop-forensics trigrams). Fix: one detail particular to this scene.
3. **Over-used words** from the same lists: whispered, flickered, faintly, lingered, rustled, acrid, bustling,
   cacophony, calloused, arcane, ashen (measured). The same probe found ash, ember, dust, silence and weight are *not*
   over-used. Claude models measured weak on word-level tics specifically (measured, snippet).
4. **Stock names:** Elara, Aris, Alaric, Aethel-anything, Elara Voss and her variants across every major model
   (measured; practitioner). Fix: names come from an outside list, never the model.
5. **Inflated verbs:** delve, underscore, showcase, serves as, stands as, boasts, features (measured in academic text;
   practitioner). Fix: "is", "has", "shows".
6. **Lists of three** used to sound complete; sentences ending in an "-ing" tail ("...reflecting its continued
   relevance"); sections that end on a vague hopeful note (practitioner). Fix: keep what is supported, cut the tail.
7. **Em dashes in quantity** (practitioner; players flag them, others rightly say one proves nothing). Fix: comma or
   full stop.
8. **Rhetorical question answered at once; dramatic fragments** ("She waited. And waited."); **redundant adjective
   pairs** ("dark and brooding"); **metaphors that don't clarify** ("a symphony of colors"); **telling after showing**;
   prose too clean to have a voice (practitioner, community writing guide). Fix: keep the question or the answer;
   delete the metaphor; cut the told half.
9. **A style that shifts between scenes,** ornate in one place and plain in the next (practitioner, itch.io, snippet).

Not supported by anything found: Claude-specific tics beyond the shared lists, "something shifted" as a tell, and
stock "-fall" titles. The reviewer's two "Ashfall" submissions are first-hand evidence of the last, and enough.

## 6. The title

Chosen by the owner, never proposed by a model (the reviewer's ask). From `naming-notes.jsonl`, all inferred from
Wikipedia-level sources, since no developer account of a naming was found: good titles come from inside the game,
such as its premise or opening scene (A Dark Room, Universal Paperclips), a place in its world (Kentucky Route Zero) or
a lore character (Hollow Knight). A candidate passes when: an exact search of Steam, itch.io, the app stores and Google
finds no game or well-known work by that name; the domain is free; someone who hears it can spell it and guess the
genre; it is short, with no invented spelling. No source measured which title shapes read as generated.

## 7. How a rewrite is judged

The model that wrote a line cannot hear its register, so its own voice pass, or a fresh agent's, does not count as
the check (the reviewer heard at once what passes had let through). A rewrite is judged by readers who don't use LLMs,
blind, old against new, as a batch rather than single lines: readers score single short pieces at about chance, and
the measurable deficit is sameness across many lines (measured; `llm-writing.md`). The question to ask them is which
version says what it means and which sounds written by a person, not which they like.
