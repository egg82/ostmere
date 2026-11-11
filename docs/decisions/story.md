# Story

The story, its tone and its voices.

## Story is the spine

**The story carries the whole game**: the worldbuilding, the villagers' own hard personal decisions, the
hardships, daily life and the progression are all story. It is not a track beside the mechanics; the mechanics exist
to make it happen and let the player steer it.

- A main story with a real ending; expansions later (the Melvor route). Mini-stories alongside.
- **The ending is a real finish without fanfare**: the game is finished, but there is still a
  ton of work to do. You didn't save the world, just this one small part of it, for the foreseeable future; the
  rest of it is what expansions are for. The exact feel is decided in `content/`.
- **The player's path shapes the ending**; how, and how much, is decided in `content/` and in the
  systems that carry it.
- **Tropes are shorthand, used knowingly**: readers understand them at once, so avoiding them on reflex is its
  own mistake. And a trope resolving the way the reader expects is the point of a trope, not a failure: most resolve
  as promised. Subverting everything confuses people and becomes dull and predictable in itself, so a turn is
  spent on a few chosen ones, where it matters.
- The ending is reached by progression and planning, never gated by reflexes. (An unlock-everything RPG that leaves a
  maxed-out player still unable to beat the final boss loses them after days.)
- The progression itself tells the story where it can (Progress Knight: beggar to knight, aging and rebirth, each promotion
  a beat). Spreadsheet depth is welcome when it serves the story; Progress Knight's one failing is the time it demands.
- The reveal pace holds to the end, and the story must not run out before the mechanics do (Cookie Clicker loses
  players when reveals thin into an achievement grind).
- Reveals need earned waiting: a trainer that skipped the wait was boring too.
- **No spoilers for the owner,** who plays the game. The owner sets the shape (tone, themes, length, what to feel); the
  specifics (beats, clues, twists, mini-stories, exact numbers, the map past the next hill) live in one content folder
  the owner doesn't open. Commits, reports and simulation output name beats by number, never by what happens; a question
  for the owner is asked in spoiler-free terms or flagged so the owner can choose to look. Runtime Claude calls write some mini-stories fresh.

## Tone: gritty survival, dark story, dry humor

The genre word is **grimdark**.
The register is A Dark Room's, and Progress Knight's as it darkened, in D&D-style high fantasy and magic. Not Norse or Yggdrasil: that is habits' world.

**Premise:** magic gone wrong broke the world, and you remember nothing. Memory loss puts player
and character on the same footing: both learn the world together, and progression is remembering and rediscovering.
The spine to the ending is learning what happened and trying to fix it. Three reasons pull the thread without saying
how you relate to the catastrophe: something about you is unusual (curiosity: who you are, why you have this power,
the pull Slay the Princess had), the town needs you (responsibility), and the world isn't finished breaking (stakes,
never a countdown). Your role in the catastrophe is deliberately not decided at the owner's level, since knowing you're at
the centre would hand the owner the twist; it, and everything else below this, is in `content/`. The amnesia trope's
resolution follows the rule on tropes in "Story is the spine": expected unless it is one of the few chosen turns.

**You're just a dude, or a chick** (Grim Dawn's "what are you even doing here?"): not a chosen
one, a nobody in way over their head. Scale is personal, epic things happening to someone small; the humor is dry and
wry about that gap. Whatever is unusual about you doesn't make you a hero, it just got you into this. You're not the
best mage around, just somehow the one stuck doing the thing (again; what that means is in `content/`):
chosen by circumstance, never destiny, and others in town may be stronger mages than you. You're not irreplaceable
either, just the most convenient person around, and you can't figure out the word "no"; that is why the jobs only you do
fall to you. **The joke is only ever about choices the player made:** every job is an offer the player picks, and
declining costs nothing; the character never accepts something the player didn't choose. The humor lands after a yes
("you said yes. Of course you did"), wry about the player's own urge to take everything on, never taking a decision away
(otherwise a player wondering why their character keeps saying yes reads it as no control).

**Magic is wonder to the outsider and craft to those who know it** (magic is science not yet understood;
Galadriel's mirror, where the elves don't know what the hobbits mean by magic). It has consistent rules:
you start as the outsider and relearn it, so wonder moves on to whatever you don't understand yet; an optimizer can
learn and exploit it; and it solves story problems only as far as the player understands it (Sanderson's first
law), so no hand-wave rescues. **Magic is a tool, not the villain:** people did what was done with it. Whether
the catastrophe was intent, accident or both is decided in `content/`. To the player it starts wondrous.

**A power fantasy in the numbers, a nobody in the story,** keeping both Melvor's climb (just some guy who soon
buys a ton of land) and staying just a guy all the way through. Mechanically you get strong: numbers climb, cascades
fire, the early wolf dies in a second, the town grows big. Narratively the world stays bigger than you, deeper
threats outclass you, and people still hand you the jobs nobody wants: competence grows, status doesn't (Grim Dawn).
The gap between how strong you are and how little anyone cares is a source of the dry humor. You run the town
**by default, never by title**: you built the first fire and can't say no, so people follow whoever keeps doing the
work. How that tension plays out is in `content/`.

**Theme: significance earned by choice, not granted by destiny.** Just some dude can build a town; Rosa Parks was
just someone on a bus until she wasn't. You become someone through what you build and stand for, and the people
follow for that. Hope breaks through the grit by sheer determination, willpower and some godforsaken luck. The luck
is the story's (wry about how many wins were dumb luck), never the numbers'.

**Humor like habits' and A Dark Room's:** mostly dry, chuckle-worthy wit, now and then a genuinely funny moment,
never too often, and some gallows humor: laughing because otherwise you'd cry, the world having ended. For
Claude-written lines the rate is set in code (which call may be a funny one), never asked for with a frequency word.

**Voice: the narration leans passive, people act.** The narration's register is A Dark Room's: spare, lowercase, the
world happening around you, and often the two halves of a cause: what you did, then what the world did about it.
People are the exception: villagers, visitors and
anyone else with a will speak and act in active voice, since what they do is theirs. Consistency is per kind of line,
not one voice for everything.

**Character creation is identity, never numbers:** at least a name and pronouns (every prompt is given them, so no
line guesses), appearance if the visuals have room for it. Nothing chosen at creation affects progress, and all of it
can be changed later (the elf lesson).

Candidate element: tower defense (The Perfect Tower II's twist on it lands); defending the town against
the broken world is a natural home for it. Not decided.

**Goosebumps, not horror:** things that go bump in the night and an eldritch edge (not horror, but the eerie edge a grimy
magic game carries). Dread and wrongness; gore is fine, but never jump scares; a vague
feeling that something is very wrong. Texture reference: Slay the Princess, the mirror showing something you'd rather
not see (texture only: whether anything like it applies to the player character is decided in `content/`). Sparing, so
it lands. The game knows the player's real night, so eerier flavour may surface more then, never touching progress.

**Tropes named as fair game** (whether and how they appear is decided in `content/`): a dead god, as The
Owl House's Boiling Isles do it (the land itself the corpse of a titan, a lingering wrongness), or Jay Kristoff's
city on a god's bones (Godsgrave, in the Nevernight books). Guardrail from the latter: interesting, but very
on-the-nose and literal at the end; leave it implied and strange, never spelled out.

**A premise's consequences are followed through honestly.** The writing test's throwaway sunless valley shows why: it
wouldn't be cold, it would be dead, very quickly, unless magic intervened (Nevernight's multiple suns do this well).
Whatever broke the world has real, consistent knock-on effects (weather, food, light, what still grows); where magic
is why something still works, that is a fact of the world with its own rules, never a hand-wave.

**Creatures follow from biology**: how a thing lives, reproduces, evolved or was made, what it eats and what
eats it, and its anatomy follows from those answers, the same honesty as the sunless world. Principles in
`docs/research/creature-design.md`; the creatures themselves are in `content/`.

**Magic has rules; the eldritch is never fully explained** (cosmic horror rarely is). Magic is the science you
rediscover and can master; what lies past it (the wrongness, anything god-sized) stays partly unknowable on purpose.
Even the journal's "perfect once known" stops at its edge: some entries are never finished. The register meant by
goosebumps: "have you ever heard a god scream?", a line that implies something vast and wrong without showing it. One or
two sentences (that line is a one-sentence take on r/TwoSentenceHorror), delivered where text already lives (a
chronicle line, a journal margin, what a newcomer mutters by the fire), so it lands in a two-minute peek; how often, for
Claude-written ones, is set in code.

**A running joke or signature motif** carries the dry humor and makes it memorable (Spaceplan's potatoes are what players
remember of it, years on). Chosen in `content/`, so it lands unannounced.

## Catalogue, gates, triggers, unlocks and offers, as built

How these parts behave today, moved from their rows in `systems.md`.

Catalogue: null is an empty catalogue for tests, and its checks name ids and fields, never text, since the owner reads CI
output. The opening's file loads alone; each later chapter is its own file merged on (new ids only, filling the
markers past the content so far), so a file boundary is a spoiler boundary. A chapter's `[[town_cards]]` entry (a
card's fields, `lanes` and an id pattern with `{lane}`) is expanded by the loader to one ordinary card per lane
(`app/ashfall_app/opening/town.py`), a lane expanding where it is declared; the engine sees only cards. A chapter's
`while_running` table gives a card an earlier file shipped the entries it holds while running, on a side the chapter
declares (`app/ashfall_app/opening/chapters.py`).

Gates: one vocabulary from the start, where habits grew six or seven separate ones. An offer's gate is a trigger the
loader makes; "answered, either answer" is one Unlocked condition. LaneRules counts the player-set orders on a ruled
lane, and only a trigger's `when` or an offer's gate may read it.

Triggers: deterministic, so what a level or a count earns shows the moment it is earned. Gates is the vocabulary;
triggers are the engine firing it. The end is one too, with its time kept (`Save.ended_at`; engine `DESIGN.txt`, "The
end"). What the next beat waits on is a query over them: the pending triggers with when each lands
(`app/ashfall_app/engine/pending.py`), read against the content's goals (`app/ashfall_app/opening/goals.py`) into the
view's goals (`app/ashfall_app/api/goals.py`), which the page marks (`app/client/src/game/story.ts`, the wait line
`app/client/src/ui/waitline.ts`). Each store and level goal, and each skill's next level, also gets when it lands at
the rates as set, a tap of the hands set aside, and the dry store that binds it (`app/ashfall_app/api/goalrows.py`,
`app/ashfall_app/api/setrates.py`), which the mix and condition editors list for an edit
(`app/client/src/ui/goaltimes.ts`). "The player set a rule on a ruled lane" is one: the LaneRules subject, fired at
the decision that sets it (engine `DESIGN.txt`, "Lane rules"). A later prestige phase's level pays are one table per
skill, keyed by the level within the phase, which the merge expands into ordinary triggers
(`app/ashfall_app/opening/phase_pays.py`).

Unlocks: the client never decides what exists. A person joining the town is one (`app/ashfall_app/engine/joins.py`: an
outcome part that adds the joined unlock and turns the lane's always task into its share), and a person leaving
another (`app/ashfall_app/engine/leaves.py`: the left unlock, from which `app/ashfall_app/engine/gone.py` derives the
lane's cards out of play and the standings it stops). The page decides when an unlocked part is first drawn, from the
view, the content and what the account keeps (`app/client/src/game/shown.ts`; `decisions.md`, "The screen arrives
when it means something"). Features (the ledger, the craft list) are page parts the engine only switches on. Facts
that only grow live here too: a card retired, an offer shown, answered, and by which answer, a person joined or left.
The stated aim is read off this set the same way: each aim in the content names the unlock it starts at, and the page
shows the last one that holds (`app/ashfall_app/opening/aims.py`).

Offers and quests: authored or Claude-proposed, timing decided in code; state is three only-growing unlocks (shown,
answered, which answer). Answering is a Command, an order verb like a tap, so a rule or the queue can answer, and an
offer's optional kind lets one rule answer every offer of it by role (engine `DESIGN.txt`, "OFFER KINDS";
`app/ashfall_app/engine/answers.py`, `AnswerKind`). Never expires in its first piece. Declining costs no progress.
Interface: engine `DESIGN.txt`, "Offers", and `app/ashfall_app/api/CONTRACT.txt`, "OFFERS". Built:
`app/ashfall_app/engine/offerstate.py` (where an offer stands), `app/ashfall_app/engine/answering.py` (an answer
landing); the loader makes each offer's trigger (`app/ashfall_app/opening/convert.py`).
