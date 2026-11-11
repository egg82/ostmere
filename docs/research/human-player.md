# Human-paced player: sourced numbers for the pacing simulator

Numbers a human-paced player model can use to flag stretches where a first-time player would likely drift away,
each with its source. Part B (separate) is a proposal for how the simulator uses them.

Part A, the evidence, is held in the `game-design` skill, `references/playtesting.md`, "Numbers for modelling a
human-paced player": sources, labels, and what is unverified. Below are only the figures Part B and
`app/tests/dayone/human_thresholds.toml` use, and what the skill does not hold. The headline gap is there too: no
source gives "N minutes without a meaningful event in an idle game, X% leave", so a drift threshold is a design choice
anchored to a figure and labelled as such. Every session and retention benchmark is from mobile or store-wide games
with push notifications, daily rewards and offline caps, which Ostmere bans ("Fun, but never vying for attention"), so
they say when a human might show up, never what to target.

---

## Part A. Evidence

### 1. Reading speed and decision latency

- Silent reading: 238 wpm for non-fiction (175-300), 260 for fiction (Brysbaert 2019). BBC subtitle guidance gives a
  minimum of about 0.3 s per word for text read beside a picture.
- Carver's reading "gears" as reported in Brysbaert 2019: 450 wpm skimming, 650 scanning, older estimates (medium).
  The skill does not hold these.
- Action time: M + P + 2B = 2.65 s for a practised desktop click (keystroke-level model, Card, Moran & Newell 1980);
  3.73 s for a first-time click on an unfamiliar web UI, response time included (Sauro 2009).
- No source for choosing 1 of N (a Hick slope) or for a touch equivalent of the KLM.

### 2. Sessions, visit cadence, retention

- Mobile idle games: 8 min a session, 5.3 sessions a day, 18% DAU/MAU; top quartile 5.0 sessions of 6 min
  (GameAnalytics blog, sample not stated). PC, all genres, 2025: session median about 18 min, 1.65-1.70 sessions a day
  (GameAnalytics 2026 report, read not stated, so unverified).
- First session: mean 9 min; games above it had 31% D1 against 20% below, correlational and possibly caused by churn
  (deltaDNA, 275 mobile F2P games). The same source says most games lose 20% of installs within 2 minutes; the skill
  does not hold this figure, and a browser visitor costs nothing to leave.

### 3. Time without a meaningful event

- Nielsen's "10 seconds is about the limit for keeping the user's attention" is unverified: the skill's Nielsen row
  covers only the 0.1 s limit. It is about waiting on a system, which an idle stretch on screen is.
- Continuous attention to a phone broke into 4-8 s bursts in the mobile situations (8-16 s in the lab and cafe), with
  up to 8 glances away in one page load (Oulasvirta et al., CHI 2005; 28 adults, phone in transit, so desktop players
  hold longer). The paper's text does not hold a 4.8-7.6 s switch-back figure.
- Practitioner targets (first upgrade under 60 s, first automation under 3 min, first prestige 10-15 min) are
  individual developers' opinion with no data: `pacing-math-notes.txt`, not re-verified.

### 4. Bots versus humans

A strong policy is a poor stand-in for human choices: a CNN trained on human Candy Crush moves predicted the human
move 47-48% of the time, and CNNs trained on human data were almost 50% better in validation accuracy than ones
trained on MCTS play (Gudmundsson et al. 2018). Per-level churn tracks difficulty weakly (Spearman r = -0.144), and a
population model with per-player skill, persistence and boredom, fitted to 95,266 players' real data, predicted churn
better than AI pass rates (Roohi et al. 2020). The method transfers, the fitted values do not.

---

## Part B. Proposal: how the simulator would use these (design, not evidence)

Everything in this part is a proposal. Where a threshold is a judgement anchored to a source, it says so; the
simulator's output should carry the same label, so a flag never reads as a measured churn prediction
(`no-fabricated-certainty`).

### B1. The human-paced player: time cost per action

Make the simulator's player spend wall-clock time the way a person does, on the engine clock:

- **Reading:** each line shown costs `words / rate × 60` s. Three readers: slow 175 wpm (Brysbaert lower range),
  typical 238 wpm (non-fiction mean; story lines could use 260), skimmer 450 wpm (Carver's skimming gear; a skimmer
  is assumed to miss content, so it should not count lines it skimmed as "understood" for any check that cares).
- **Acting:** each deliberate click on a card or control costs 3.73 s for a first-time player (Sauro's empirical
  web click, including response) and M + P + 2B = 2.65 s for a practised one (KLM). A choice between several cards
  gets an extra M per option looked at as a placeholder: there is no sourced Hick slope, so label it.
- **Touch players:** no sourced KLM equivalent; reuse the desktop numbers and say so.

This gives "seconds of play the content asks for" per stretch, which the engine-only optimizer never pays.

### B2. Visit schedule

Two first-day presence profiles, both from GameAnalytics, both labelled as borrowed from other platforms:

- **Checker:** ~5.3 visits/day of ~8 min (mobile idle average); top-quartile variant 5.0 × 6 min.
- **Sitter:** ~1.7 visits/day of ~18 min (PC median).
- **First session:** 9 min (deltaDNA mean) as the default length, with 2 min as the early-leaver case.

Return intervals have no sourced distribution; spread visits across a waking day by a seeded roll and keep the rates
as data the tuning pass can change (`stateless-calls-cant-keep-a-rate` applies to the sim too: rates in code, seeded).

### B3. Flags

| Flag | Fires when | Threshold anchored to | Strength |
|---|---|---|---|
| **Dead air (in session)** | while the player is present, a stretch longer than **10 s** with nothing new on screen and nothing affordable or choosable | Nielsen's 10 s attention limit (unverified, see A3); a phone-profile variant at **8 s** (the upper end of Oulasvirta's 4-8 s bursts) | medium — predicts "looks away", not "quits" |
| **Text outruns the reader** | lines arrive faster than the typical reader (238 wpm) can read them, or a ceremony moves on before its line's read time | Brysbaert; BBC 0.3 s/word as the floor for any line's display time | strong |
| **Slow first hook** | the first player-caused visible result lands after more than **2 min** of the human player's time (reading and clicks included) | deltaDNA's 20% loss inside 2 min | medium; the 2 min is a ceiling, the design should land far under it |
| **Short first session** | the opening runs out of things to read, choose or watch before **9 min** | deltaDNA: >9 min first sessions associated with 31% vs 20% D1, correlational | medium |
| **Empty return** | a visit in either B2 profile opens to nothing to unwrap and no visible step toward a goal | the decision "Leaving and coming back always pays"; the cadence is from B2 | design rule, cadence medium |
| **Optimizer gap** | the human-paced player's day-1 position trails the engine optimizer's by more than an agreed margin | Gudmundsson/Roohi only show the gap is large and that a policy is a poor human proxy; **no source for a margin**, choose one and label it | weak |

Two things the sources argue against:

- **Don't let the optimal bot stand in for the human.** Even a model trained on human moves matched them only about
  half the time in Candy Crush; an engine-optimal policy will be further off. Keep the human-paced player separate
  from the existing sharp/typical/neglectful route players.
- **Don't add a churn probability yet.** Roohi's skill/persistence/boredom population model is the right shape for
  one, but its parameters were fitted to 95,266 players' real churn; Ashfall has none. Flags stay binary and
  labelled until there is play data to fit against.
