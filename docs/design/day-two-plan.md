# Day two: what engineering builds

Day two runs from B3 (the first arrival, day one's last beat) to B4, through beats J1–J4 and steps A15–A19. Its
design is in `content/` (`team/day-two.md`, never shown to the owner); this file holds only what the code needs: which
systems it touches, the new kinds of things and their fit, rough sizes, and what must exist before its content ships.
Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a week or more.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A townsperson who works | Lanes (a lane of their own), Cards (their versions of the gathering cards on it), Standing orders (their task is a rule on that lane) | Work beside the player's hands is a lane, and a side lane's rule is a single task (`decisions.md`, "The mix"). With one person a share is always all of them, so the town's mix with people as shares waits for the second arrival |
| A default rule set by the story | Standing orders: an outcome that installs an order (the "default orders" the row already plans) | The person starts working the moment they arrive, so a beat that lands while the player is away costs nothing |
| The first offer | Offers and quests (planned row): its first piece | Accepting and declining with state in the save is exactly that row; the page's offer row is the mix offer's row with two answers |
| A one-off that runs on whichever lane the answer picks | Cards (two one-off cards, one per lane), started by the answer | A card's lane is fixed today; two cards with one shared done mark keep it fixed |
| Two builds shown together as one choice | Cards (crafts), as day one's | Unchanged shape |
| A rate bonus for the new worker | Modifiers (`LaneSpeed` on their lane) | Already a modifier target |
| Camp levels 7 and 8 (8 held, lifted by B4) | the Camp's levels, day one's held-level schema | Data |
| Skill levels 21–25, and finds beside shipped speed-ups | Pacing curve (append only), level pays as triggers | Data, plus a lock check |
| A second night and morning on the story's clock | Triggers and standing actions, as day one's night | Data |

## Work, by system

Items 1–4's interface: engine `DESIGN.txt`, "TOWNSFOLK, INSTALLED RULES AND OFFERS", and `api/CONTRACT.txt`, "A LANE
RUN BY RULES" and "OFFERS".

1. **Lanes and orders for a townsperson** (**L**). A declared lane that the page draws as a row under the hands strip:
   who, what they are doing, its bar, `Change` (the rule editor's simple view, scoped to that lane). Rules may target a
   non-hands lane (a single task, never a mix). Their cards never show in Tasks, train no skill, and make camp items at
   the hands' rate. The row's label can change at a beat (J1). View: the lane's state and its rules in order_states.
2. **An outcome that installs a rule** (**S**). B3's outcome sets the townsperson's default rule; an offer's answer
   sets a one-off rule above it. Validation: the installed rule is an ordinary rule the player can edit or remove.
3. **Offers, first piece** (**M**). Content: an offer entry (id, gate, two answers, each answer's outcome); save state
   (open, and which answer); View; the page's offer row (a line, two answers, each naming its time cost), through the
   arrival queue like any arrival; never expires. Gate vocabulary: `offer` answered, either answer.
4. **Answering an offer as an order** (**S**, engine and simulator only). Every verb has an order, so the simulator
   needs "answer offers of this kind with X". Whether the Rules tab shows it in day two is an open content call.
5. **Feature cards** (**S**). Day one's end card drops its "still being written" line once day two ships; day two's
   last beat (B4) carries the out-of-fiction end-of-current-content card.
6. **The content file** (**M**). `day_two.toml`, merged after `day_one.toml` (new ids only), with its stores, standing
   actions, cards, order cards, triggers, aims, Camp levels and curve. Answer-dependent line sets for B4 are chosen by
   the answer's state, never by text.
7. **Levels** (**S**). Append levels 21–25 to the curve. Day two reaches shipped levels that pay speed three running,
   so it adds a find beside the speed-up at a few of them, each as a new trigger; check the release lock reads that as
   additive, or the "every third level pays a thing" test fails once routes reach them.
8. **Art** (**M**). A second figure with a pose per task and the few the beats ask for (listed in `content/team/day-two.md`,
   "Art"); two new built pieces; one world layer gains a second state at J2 (`tools/scene`, stages 17–24).
9. **Flat check** (**S**). `content/team/flatcheck.py` reads `day_one:` only; teach it `day_two:` (same checks, its own
   near promise), or a generic `day_*:` list.
10. **The simulator past B3** (**M**). Day-two routes (the same ten), policies for the townsperson's task and the offer's
    answer, per-visit and per-absence counters, the 2 AM test with the second lane and the installed rules, B4's
    landing band, and the line state lists (`report --lines`) the writers' brief is built from.
