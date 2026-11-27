// FIXTURE, never shipped: a GameApi that answers from fixtures/steps.ts, moving between phases on the decisions the
// page sends, and logging each request so a screenshot run can see what the page asked for. Game time is the wall
// seconds since Begin, as the server's is.
import { FIRST_MIX, FIRST_RULE, JOURNAL } from "../src/game/lessons/lessons";
import { FIXTURE_CODE, fixtureDevices } from "./devices";
import { ApiFailure, type GameApi } from "../src/api/api";
import type { AccountPresentation, AccountSettings, Decision, GoalRow, Mix, SaveInfo, SavePresentation, Step } from "../src/api/types";
import { fixtureContent } from "./content";
import { CHRONICLE_VISITS, chronicleStep, isChronicle } from "./chronicle";
import { dayOneStep, isDayOne } from "./dayone";
import { dayTwoStep, isDayTwo } from "./daytwo";
import { fightsStep, isFights } from "./fights";
import { fixtureGames } from "./games";
import { isJournal, journalStep, LONG_READ, LONG_READ_TO, READ_TO } from "./journal";
import { isPrestige, prestigeStep } from "./prestige";
import { isGroups, groupsStep } from "./groups";
import { isTown, townStep } from "./town";
import { fixtureStep, type Kept, type Phase } from "./steps";
import { SINCE_VISITS, isSince, sinceBack, sinceStep } from "./since";
import { asksStep, isAsks } from "./asks";
import { isLedgerRules, ledgerRulesStep } from "./ledgerrules";
import { feelStep, isFeel } from "./feel";
import { guardsStep, isGuards } from "./guards";

const stepOf = (phase: Phase, at: number, kept: Kept = {}, decisions = 0): Step =>
  (isFeel(phase) ? feelStep(at, kept, decisions) : isAsks(phase) ? asksStep(phase, at, kept, decisions) : isLedgerRules(phase) ? ledgerRulesStep(phase, at, kept, decisions) : isGuards(phase) ? guardsStep(phase, at, kept, decisions) : isChronicle(phase) ? chronicleStep(at, kept, decisions) : isSince(phase) ? sinceStep(phase, at, kept, decisions) : isFights(phase) ? fightsStep(phase, at, kept, decisions) : isJournal(phase) ? journalStep(phase, at, kept, decisions) : isDayOne(phase) ? dayOneStep(phase, at, kept, decisions) : isDayTwo(phase) ? dayTwoStep(phase, at, kept, decisions) : isTown(phase) ? townStep(phase, kept, decisions) : isGroups(phase) ? groupsStep() : isPrestige(phase) ? prestigeStep(phase, at, kept, decisions) : fixtureStep(phase, at, kept, decisions));

/** `unavailable`: every step after Begin answers 503 (the page's reconnecting state). `seen`: the player has seen a
 * rule come on and let go (writing rules is open). `limited`: a send of feedback answers 429. `due`: recovery words
 * are due. */
export function fixtureApi(first: Phase, unavailable = false, seen = false, limited = false, due = false): GameApi {
  const kept: Kept = {};
  const games = fixtureGames();
  let phase = first;
  let decisions = 0;
  let began = Date.now();
  const now = (): number => Math.floor((Date.now() - began) / 1000);
  const taught = first === "repeattap" || first === "repeatswitch" || isDayTwo(first) || isFights(first) || isJournal(first) || isTown(first) || isGroups(first) || isPrestige(first) || isChronicle(first) || isSince(first) || isAsks(first) || isLedgerRules(first) || isGuards(first) || isFeel(first);   // the repeat offers come only after the lessons
  const player: AccountPresentation = { rules_opened: false, devices_opened: false, reminder_mentioned: false, ledger_lines: [], mix_stopped: [], switch_offered: [], journal_read: first === "journalbook" ? LONG_READ : [] };
  const taughtSave: SavePresentation = { rule_seen: seen, mix_offered: [], lines_touched: [], lane_tasks_seen: [], lessons: taught ? [FIRST_MIX, FIRST_RULE, ...(first === "journal" ? [JOURNAL] : [])] : [], lesson_ends: [], visits: isChronicle(first) ? CHRONICLE_VISITS : isSince(first) ? SINCE_VISITS : [],
    newest_day_read: first === "journalbook" ? LONG_READ_TO : first === "journalweeks" || first === "journaltoday" ? READ_TO : null };
  const settings: AccountSettings = { lessons: true };
  const info = (): SaveInfo => ({
    save_id: 1, number: 1, decisions, game_time: now(), ended_at: null, started_at: new Date(began).toISOString(),
    played_at: new Date().toISOString(), camp_level: 0,
  });
  /** The player's main mix is the one the first-mix offer (or the fixture's MIX) made; other saves sit beside it. */
  const keepMix = (mix: Mix, at: Phase): void => {
    const main = kept.mix?.id ?? fixtureStep("mid", 0).view.active_mix_id;
    if (at === "firstmix" || mix.id === main) kept.mix = mix;
    else kept.extra = [...(kept.extra ?? []).filter((m) => m.id !== mix.id), mix];
  };
  const next = (d: Decision | null, keep: boolean): Phase => {
    if (d?.kind === "tap_card" && phase === "start") return "standing";
    if (d?.kind === "tap_card" && phase === "alone") return "aloneDone";   // the lone first card finishes: its line and the panel foot
    if (phase === "standing") return "mid";
    if (d?.kind === "tap_card" && (phase === "fight" || phase === "fightlater")) return phase === "fight" ? "fightlater" : "fightmany";   // each tap: a window of fights since the last view
    if (phase === "away" && d === null && now() > 0) return "mid";   // time passed with the page shut or hidden
    if (phase === "restaway" && d === null && now() > 0) return "restoffer";
    if (phase === "returned" && d === null && now() > 0) return "landed";   // a planned moment landed while away
    if (isSince(phase) && d === null && now() > 0) return sinceBack(phase) ?? phase;   // shown again: the return
    if (phase === "prestigeaway" && d === null && now() > 0) return "prestige";   // firecraft topped out while away
    if (d?.kind === "prestige") return "prestigeclicked";
    if (d?.kind === "undo_pick") return "prestigeowed";
    if (d?.kind === "move_pick") return "prestigeparked";
    if (d?.kind === "set_queue" && keep) kept.queue = d.entries;
    if (d?.kind === "set_queue") return phase === "whenready" ? "queued" : phase;
    if (d?.kind === "set_orders" && keep) kept.orders = d.orders;
    if (d?.kind === "answer_offer" && isAsks(phase)) {
      if (keep) kept.answered = [...(kept.answered ?? []), `${d.offer}:${d.answer}`];
      return phase;
    }
    if (d?.kind === "answer_offer") return "answered";
    if (d?.kind === "set_orders" && isDayTwo(phase)) return phase;
    if (d?.kind === "set_orders" && phase === "restoffer") return "restrule";
    if (d?.kind === "set_orders" && phase === "ruleoffer") return "ruleon";   // the rule lesson: a rule set mid-lesson comes on
    if (d?.kind === "set_orders") return phase === "orderlist" || phase === "rulemix" || phase === "written" || phase === "restrule" || phase === "rulestab" ? phase : "covered";
    if (d?.kind === "save_mix" && keep) keepMix(d.mix, phase);
    if (d?.kind === "save_mix" && phase === "firstmix") return "mid";
    return phase;
  };
  const step = (d: Decision | null): Promise<Step> => {
    if (unavailable) return Promise.reject(new ApiFailure("save_unavailable", "fixture: unavailable", null, 3));
    if (d?.kind === "answer_offer" && phase === "answered") return Promise.reject(new ApiFailure("invalid_decision", "fixture: already answered"));
    phase = next(d, true);
    if (d) decisions += 1;
    const s = stepOf(phase, now(), kept, decisions);
    const failed = d?.kind === "tap_card" && d.card === "look";
    return Promise.resolve(failed ? { ...s, lines: [...s.lines, { at: now(), seq: s.lines.length, key: "line.4", card: "look", opens_beat: false }] } : s);
  };
  return {
    content: () => Promise.resolve(fixtureContent),
    me: () => Promise.resolve({ account: { presentation: player, settings, has_words: false, words_due: due }, saves: [], max_saves: 5, kept_days: 30 }),
    begin: () => {
      began = Date.now();
      phase = first;
      decisions = 0;
      return Promise.resolve({ save: info(), presentation: structuredClone(taughtSave), step: stepOf(first, 0) });
    },
    open: () => Promise.reject(new ApiFailure("not_found", "fixture: no saves to open")),
    advance: () => step(null),
    savedView: () => Promise.reject(new ApiFailure("not_found", "fixture: no saves to show")),
    mixRows: () => step(null).then(({ view }) => {   // authored, not the engine's: each mix a little slower than the one before
      const own = view.mixes.filter((m) => !m.id.startsWith("town:"));
      const base: GoalRow[] = view.goal_rows.length > 0 ? view.goal_rows : [
        { kind: "store" as const, store: "wood", skill: null, target: 20_000, lands_at: view.at + 5400, per_hour: 36_000, limit: null,
          until: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 20_000, release: 20_000 } as GoalRow["until"] },
        { kind: "level" as const, store: null, skill: "foraging", target: 3, lands_at: view.at + 9000, per_hour: 12_000, limit: null,
          until: { kind: "at_least", watched: { kind: "skill_level", skill: "foraging" }, value: 3, release: 3 } as GoalRow["until"] },
      ];
      const rows = own.map((m, i) => ({
        id: m.id,
        goals: base.map((g) => ({ ...g, lands_at: g.lands_at === null ? null : g.lands_at + i * 900 })),
        nets: base.flatMap((g) => g.store === null ? [] : [{ store: g.store, per_hour: g.per_hour + i * 120 }]),
        runs_out_at: i === 0 ? null : view.at + 7 * 3600,
      }));
      const best = base.flatMap((g) => g.lands_at === null || own.length === 0 ? [] : [{
        goal: `${g.kind}|${g.store ?? ""}|${g.skill ?? ""}|${g.target}`, mix_id: own[0]?.id ?? "", lands_at: g.lands_at - 300, saved_at: view.at - 3600 }]);
      return { at: view.at, rows, best };
    }),
    forecast: () => step(null).then((s) => ({   // the phase's own view carries the forecast it is drawn with
      decisions: s.decisions, forecast: s.view.forecast ?? { horizon_at: s.view.at + 6 * 3600, level_ups: [], tops_out: [], fills: [], empties: [] },
    })),
    decide: (_id, d) => {
      console.info("fixture decision", JSON.stringify(d), "at", now());
      return step(d);
    },
    dryRun: (_id, ds) => {
      const was = phase;
      let at: Phase = phase;
      let preview: Kept = kept;
      for (const d of ds) {
        at = next(d, false);
        phase = at;
        if (d.kind === "save_mix") preview = { ...preview, mix: d.mix };
        if (d.kind === "answer_offer") preview = { ...preview, answered: [...(preview.answered ?? []), `${d.offer}:${d.answer}`] };
      }
      phase = was;
      return Promise.resolve(stepOf(at, now(), preview, decisions).view);
    },
    putMePresentation: (presentation) => Promise.resolve({ presentation, settings, has_words: false, words_due: false }),
    putMeSettings: (s) => { settings.lessons = s.lessons; return Promise.resolve({ presentation: player, settings, has_words: false, words_due: false }); },
    putSavePresentation: (_id, presentation) => Promise.resolve(presentation),
    sendFeedback: () => (limited ? Promise.reject(new ApiFailure("rate_limited", "429")) : Promise.resolve()),
    makeCode: () => Promise.resolve(FIXTURE_CODE),
    makeWords: () => Promise.resolve({ words: "ember-lantern-gravel-oyster", label: "Ostmere" }),
    // a code with "BUSY" in it finds this device holding games of its own (moved on Move my games, which reloads into
    // the fixture; left behind on Join without moving, which answers the words step: new words, or none to show when the
    // code also has "HAD"), and one with "WORDS" too finds both accounts holding recovery words; one with "FULL",
    // games past the cap on both together; anything else, no such code
    join: (typed, way) => {
      const summary = { here: 3, there: 3, there_newest_game_time: 0, max_saves: 5, words_replaced: /words/i.test(typed) };
      if (/full/i.test(typed)) return Promise.reject(new ApiFailure("too_many_saves", "fixture: past the cap", null, null, summary));
      if (/busy/i.test(typed) && way === "keep") {
        const kept = { saves: 2, words: /had/i.test(typed) ? null : "ember-lantern-gravel-oyster", label: "Ostmere" as const };
        return Promise.resolve({ moved: 0, account: { presentation: player, settings, has_words: false, words_due: due }, kept });
      }
      if (/busy/i.test(typed) && way === "move") return Promise.resolve({ moved: 2, account: { presentation: player, settings, has_words: false, words_due: due } });
      if (/busy/i.test(typed)) return Promise.reject(new ApiFailure("confirm_merge", "fixture: this device has games", null, null, { ...summary, here: 2 }));
      return Promise.reject(new ApiFailure("no_such_code", "fixture: no such code"));
    },
    ...games,
    ...fixtureDevices(),
  };
}
