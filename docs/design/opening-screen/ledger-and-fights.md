## Ledger and rules

The ledger arrives with the fire (the `ledger` feature unlock); until then nothing of it is drawn. It arrives with only
the lines that ask something: red, starved, or carrying an offer. Any other line joins the first time it is falling
(not only from the hands' passing tap), full while something feeds it, or covered by a rule, taking its turn as it
arrives. Once drawn a line stays, remembered for the account, so each line moves the layout once; with nothing
remembered (another account), the lines that ask something still show.

The ledger is grouped: the player's stores under Yours, then the threats at them under Threats, each label drawn
while its group has a row (on a phone, the lines moved above the cards take no label). A line is a row of name, rate
and stock, with its time under the stock.

Lines are store rates per hour, with when a store empties or fills; the "full in" time is the view's forecast
(api `CONTRACT.txt`, "Forecast"), so no time is drawn when a rule will take from the store, or stop it, first.
A **falling line with no rule covering it is red**, with its answer right beside it: an **inline rule offer** under
the line, the card's condition and task (`Under 2 dry wood, until 6 → Lay to dry`), pre-filled, and `Show me` beside
the sentence, while the first rule's lesson may start. After it, no row: the red line is the signal and carries the hint
dot (below), and the player writes the rule in the Rules tab. Nothing is ever built from the line. On a desktop the ledger is a grid and the offer spans the whole row under its line, the line's neighbour
keeping the cell beside it. It is shown unprompted: in the preview, no player found the order card it kept out of
sight, and every player who saw the inline offer set it. On the hands a rule always runs a mix, so the lesson's editor saves
a mix of that task alone (named by the task) with the rule; a task on another lane
(the rack) becomes a rule of its own. Once set, the offer goes and the line turns white. Player text says rule and task,
never order or card.

- **Covered** is something keeping the store fed, or a rule of the player's spending it as the rule says: the rule is
  on, it is an `n or more` rule on that store, and a task it runs is what takes from the store (`4 or more catch, until
  under 1 → Smoke` draws the catch down and the line stays white). Red is for a store falling with nothing covering it.
- **Nothing stands under a line a rule watches.** The line carries a small rule mark (the Rules tab's icon, dim), and a
  tap anywhere on it opens that rule in the Rules tab: the rule spending the store, else the first rule on it. A rule
  set while the line is still red changes nothing under it either; the mark is the way to it.
- **Starved** (the store is at 0 and something waits on it) reads as a problem too, covered or not.
- **Full** (`damp wood 12/12 · full`) is not an alarm: the ordinary line colour, `full` in
  the time's dim ink (never green, which would call a loss a gain; never an alarm hue or a pulse), no `Edit mix`. The rate beside it is what spills,
  and the numbers show the loss: a cap rule is the player's to write (the cap rule's lesson), and skipping it costs
  only that overflow.
- **A rising line's rule** (a card whose condition is `n or more` on a store a task takes, a side lane's or a build on
  the hands: `4 or more catch → Smoke`) is marked on the line (a hint dot) once it is full or rising, calm rather than red, and
  stays until a rule is set.
- **A rule re-tuned:** a later card on a store whose rule is already set at other levels (a new need asks more of it) changes nothing:
  the player edits the rule in the Rules tab, and its goal rows show what the levels buy.
- **Falling with no order card to answer it** (a drain the mix or the rack is causing) names what draws on it most,
  with `Edit mix` beside it. A tap of the hands draining a store for a moment gets neither: it ends by itself.
- While a mix share is being dragged, the lines that card feeds or draws on light up.

## Fights

Fight parts show once the `combat` feature is unlocked (api `CONTRACT.txt`, "FIGHTS"); every number is the engine's, served.

- **A fight card** draws under its tap, never inside it: the odds as the smallest exact "1 in 5 lost" (a percentage when
  no whole pair up to 20 is exact), the two strengths beside it (`yours 12, theirs 9`), and what one lost fight costs or
  adds. Each strength is a button of at least 28 px that opens its entries under it, the base first, then sums as
  signed percentages, then factors as multiples; a second tap, or the other strength, closes it. No hover.
- **A standing fight** (a threat that runs on its own) is a row in the ledger's Threats group under the stores' lines,
  calm and never red: its name, the same odds and strengths, and `fought, lost` as served.
- **The arrival queue** writes each window of fights since the last view as the chronicle's Fights entries, never the strip: k entries
  of which exactly j read as lost, which ones picked by a shuffle-bag draw seeded by save, runner and the fought count
  the window starts at (`app/client/src/game/fights.ts`), so the same window reads the same on every device. Past three
  in one window, one summary line of the exact counts. The draw changes no number.
- A threat's strength is never worded as answering what the player built: it rises with the region's clock alone.

