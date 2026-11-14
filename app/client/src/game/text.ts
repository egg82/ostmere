// Every visible word comes from Content's text table (CONTRACT.txt). The page names keys, never text: a key
// the content lacks renders as nothing and is reported once on the console, so the gap is found, not papered over.
import type { Content } from "../api/types";
import { ASK_KEYS } from "./askkeys";
import { GOAL_ROW_KEYS } from "./goalkeys";
import { LESSON_KEYS } from "./lessonkeys";
import { CHRONICLE_KEYS } from "./chronkeys";
import { PRESTIGE_KEYS } from "./prestigekeys";
import { REMINDER_KEYS } from "./reminderkeys";
import { RULE_KEYS } from "./rulekeys";

/** Keys the page itself asks for: units, templates, the controls. Line, label and card keys come from the content. */
export const UI = {
  durationD: "ui.duration.d", // "{days} …": DAYS_FROM_H hours and over, on the day exactly
  durationDH: "ui.duration.dh", // "{days} … {h} …": DAYS_FROM_H hours and over
  durationH: "ui.duration.h", // "{h} …", on the hour exactly
  durationHM: "ui.duration.hm", // "{h} … {m} …"
  durationMS: "ui.duration.ms", // "{m} … {s} …"
  durationS: "ui.duration.s", // "{s} …"
  perMinute: "ui.rate.per_minute", // "{n}/min"
  amount: "ui.store.amount", // "{n} of {cap}"
  empties: "ui.ledger.empties", // "{d}" until a falling store is empty
  fills: "ui.ledger.fills", // "{d}" until a rising store is full
  level: "ui.skill.level", // "{n}"
  skillNextIn: "ui.skill.next_in", // "{pays} {d}": what the next level pays, and the forecast's time to it
  skillNone: "ui.skill.none", // a skill row with nothing ahead in this content
  nextUnnamed: "ui.next.unnamed", // a Camp marker whose pays names something the player has not met
  goalIn: "ui.goal.in", // "{d}": the time left on the wait line (ui/waitline.ts)
  goalWhile: "ui.goal.while", // "{store}": the wait line's clock runs while this store holds some
  goalPaused: "ui.goal.paused", // "{store}": the wait line's clock stopped on this dry store
  needs: "ui.card.needs", // "{store} {have}/{n}": a card's need
  needsSpent: "ui.card.needs_spent", // "{store} {have}/{n}": a card's need on a store nothing will bring again
  needsSkill: "ui.card.needs_skill", // "{skill} level {have}/{n}": a card held back by a skill level
  needsStep: "ui.card.needs_step", // "{card} {have}/{n}": a card held back by another card's completions
  ledgerHeading: "ui.heading.ledger",
  ledgerYours: "ui.ledger.yours", // the ledger's group of the player's own stores
  ledgerThreats: "ui.ledger.threats", // the ledger's group of threats at the stores
  craftHeading: "ui.heading.craft",
  ordersHeading: "ui.heading.orders",
  mixesHeading: "ui.heading.mixes",
  runs: "ui.mix.runs", // "{d}"
  runsIndefinitely: "ui.mix.runs_indefinitely",
  defaultMix: "ui.mix.default", // the id of the first mix, saved from the first-mix offer
  orderAdd: "ui.order.add",
  orderChange: "ui.order.change",
  orderRemove: "ui.order.remove",
  ...RULE_KEYS,
  handsByRule: "ui.hands.by_rule", // "{store}{n}": the strip while a "below" rule with no band runs
  handsUntilUp: "ui.hands.until_up", // "{store}{m}": the strip while a "below" rule runs
  handsUntilDown: "ui.hands.until_down", // "{store}{m}": the strip while a "reaches" rule runs
  handsWhileChip: "ui.hands.while_chip", // "{chip}": the strip while a rule worded as a chip runs
  close: "ui.close",
  feedbackOpen: "ui.feedback.open",
  feedbackPrompt: "ui.feedback.prompt", // the field's placeholder and accessible name
  feedbackNote: "ui.feedback.note", // what is sent along
  feedbackSend: "ui.feedback.send",
  feedbackCancel: "ui.feedback.cancel",
  feedbackThanks: "ui.feedback.thanks",
  feedbackLater: "ui.feedback.later", // not kept: too many just now, or no answer
  tabCards: "ui.tab.cards",
  tabCompleted: "ui.tab.completed",
  tabTown: "ui.tab.town",   // a phone's bottom bar: the ledger and skills
  tabBook: "ui.tab.book",   // a phone's bottom bar: the chronicle's sheet, with Done beside it
  bookDone: "ui.book.done",   // the Book's page of what is finished (a phone's; the Completed tab elsewhere)
  handsIdle: "ui.hands.idle",
  laneIdle: "ui.lane.idle",   // a lane row while its lane is free
  laneChange: "ui.lane.change",   // a lane row's way to the rule that sets its task
  ruleTownAlways: "ui.rule.town_always",   // "{mix}": the town's always rule
  ruleAlways: "ui.rule.always",   // "{card}": a lane's always rule
  ruleAnswer: "ui.rule.answer",   // "{answer}": what a rule or queue entry that answers an offer does
  ruleAnswerNext: "ui.rule.answer_next",   // the answer rule builder's line over its role buttons
  ruleAnswered: "ui.rule.answered",   // "{answer}": the builder's word of the answer its offer was given
  ruleAnswers: "ui.rule.answers",   // the Rules tab's heading over the rules that answer offers
  both: "ui.mix.both",
  ...GOAL_ROW_KEYS,
  ...LESSON_KEYS,
  ...CHRONICLE_KEYS,
  ...ASK_KEYS,
  ...PRESTIGE_KEYS,
  ...REMINDER_KEYS,
  townTitle: "ui.town.title",   // the camp's shown name: the town mix's heading and label, one home
  townChange: "ui.town.change",   // the strip's way into the town's mix
  townIdle: "ui.town.idle",   // "{person}": a person's unshared remainder
  edit: "ui.mix.edit",
  editMix: "ui.mix.edit_mix",
  save: "ui.mix.save",
  saveNew: "ui.mix.save_new",
  newMix: "ui.mix.new",
  mixFull: "ui.mix.full", // in the place of New mix once the save holds Content.limits.max_mixes
  runMix: "ui.mix.run", // the Mixes list: tapping this row runs the mix
  mixRunning: "ui.mix.running", // the Mixes list: the mix running now, when no time to state
  name: "ui.mix.name",
  add: "ui.mix.add",
  perMinuteHead: "ui.mix.per_minute",
  now: "ui.mix.now",
  after: "ui.mix.after",
  ifRun: "ui.mix.if_run", // the totals' second column for a mix that Save does not run
  yielded: "ui.mix.yielded",
  spent: "ui.mix.spent", // "{store}": a card of the mix is stopped on a store nothing can make again
  runningNow: "ui.mix.running_now", // the label of the split the mix runs now, while a card of it is stopped
  gainFrom: "ui.mix.from", // "{pct}{card}": a part of the split that runs now gained from a stopped card
  waiting: "ui.mix.waiting", // "{card}": a stopped card's part of the split that runs now
  stopped: "ui.mix.stopped", // "{card}": the strip's note on a greyed mix, naming the card in it that is done
  deleteMix: "ui.mix.delete",
  deleteAsk: "ui.mix.delete_ask",
  yes: "ui.yes",
  no: "ui.no",
  namedByOrder: "ui.mix.named_by_order",
  usedBy: "ui.mix.used_by", // "{n}": the Mixes list's note on a mix several rules run
  usedByOne: "ui.mix.used_by_one",
  nested: "ui.mix.nested",
  cardCount: "ui.card.count", // "{n}/{cap}"
  retired: "ui.card.retired",
  full: "ui.ledger.full",
  campPays: "ui.camp.pays", // "{level} {pays}": the next Camp level and its pays words, their own {from} and {to} filled
  starved: "ui.ledger.starved",
  unfed: "ui.ledger.unfed", // "{pct}": a dry store that only feeds a bonus (StoreInfo.bonus_bp), the bonus it holds back
  queueWhenReady: "ui.queue.when_ready", // a step's button that lines up its tap for when it turns ready
  queueQueued: "ui.queue.queued", // the same button once the tap is in the queue
  queueRunning: "ui.queue.running", // a Next entry whose tap a lane already runs, in Remove's place
  queueHeading: "ui.queue.heading", // the Rules tab's list of what the queue taps next
  queuePlan: "ui.queue.plan", // Next's "+ Plan": a stint written from the list (ui/stintplan.ts)
  queueFull: "ui.queue.full", // the When ready button's place once the queue holds Content.limits.max_queue
  handsNext: "ui.hands.next", // "{card}": the strip's note of the queue's head
  devicesOpen: "ui.devices.open", // the panel foot's way to the "Another device" sheet
  devicesHeading: "ui.devices.heading",
  codeLead: "ui.devices.code_lead",
  codeNote: "ui.devices.code_note", // "{d}": how long the code still works
  codeGone: "ui.devices.code_gone",
  codeNew: "ui.devices.code_new",
  wordsHeading: "ui.devices.words_heading",
  wordsLead: "ui.devices.words_lead",
  wordsMake: "ui.devices.words_make",
  wordsRemake: "ui.devices.words_remake",
  wordsReplaceAsk: "ui.devices.words_replace_ask",
  wordsNote: "ui.devices.words_note",
  wordsSave: "ui.devices.words_save",
  wordsCopy: "ui.devices.words_copy",
  wordsCopied: "ui.devices.words_copied",
  wordsCopyFailed: "ui.devices.words_copy_failed",
  joinHeading: "ui.devices.join_heading",
  joinLead: "ui.devices.join_lead",
  joinCode: "ui.devices.join_code", // the code box's label
  joinWords: "ui.devices.join_words", // the recovery words box's label
  join: "ui.devices.join",
  joinNone: "ui.devices.join_none", // "{minutes}": how long a code works (Content.transfer_code_s)
  joinLimited: "ui.devices.join_limited",
  joinFull: "ui.devices.join_full", // "{max}": MergeSummary.max_saves; both devices' games together pass it
  mergeAsk: "ui.devices.merge_ask", // this device has games of its own: move them into the other account?
  mergeWords: "ui.devices.merge_words", // added to the question when both accounts have recovery words
  merge: "ui.devices.merge", // the ask's primary answer: move the games
  keep: "ui.devices.keep", // the ask's other answer: join and leave the games on the old account
  mergeCancel: "ui.devices.merge_cancel", // the ask's no
  keptHeading: "ui.devices.kept_heading", // after a join that kept the games
  keptNew: "ui.devices.kept_new", // the old account's new words are shown below
  keptHad: "ui.devices.kept_had", // it had words already: they are what brings the games back
  keptDone: "ui.devices.kept_done", // reload into the other account
  devicesAway: "ui.devices.away", // the server did not answer
  listHeading: "ui.devices.list_heading",
  listLead: "ui.devices.list_lead",
  listThis: "ui.devices.list_this", // the row of the browser asking
  listSeen: "ui.devices.list_seen", // "{seen}": Device.last_seen_at as a date
  listRemove: "ui.devices.list_remove",
  listRemoveAsk: "ui.devices.list_remove_ask", // asked only before this browser is signed out
  listRemoveYes: "ui.devices.list_remove_yes",
  listRemoveNo: "ui.devices.list_remove_no",
  gamesOpen: "ui.games.open", // the panel foot's way to the Games sheet
  gamesHeading: "ui.games.heading",
  gameName: "ui.games.name", // "{number}": SaveInfo.number
  gameUnnumbered: "ui.games.unnumbered", // a save with no number yet
  gameCamp: "ui.games.camp", // "{level}": SaveInfo.camp_level
  gameDates: "ui.games.dates", // "{started}", "{played}": dates
  gamePlaying: "ui.games.playing", // the game this page plays
  gameSwitch: "ui.games.switch",
  gameDelete: "ui.games.delete",
  gameDeleteAsk: "ui.games.delete_ask", // "{days}": Games.kept_days
  gameStartOver: "ui.games.start_over",
  gameStartOverAsk: "ui.games.start_over_ask", // "{days}": Games.kept_days
  gameCancel: "ui.games.cancel",
  gameNew: "ui.games.new",
  gamesFull: "ui.games.full", // "{max}": Games.max_saves
  gamesLimited: "ui.games.limited",
  gamesDeleted: "ui.games.deleted_heading",
  gameKept: "ui.games.kept", // "{until}": DeletedSave.purge_at as a date
  gameRestore: "ui.games.restore",
  gameStraight: "ui.games.straight", // the per-device choice to skip the front page (app/straight.ts)
  gameSkipLessons: "ui.games.skip_lessons", // the account's choice to turn lessons off in every game (AccountSettings.lessons)
  frontContinue: "ui.front.continue", // the front page's button for a browser with games
  frontBegin: "ui.front.begin", // the front page's button on a first visit, and while New game is selected
  frontFirst: "ui.front.first", // the front page's line under the title on a first visit
  gamesPlayed: "ui.games.played", // "Last played {when}": {when} is one of the ui.time.* words
  timeNow: "ui.time.now",
  timeMinutes: "ui.time.minutes", // "{n} minutes ago"
  timeHour: "ui.time.hour",
  timeHours: "ui.time.hours", // "{n} hours ago"
  timeYesterday: "ui.time.yesterday",
  timeDays: "ui.time.days", // "{n} days ago"
  frameKept: "ui.frame.kept_out", // this browser keeps no game inside the page that frames it
  frameOpen: "ui.frame.open", // the link that plays it in its own tab
  fightOdds: "ui.fight.odds", // "{lost}{of}": a fight's odds as a whole pair
  fightOddsPct: "ui.fight.odds_pct", // "{pct}": the odds when no small pair is exact
  fightOddsUnknown: "ui.fight.odds_unknown", // a fight not yet fought: its odds are not known
  fightThreatUnknown: "ui.fight.threat_unknown", // the threat's strength in the vs words, before the first fight
  fightVs: "ui.fight.vs", // "{side_name}{power}{threat_name}{threat}": the two strengths, each a tap to its entries, each named
  fightOnLoss: "ui.fight.on_loss", // "{costs}": what one lost fight costs, or adds, as a list
  fightBase: "ui.fight.base", // a strength's base row
  fightTally: "ui.fight.tally", // "{fought}{lost}": a standing fight's counts
  fightSince: "ui.fight.since", // "{fought}{won}{lost}{runner}": a window past three fights, in the arrival queue
  fightWon: "ui.fight.won", // "{runner}": one fight in the arrival queue
  fightLost: "ui.fight.lost", // "{runner}"
  catchingUp: "ui.catching_up", // "{percent}": how far through the time away the server has caught up
} as const;

export type Slots = Record<string, string>;

/** The text table with every person's name slot and each find's `{found}` slot filled (CONTRACT.txt, "Text and
 * numbers", {<lane>}, {found}): the lane's name_key text, lowercased in a line as the lines' voice writes it; the
 * amount a find found, in whole items. Any other slot is left for fill(). */
function named(content: Content): Map<string, string> {
  const raw = new Map(content.text_entries.map((e) => [e.key, e.text]));
  const names = new Map(content.lane_infos.flatMap((l) => (l.name_key ? [[l.lane, raw.get(l.name_key) ?? ""] as const] : [])));
  const lines = new Set(content.line_infos.map((l) => l.key));
  const found = new Map(content.find_infos.map((f) => [f.line_key, String(Math.floor(f.quantity / content.scales.quantity_per_item))]));
  const fillNames = (key: string, text: string): string => text.replace(/\{(\w+)\}/g, (slot, lane: string) => {
    if (lane === "found") return found.get(key) ?? slot;
    const name = names.get(lane);
    if (name === undefined) return slot;
    return lines.has(key) ? name.toLowerCase() : name;
  });
  return new Map([...raw].map(([key, text]) => [key, fillNames(key, text)]));
}

export class Text {
  private readonly table: Map<string, string>;
  private readonly reported = new Set<string>();

  constructor(content: Content) {
    this.table = named(content);
  }

  has(key: string): boolean {
    return this.table.has(key);
  }

  get(key: string): string {
    const text = this.table.get(key);
    if (text !== undefined) return text;
    if (!this.reported.has(key)) {
      this.reported.add(key);
      console.warn(`ashfall: the content has no text for key "${key}"`);
    }
    return "";
  }

  /** A template with `{name}` slots; a slot with no value is left empty. */
  fill(key: string, slots: Slots): string {
    return this.get(key).replace(/\{(\w+)\}/g, (_, name: string) => slots[name] ?? "");
  }
}
