# Clock

Day, night and seasons.

## Day and night run on the story's clock

The scene's night, morning and day follow the story, not the player's real clock (a real-life cycle
like habits' won't fit a game played in visits, so it is gamified). Something the player set in motion that lands
while they are away plays out in full when they return. Look-tested on 2026-10-16: day is the scene's normal
warm grade (separate day grades all read washed out); night is a darker grade (`night_n2` on branch `daylight-test`)
in which the fire is the only warm light and the camp's built pieces stay legible; the change from night to morning is
the visible beat.

## Seasons change the game, more than slightly

Idle Fantasy's seasonals work mostly for the new content, which keeps the game fresh, then the change of scenery and
the rewards; here seasons differ more than its slightly, and its latest took only about half a day to clear.
- The world's own seasons come round on a cycle of real days. What they are is a fact of the broken world
  (followed through honestly, like everything else) and lives in `content/`.
- Each season changes how the game plays, not only how it looks: a different grade over the whole town, actions
  and creatures only it has, different threats, seasonal options that make your mixes worth re-tuning, and its own
  stories and quests. A season adds and raises, never lowers: a saved mix keeps its rates, as the mix rules
  require, so a season changing while you're away breaks nothing.
- Nothing is missable. A season comes back, and whatever you hadn't finished waits for it; nothing on the main
  path needs a season's content. So no season creates a schedule to keep.
- Sized to last: a season's content is paced like the rest of the game, never a half-day burst.
- **Each season brings its own chores**: problems specific to that season, so a new season brings
  different trouble from the last, and a season may bring several. Each chore arrives with its problem and a hint dot, and
  the rule that answers it is the player's to write. A rule written for a chore goes away when its season ends
  (probably), so a chore that returns in a later year asks for the rule again. Chores are a deliberate sink for the town's time, the player's time and banked resources,
  and each fits the story naturally rather than reading as upkeep for its own sake. Leaving a chore undone is a real
  option with a real cost: some costs build up while it waits, some stay small. Doing it and living with what it
  brings are both legitimate choices, never a trap: either way, it's a choice.
