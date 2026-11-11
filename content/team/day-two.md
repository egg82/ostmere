# Day two: from the first arrival to the ridge

Spoilers: this file is under `content/` and never shown to the owner. It picks up where `day-one.md` ends (B3, somewhere in
the long grey story day 2) and runs through the evening, the second night and story day 3 to B4. Its data twin is
`beats.yaml`'s `day_two:` list (ids, gates, shape fields); its canon is C-promise-18 and C-beat-80 to C-beat-86 in
`canon.jsonl` (tentative until the lead confirms); its decisions are D-82 to D-91. **Every number below is a target**:
the simulator's routes set them, and the line state lists are generated from those routes, not written by hand.
Schema, engine and page work are in `docs/design/day-two-plan.md` (spoiler-free); this file says what they must carry.

Binding, carried from day one: day and night run on the story's clock; a planned moment that lands while the player is
away plays in full on return; nothing is lost *because* the player was away (D-59).

## The shape

Four visits, as day one counts them. V1 is the rest of the session B3 lands in (or the return that reveals it); V2–V4
are the next sessions a typical player has, 1–12 hours apart.

The day is one causal chain the player builds: **you give her the stool, she gives her name; you make room for her,
she means to stay; she asks for her cart, and someone walks up to the ridge.** Every link is a step the player takes;
the story says what it looks like from outside.

- **The near question** (C-promise-18, *what is up on the ridge?*): the dark square H3 showed and never named. Opened by
  J1 (her eyes go to the ridge when she gives her name), advanced on every visit, paid by B4 (her people's cart, and it
  is gone).
- **The deep pull** gets one touch, the stool (C-promise-8, J1): it rocks under her, she wedges it, and by morning it
  rocks again. Nothing new about the ground (B5's), the hand on the stone (B6's) or old snares (H4 is enough).
- **What day two teaches:** the first person who works for the camp (her lane, run by a rule, D-83) and the first offer
  (B4, D-87). One each, spaced: her lane in V1, the offer in V2 or V3.
- **Story clock.** B3 lands whenever P0.4 completes. The grey afternoon runs on until a quarter of a game hour after
  A15; then dusk, a night of about one game hour, and story day 3, which lasts until B4 however long that takes. Still
  the Still.

## The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| V1 | 0 | giving her name, she looks at the ridge a long time | who is she, and what is up there for her? | J1 (opens) |
| V2 | 1–12 h | in the night, a sound carried down from the ridge: wood on stone, a long scrape, then nothing; by morning the square is gone from the ridge (art only, no line says so) | what was that, up there? | J2, J3, J4 |
| V3 | 1–10 h | with a roof of her own, she asks: her people's cart, on the ridge. Will you fetch it? | will you go, and what's left of it? | the offer (O-cart) |
| V4 | 0–12 h | the cart is gone, dragged off, wolf prints all round where it stood; she takes the news without a word | the wolves have been that close: what comes next? | B4 (pays) |

Each pull is a gap left open and not a timer: the player can see the ridge in the art on every visit, and the change in
it (the square gone) is there for whoever looks (`decisions.md`, "Something to watch, any time, for hours").

## Timeline

Minutes inside a visit are active minutes; game hours are after B3 lands. **Bold** marks the bigger new things.

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| V1 (3–6 min, the B3 session or the return that reveals it) | reads B3 and re-tunes for two (day one's); meets **her row** under the hands strip, already foraging; taps **Give her the stool** (A15, glows: the one next step); **builds or queues the raised bed** (opened by A15, on the stores full at B3: V1's decision, D-105); optionally **changes her task**; may take **her first rule** if roots fill | her row and her default rule (B3's outcome, D-83); A15 (B3); J1 at A15; dusk 15 game min after A15 (a stayer sees the grade turn; no wait card, D-89) | B3's: N1 at the fire on the player's side; then on the stool, the stool rocking | l_her_row, l_stool_1, l_stool_2, l_name (J1), l_her_first, l_dusk_2 |
| V2 (6–10 min) | reads the night (J2, J3); taps **Make room for two** (A16); **chooses** which of two builds first; **switches the mix** and **her task** (the shelter wants poles, the woodstack stones); builds or queues with When ready | night 2 (A15 + 0.25 h); J2 three minutes in; A16 on the cards from J2 with its countdown to first light (look_out's shape); morning 3 (A15 + 1.25 h, J3); A16 → J4: her shelter and the woodstack in view, unready | night grade with two at the fire; the ridge without its square from J2 on; the camp by day 3; her shelter or the woodstack | l_night_2a, l_night_2b (J2), l_morning_3 (J3), l_room_1, l_room_2 (J4), l_shelter, l_woodstack (each with order variants), l_shelter_fail, l_woodstack_fail |
| V3 (3–6 min) | answers **the first offer**: goes, or lets her go; if going, **the walk** takes the hands about 6 game min (or is queued); builds the second build; takes the rule offered on a falling or full line | O-cart when her shelter is built (often while away, shown on return); the walk card (hands) on Go, or her walk (her lane) on the other answer; Camp 7 by now | the player at the gap facing out, or N1 leaving through it | l_offer_1, l_offer_2, l_yes (Go only), l_walk_go, l_she_goes, l_camp_7 |
| V4, or V3 for a player who waits out the walk (B4) | reads B4; meets day two's end card; re-tunes her rules for the evening | B4 at the walk's end; Camp 8 lifted (B4 raises the camp cap); the aim moves on | the player back at the fire, or N1 back; N1 at the fire, not looking at the ridge | l_b4_1 to l_b4_4 (went), l_b4_h1 to l_b4_h3 (she went), l_camp_8, the end card |

**Per visit** (day one's checks, unchanged): at least one bigger and three new things, the first within 60 s; at least
one decision; no idle stretch over 90 s inside the activity window; no run of one card over 3; effort between bigger
things at most 10. V1's bigger thing is her row; V2's the two builds; V3's the offer; V4's B4.

**Per absence:** at most two unlocks. V1→V2: night 2 (A16 comes with it) and morning 3. V2→V3: the second build's
upside and O-cart (one moment with her shelter's finish). A return that reveals a queued B3 brings B3 with her row (one
moment) and A15. **Nothing on the night's clock starts before A15**, so a B3 that landed while the player was away
never brings the night with it (D-84).

**Landing targets** (game hours after B3): B4 on the typical route 10–30 h; the babysitter not before 1.6 h (A15, the
night, A16, the shelter, the offer and a 6-minute walk, nothing waiting); every route no later than the babysitter's
plus one visit gap for each step that waits for the player (A15, A16, the offer: `bands.presence_steps`, as day one).

## Cards, stores, lanes, standing actions

All targets. Same schema as `day_one.toml`; everything additive (new ids, appended levels, raised caps, new triggers)
except where `docs/design/day-two-plan.md` names a schema change.

### Her lane (fit pass)

**What it is:** the first person who works for the camp. **What it is an instance of:** work that runs on its own
beside the player's hands, which is a lane (the rack, the smoke lane), started by a rule (a side lane's rule is a
single task, `decisions.md`, "The mix"). **What already does that:** Lanes and Standing orders. **Fits into:** Lanes
(a lane `n1`), Cards (her versions of the gathering cards on that lane), Standing orders (her task is a rule on her
lane; changing her task is editing or adding a rule, so every verb has an order). **Not** the town's mix with staff as
shares: with one person a share is always all of her, so that waits for the second arrival (Open 3).

- **Her cards:** `n1_forage`, `n1_gather`, `n1_cut`, `n1_scavenge` on lane `n1`: the same takes and makes as forage,
  gather_wood, woodcutting and scavenge at their base rate (no level speed-ups: the player's levels are theirs, so her
  work is slower than theirs by however far they've climbed), **no XP** (`decisions.md`, "You and the town"), and each
  also makes camp items at the hands' rate, so the Camp bar fills for two. They never show in Tasks: the player meets
  them as her task's options (D-83). Woodcutting's card needs the knapped edge; she has her own knife, so `n1_cut` has
  no requires.
- **Her default rule**, set by B3's outcome: "always → she forages" (`when` unlocked feature n1). She came for roots
  (H7) and forages from the moment she sits down, so she is never idle and a B3 landed while away loses nothing.
- **Her row:** under the hands strip, the same shape: who, what she is doing, its bar, and `Change` (opens the rule
  editor on her rule, the simple view: pick the task). Labelled "she" until J1, then her name.
- **No chips for her.** Her food is the standing `n1_eating` (day one's); she does not tire or get cold. Notables are
  safe (`cast.md`), and a chip on a person the player can't tend is a cost with no cure (`decisions.md`, "Every bad
  state has a cure in reach").

### Stores

| Store | Cap | Notes |
|---|---|---|
| dry_wood | 12, 24 with the woodstack | existing store, cap raised by the woodstack's upside |
| night_2 | 20 | never unlocked; filled by `night_2`, ~60 game min, as day one's `night` |
| walk | 1 | never unlocked; the walk's done mark, whoever walked (B4's gate reads it, so either answer lands the same beat) |
| walk_out | 15 | never unlocked; the walk's clock from either answer, filled by `walk_out` in 45 game min (t_walk_out) |

### Standing actions

| Id | Unlocked by | Makes / costs (per hour) |
|---|---|---|
| night_2 | t_dusk_2 (A15 + 0.25 h) | night_2 +20 |
| walk_out | either answer to O-cart | walk_out +20 |
| n1_eating | B3 (day one's) | smoked −1, roots −1 |

### Cards

| Card | Story id | Lane | Cap | Bar (s) | Takes / requires | Makes / effect | Opened by |
|---|---|---|---|---|---|---|---|
| give_stool | A15 | hands | 1 | 5 | | J1; starts the evening's clock | B3; glows (the one next step) |
| make_room | A16 | hands | 1 | 5 | requires night_2 ≥ 20 (first light) | J4: the two builds in view | t_night_2_shown (J2), so its countdown shows through the night; failed line before first light |
| build_shelter | A17 | hands (craft) | 1 | 20 | 12 damp wood (green poles), 2 stones | upside "She works a fifth faster": LaneSpeed(n1) ×1.2; opens O-cart | make_room |
| build_woodstack | A18 | hands (craft) | 1 | 20 | 10 stones, 4 dry wood | upside "Room for twice the dry wood": dry_wood cap ×2 | make_room |
| walk_ridge | A19 (Go) | hands | 1 | 360 | | walk +1 → B4 | O-cart answered Go; the answer starts it (queueable instead) |
| n1_walk_ridge | A19 (she goes) | n1 | 1 | 360 | | walk +1 → B4 | O-cart answered the other way; run by a rule set by the answer, above her task |
| n1_forage, n1_gather, n1_cut, n1_scavenge | | n1 | none | as the hands cards | as the hands cards | as the hands cards, no XP, + camp items | B3 (her task's options) |

The two builds are day one's lean-to/larder shape again, now for the town: each names only its upside; the cost is
what the other then reads. Shelter first leaves dry wood capped at 12 while the woodstack's 4 and the fire's draw both
want it; woodstack first leaves her at her slower pace and holds the story back (the offer waits on the shelter). They
pull on different stores, poles and stones, so the need is a mix switch for the player **and** a task switch for her:
the first time the player plans two pairs of hands.

The walk is 6 game minutes for either walker. Going takes the player's hands (the mix pauses while the hands walk, as
any tap); letting her go takes her lane for the same time (her task waits). Equal time, so neither answer is the
costly one (D-87).

### The first offer (fit pass)

**What it is:** a person asking the player to do something, with a yes and a no. **Instance of:** an offer.
**Already does that:** Offers and quests (`docs/systems.md`, planned): what is on offer, accepted or declined, what
declining changes. Day two builds its first piece. **Fits into:** Offers (its state in the save: open, gone, stayed),
the mix offer's row on the page (where a line with two answers already sits), Cards (each answer starts a one-off
card on a lane), Gates (B4 reads the walk store, so the gate needs no new vocabulary).

| Offer | Shown | Answers | Each answer | Expires |
|---|---|---|---|---|
| O-cart | when build_shelter completes (she has a roof: she means to stay) | **Go** / **She goes** (labels to the voice pass) | Go: walk_ridge starts on the hands, l_yes follows (the first you-said-yes line, C-promise-7). She goes: her rule "walk to the ridge" goes above her task, n1_walk_ridge runs once, her task resumes after | never: B4 waits on it, so it stays until answered (a branch pauses only itself) |

The offer's line is hers, in the narration register (she asks; the strip says so); the row carries the two answers.
It names what each answer costs in time ("about 6 min, your hands" / "about 6 min, hers"), as every card shows what it
takes. Nothing comes back either way: whoever walks brings only the news, so declining costs no progress and the yes
is never a free win.

### Order cards

- **Under the damp wood line, from B3:** "Under 5 damp wood → she cuts wood, until 11" (at_most, a rule on lane n1),
  her first rule, taught by need: the rack draws the line down and she keeps it up, and it feeds the shelter's poles.
  One card for both of D-85's moments (D-91): a full roots line cannot carry a rule of hers, since an at_least card
  taps a card that spends its store and none of hers takes roots; a full line she feeds is answered by `Change`.
  Release under the cap the loader can count on at B3 (12). Offered beside the player's own wood rules; either answers
  the line.
- **After B4:** nothing new. Her rules stand; the end card follows.

### Levels and finds

The curve appends levels 21–25 for every hands skill, each step half again the last (36 600, 54 900, 82 350, 123 500,
185 300 items), so no row tops out in day two on any route (Woodcutting stood at 19 at B3 on the measured routes).
Every level past the finds stays a tenth faster at its own work. **Day two reaches levels whose shipped pay is speed
alone three or more running** (Foraging 8–10 and on, Scavenging 18–20), which breaks "at least every third pays a
thing" (`decisions.md`, "A level is a thing") once those levels are reached: day two adds a find beside the speed-up at
the levels marked *added* (each a new trigger, so additive under the lock; the plan file has the check).

| Skill | Level | Pays |
|---|---|---|
| Foraging | 9 *added* | a stand of ashroot gone to seed by the old field wall (roots +5) |
| | 12 *added* | lichen thick on a north-facing stone (roots +4; the roast's line can mention it) |
| | 15 *added* | a warm-stream bank of soft clay (no store yet: holds the place of seam-warm clay, R1's, for day three; if no card uses clay by then, it pays roots +4 instead) |
| | 18 *added*, 21, 24 | finds of roots, sized to the curve |
| Scavenging | 18 *added* | a flagged floor under the ash (stones +5) |
| | 21, 24 | a fallen gable (damp wood +5), a kerb of dressed stone (stones +5) |
| Woodcutting | 21, 24 | a stand of straight poles (damp wood +6), a root plate torn up whole (stones +4) |
| Cooking | 7–10 | smokes faster; at 8 *new* a find: the knack of a tighter rack (smoke_catch +1 smoked a batch). From the first Take stock to B5 the rack's yield from the catch runs at 0.625 (`t_rack_lean`, `t_rack_lean_off`; day-two-numbers.md): a full store drops most of a batch, and the trim is not shown to the player |

Finds never name or hint at the ridge, the cart, wheels or anything a cart carries: those are B4's.

### The Camp

| Level | At (camp items) | ~ two-worker hours past the last | Pays |
|---|---|---|---|
| 7 | 90 000 | 5 | the wall takes 9 (lay_to_dry batch 7 → 9): a fire for two |
| 8 | 150 000, held ("?"); cap 149 999 until lifted | 8 | lifted by B4 (its outcome raises the camp cap): catch holds half again (9 → 13); the next marker shows its pay plainly, a reason to stay up |

Her lane fills the camp bar at the hands' rate, so these are two-worker hours. Day one's note that Camp 7's marker
would "read as a choice" is met instead by A16's two builds (D-86): a level that opened builds while the player was
away would break the 2 AM test (builds have to be in view unready to be queued).

## The beats

Fields as in `beats.yaml`. Facts each writer may use are the canon ids named; nothing else.

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread | Canon |
|---|---|---|---|---|---|
| B3 ★ | V1 | P0.4 (day one's) | as day one; her row comes with it | as `beats.yaml` | C-beat-76 |
| J1 | V1 | A15, giving her the stool | The player gives her the stool. It rocks under her; she wedges the short leg with a chip of stone and doesn't remark on it. She gives her name, Lucy, plainly, and then looks at the ridge a long time. | up · none · wry · none · N1, PC · opens C-promise-18, advances C-promise-8 · th-cart start | C-beat-81 |
| J2 | V2, met on return | three minutes into night 2 | The two at the fire, her on the player's side. A sound carried down from the ridge by the still air: wood dragged on stone, a long scrape, and then nothing. She hears it too and says nothing. From here on the ridge's square is gone from the art; no line says so. | down · none · dread · none · PC, N1 · advances C-promise-18 · th-cart middle | C-beat-82 |
| J3 | V2 | morning 3 (A15 + 1.25 h) | A grey morning. She is up before the player; the fire has been fed; the stool's wedge is out and it rocks again. The unwrap is what two got done in a night. | up · none · wry · time · PC, N1 · none · th-survive middle | C-beat-83 |
| J4 | V2 | A16, making room for two | One cover, two people: she slept by the fire in the open. Two builds, one choice: a shelter for her and a woodstack. Both get built; the order is the choice. | up · yes_but · warm · option · PC, N1 · none · th-survive middle | C-beat-84 |
| O-cart | V2 or V3 | her shelter built | With a roof of her own she means to stay, and asks: her people's cart is on the ridge; would the player fetch it? Either answer is fine to her. | (an offer, not a beat) advances C-promise-18 · th-cart end | C-beat-85 |
| B4 | V3 or V4 | the walk done (walk ≥ 1), whoever walked | Went: the place on the ridge where the cart stood, drag-marks off over the edge, wolf prints all round; back at the fire she takes the news without a word. She went: she walks back in, sits, says nothing; the player reads it off her. The first "you said yes" line only on Go, right after the answer. | as `beats.yaml` (down · no_and · grim · time · N1, PC · opens C-promise-7) and pays C-promise-18 (Open 2) | C-beat-4, C-beat-85 |

**The flat check, authored order** (by hand; `flatcheck.py` checks only `day_one:` today, plan file item 9): turns B3
up, J1 up, J2 down, J3 up, J4 up, B4 down (never three the same); one yes_but (J4) and B4 the day's no_and; registers
warm, wry, dread, wry, warm, grim (never four the same); costs stores, none, none, time, option, time (four kinds); the
near promise opened V1, advanced V2 and V3, paid V4. Clean on the authored order; the route check comes with the
simulator.

**Mechanically, B4:** the walk store's first item plays B4's lines (the Go set or the She-went set, chosen by the
answer, never by the text), lifts Camp 8 by raising the camp cap, moves the aim on, and its feature carries day two's
end card. Nothing else changes: no store taken, nothing added. Not in this drop: the second arrival, the town's mix
with shares, the journal's wolf entry, B5.

## Away from the screen

- **Every planned moment plays in full on return:** J2 and J3 nearly always land while the player is away, the offer
  often, B4 when the walk outlasts the visit. Each is revealed in order, one at a time, with its scene.
- **Her work is time away doing what time present does.** Her lane runs whether or not anyone watches; the unwrap
  shows what she brought in, never what she might have.
- **The 2 AM test:** her default rule means the babysitter has no instant to exploit at B3; the builds are in view
  unready (A16) before either can be afforded, so they can be queued; the offer's two answers cost the same time and
  bring nothing back, so answering at 03:00 gains nothing over answering at breakfast. A babysitter who changes her task
  the instant B3 lands is ahead only by the player's own choice of task, which a whenever player sets by rule on the
  next return; the simulator checks the gap is within the ledger's tolerance on every route (plan file, item 10).
- **Rebased saves:** a save already past B3 when day two ships gets her row and default rule at the rebase instant
  (forward only: she doesn't owe the hours before) and A15 on its cards. At most two unlocks, the story in order.

## Line moments, and the states each can fire in

Written by blind proposers scored on `rubric.md`, picked by the lead, then a voice pass; the brief will be
`day-two-lines-brief.md`, after the simulator's routes exist. **The state lists below are the design's expectation;
the shipped lists are generated** by `python -m tests.dayone.report --lines` once `day_two.toml` exists, and replace
these. Each line must be true in every state on its list.

| Id | Fires when | Expected states |
|---|---|---|
| l_her_row | her row first shows | right after B3's lines and day one's re-tune; she is already foraging; the stool not yet given |
| l_stool_1, l_stool_2, l_name (J1) | give_stool | V1, or the return that revealed B3; day time; she has eaten; the stool exists on every route (both opening crafts built) |
| l_her_first | her lane's first completion | within a minute of B3, present or on return; before or after J1; any of her tasks if the player changed it at once, so the line names no store |
| l_dusk_2 | t_dusk_2 | 15 game min after A15; present for a stayer, on return for most |
| l_night_2a, l_night_2b (J2) | night_2's first item | at night; the two at the fire; the shelter not built (A16 not yet tapped on any route) |
| l_morning_3 (J3) | t_morning_3 | on return on nearly every route; her night's work in; the stool rocking again |
| l_make_room_fail | make_room before first light | night only; J2 played |
| l_room_1, l_room_2 (J4) | make_room | day 3; nothing built since day one's end |
| l_shelter, l_woodstack | each build | within minutes of A16 or by the queue while away; each with the other built or not (order variants) |
| l_shelter_fail, l_woodstack_fail | tapped unready | damp wood under 12 or stones under 2; stones under 10 or dry wood under 4; day 3 |
| l_her_rule | her first rule taken | roots full, her foraging; any visit from V1 on |
| l_offer_1, l_offer_2 | O-cart shown | her shelter just built, present or on return; the woodstack built or not |
| l_yes | answered Go | the first "you said yes" line; only ever after Go |
| l_walk_go, l_she_goes | each answer's walk starts | the player at the gap / her leaving through it |
| l_walk_out, l_walk_out_2, l_walk_out_3, l_walk_out_4 | t_walk_out to t_walk_out_4: 45 game min after either answer, then an hour apart to 3.75 h (either walk takes at least 4 h, so every hourly return during it has a line since the last; D-104) | the walk under way, on either answer; on return for nearly every route (a return during the walk), present for a stayer; B4 not yet landed; both builds done or the woodstack still to build |
| l_b4_1 to l_b4_4 | the walk done, Go | present if the player waited the 6 min, else on return; she is at the camp |
| l_b4_h1 to l_b4_h3 | the walk done, she went | present or on return; the player at the camp |
| l_camp_7 | Camp 7 | after J1, before or after the builds |
| l_camp_8 | Camp 8 (lifted by B4) | with B4 or after it |
| find lines | each added find | by the mix, any visit; never naming the ridge or the cart |

**Must-nots for the brief:** never count her people or say how many she lost ("the last of five" is canon only,
`cast.md`); never name the wolves before B4 (J2 is a sound, not an animal); never say the square is gone; the you-said-
yes line only after Go, never on the other answer and never judging either; her lines are what she does, in active
voice (people act); no line says she is grateful.

**Labels and upsides** go to the voice pass: her row's label, `Change`, the two answers, the walk's card, "She works a
fifth faster", "Room for twice the dry wood", the aims below.

### Stated aims

Each is keyed to the unlock that starts it (`aims.py`); the next one's start ends it. Intents, not lines: the voice pass
writes them.

| Aim | Starts at | Intent |
|---|---|---|
| aim_two (day one's) | feature n1 | lay in enough for both of you (unchanged) |
| aim_night_2 | feature night_2 | get the two of you through the night |
| aim_room | feature morning_3 | give her a place of her own here |
| aim_cart | O-cart shown | bring back what she left up there |
| aim_after | feature cart_news (B4) | a goal for the evening that points at what comes next: keep the camp worth keeping, now that something knows where it is |

## Art

Tools: `tools/scene` conventions. Composites checked at 390×844 and 3840×2160.

- **Grades:** the dusk and night grades again for evening and night 2 (`until="feature:morning_3"` on night-only
  layers); day 3 is the normal grade.
- **World layers (cool):** ridge_shape gains a state without the square (feature:night_2_sound, J2); nothing else on
  the ridge changes.
- **Player-made (warm):** her shelter (small, lower than the lean-to, beside it, its back to the wall), the woodstack
  (on a stone footing by the wall).
- **N1 poses:** on the stool, rocking (A15 hit frame); foraging at the scrub's edge and walking back with an armful
  (running:n1_forage); cutting (running:n1_cut); carrying (gather, scavenge); asleep by the fire in the open (night 2,
  before the shelter), then under her shelter on later nights; leaving through the gap and coming back (n1_walk_ridge).
- **The player:** standing at the gap facing out, then gone from the scene while walk_ridge runs, then back.
- **Stages:** 17_her_row, 18_stool, 19_night_two, 20_morning_three, 21_room_for_two, 22_offer, 23_walk, 24_news.

## Where canon shaped the design

- **She asks for the cart once she has a roof.** C-cast-4: she wants the fire still lit tomorrow, so she stays where
  it is; a shelter of her own is her deciding to stay, and only then is her people's cart worth asking for.
- **The cart goes in the second night, by sound.** The Still carries sound (C-season-2), H1's howl came the same way,
  and B4 says the cart was dragged off. A dragging sound is dread without naming an animal, and the art's missing
  square rewards whoever watches the ridge.
- **The stool, not the ground.** The stool always wobbles (B2) and nobody ever fixes it (N7's arc), so her wedge that
  doesn't hold is the motif carried, and B5 keeps the warm ground.
- **Either answer lands B4.** Declining costs nothing (`decisions.md`, "Tone"), and the you-said-yes line follows only a
  yes (C-beat-4, C-motif-4). So "she goes herself" is the other answer, the same time spent and the same facts found.
- **No chips, no XP for her.** Notables are safe (`cast.md`); the player levels personal skills and the town works in
  parallel (`decisions.md`, "You and the town").
- **She forages first.** At H7 she took roots: roots were what she lacked.
- **Her name at the stool.** Canon fixes the name, not the moment; given in return for a kindness the player chose, it
  keeps the yes thread for B4.
- **Nothing comes back from the ridge.** A find from the walk would make Go better than the other answer.

## Open (content side)

Decided (orchestrator, 2026-10-24, as the lead): 1, re-gate B5 and B6 on day-three steps, values
from the simulator; 2, B4's spine entry takes `{project: A19}` and pays C-promise-18 when `day_two.toml` lands; 3, the
town's mix with shares at the second arrival; 4, the answer order built now, shown in the Rules tab from the second
offer kind; 5, night 2 has the countdown only. The rest stay open for day three.

`flatcheck.py --days day_two` (2026-10-24) flags `week_net_up` on W1 (net +2) once day two's beats join week 1; the
other flags it raises all follow from Open 2 and clear when B4 pays C-promise-18. W1's net is a real pacing finding for
the beats' turns, to settle before `day_two.toml`'s lines are written. Levels 21–25 and their 15 pays are drafted on
branch `day-two-small` (commit ebe6c27, thresholds by ×1.5 from day one's last step) and held until day two's content
ships, so the live game gains no levels before its numbers are simulated.

1. **B5's and B6's gates are already met when day one ends.** B5 gates on Foraging 5 and B6 on Scavenging 8 (written
   before day one's curve), and day one reaches Foraging 7 and Scavenging 17 on the measured routes, so as written B4,
   B5 and B6 would land in one moment at day two's end (and B6 opens Arcana). Recommendation: re-gate both on day-three
   steps, keeping a level beside each at a value the routes reach in day three (simulator to set). Canon change, so the
   lead's. Spoiler-free for the owner if needed: "two later story moments are gated on skill levels the first day already
   passes; fine to re-gate them on steps instead?"
2. **B4's spine entry:** its gate is `{beat: B3}`; day two lands it at the walk (`{project: A19}`, i.e. walk ≥ 1), and it
   pays C-promise-18. The `day_two:` list carries both; the spine entry should gain them when the lead confirms.
3. **The town's mix with shares waits for a second person.** Day two runs her as a lane with rules (D-83), which is
   cheaper and is what one person is. When the second arrives, either each person stays a lane (the Rules tab grows a
   section per person) or the town gets its mix with people as shares (`docs/systems.md`, Mixes). Recommendation: the
   mix, at the second arrival, so the town layer is taught on a real split.
4. **Every verb has an order:** answering an offer needs one for the simulator ("answer offers of this kind: go / let
   them go"). Recommendation: build it in the engine now, show it in the Rules tab with the second offer kind, where
   it first saves a player a trip back. The lead may prefer it visible now.
5. **The night-2 wait card.** Day one's dusk card says once, out of fiction, that night is a real-time wait. Night 2
   gets none; A16's countdown says when first light comes. The owner, spoiler-free: "the second night: does it need the
   'this is a real-time wait' card again, or is a countdown on the next card enough?" Recommendation: countdown only.
6. **Day one's end card** says day two is still being written. With day two shipped it should lose that line, and day
   two's end card takes the out-of-fiction "this is as far as it goes for now" (`research/waits-and-ends.md`).
7. **Arrivals.** B7 needs three arrivals by about day 6; day two brings none. Day three must bring the People row's
   arrivals, with "food to spare" as the draw (`decisions.md`, "Nothing appears").
8. **Her pace.** Her cards run at base rate, so the gap to the player's levelled rate is the "competence grows" feel. If
   the simulator finds her negligible next to a levelled mix, raise her base, never give her levels (day three's
   question: do townsfolk ever level?).
9. **Clay at Foraging 15** holds a place for a day-three use; if none comes, it pays roots.
</content>
</invoke>
