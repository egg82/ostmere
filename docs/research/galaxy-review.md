# galaxy.click's review of the day-one build (2026-10-21)

Note: the title is now chosen, *The Breaking of Ostmere*; what follows still says Ashfall.

galaxy.click's staff declined the listing for now: come back when the game is complete or nearly so. Their email is
quoted at the end. What follows is what their feedback says, checked against the logs and the database where it could
be, and what it asks of the game. The work it creates is in `open-work.md`, "Before resubmitting".

## What happened in their session

Of Oct 20–21 sessions, only one played day one: save 15, 10:44–11:43 UTC, ending about three hours before the email.
It is the reviewer's by elimination, not by identity.

- **They stopped at dusk, not at the end of the content.** `saves.ended_at` (3492 game s) is the opening's end; the
  day-one chapter goes on after it, and its last beat carries the real end card. They left under a minute after dusk.
  After dusk the next step waits on the night, in real time, and the screen shows nothing but the aim line changing.
  So "I'm assuming I've made it to the end?" was the dusk read as the end. Another player (Oct 18, save 4) tapped
  the card that waits on the night 31 times over 40 minutes, failing each time, and left.
- **The mix helped only with its first two cards.** They made the guided first mix at 4 minutes and left it alone
  until 26 s before dusk; every gathering card unlocked after it they tapped by hand (91 taps against 5 mix and rule
  changes). "Repeat the same few tasks endlessly" is that. Nothing tells a player that a new card can join the mix.
  They found mix editing and rules on their own at the end, and praised the rules.

How this was read: `app/tools/play_report.py` over the Loki export (logs start Oct 17), then
`select ... from saves` / `save_decisions where save_id = 15` on the ashfall database.

## What their feedback asks for

- **Writing that does not read as an LLM's.** Their complaint: samey vocabulary, florid text that obscures meaning,
  and notation like the Camp bar's "Camp level 2 → the wall takes more 5 → 7". The reader is someone who does not use
  LLMs and spotted it at once; a model's own voice pass cannot hear it, so the fix needs a human reader or editor.
  This conflicts with game lines shipping unreviewed: open, the owner's call.
- **A new title.** "Ashfall" was the second one they had been sent recently; *-fall is a common LLM title. They asked
  that it not come from a model: the owner names it, an agent does the mechanical rename (repo, domain, page text, listing
  image).
- **Less derivative story beats** ("taking story beats from elsewhere"): a human cold read of the story plan before
  more content is built on it.
- **Sounds** read as LLM-picked too (said more lightly): swap them by a human ear.
- **Explain the repeat-action rules** to newcomers; they liked the rules and the layout.

## Their email

> After having a playthrough of the first day, I can see it being a fairly story-heavy game, and that's absolutely
> fine. [...] (I'm assuming I've made it to the end of the current content? Nothing seems to be moving on and there's
> not much to do but repeat the same few tasks endlessly.)
>
> I think the sticking point for us currently is that you're having this made one piece at a time and that makes it
> difficult for us to know what the rest of the game will be like. [...] once you have the game complete, or very
> nearly so, we could come back and look at it again, but some things would probably have to change for wider
> acceptance.
>
> The sounds and text (moreso a problem with the text) are very much as one would expect from an LLM. Because it's
> taking story beats from elsewhere, and because it has a certain 'style' that's not going to go well with the vocal
> part of our playerbase, they would let you know in comments how poorly it reads.
>
> There are people like me who don't spend a lot of time interacting with LLMs or agents, and their 'writing' always
> feels a bit samey. They seem to have a limited vocab and the same ways of writing things, with florid text that
> obscures meaning. ie: "Camp level 2 -> the wall takes more 5 → 7" The title itself might be something you'd care to
> rethink at some stage. Everything is *.fall, it's Claude's title du jour and we're seeing a lot of it. Your game is
> the second 'Ashfall' we've had submitted recently. Don't ask The Machine for another title - consider going into
> some of the fiction you consumed when you were younger and think about terms those authors used.
>
> [...]
>
> You've done a really nice job with the layout - none of that 'title at the top' nonsense, and the rules for
> repeated actions are a very nice touch, although they might need some explaining for some users. I can see clearly
> that you've taken the time to remove or adjust some of the more obvious LLMisms from the CSS.
