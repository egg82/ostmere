// Numbers into the content's templates. Fixed-point to items by Scales; words only from the text table.
import type { Scales } from "../api/types";
import { Text, UI } from "./text";

const whole = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 });
/** Spans this many hours and over read in days and hours: "47h 59m" still, then "2d". */
export const DAYS_FROM_H = 48;
const rateFormat = new Intl.NumberFormat(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 7, signDisplay: "exceptZero" });   // a rate arrives already cut to its digits
const percent = new Intl.NumberFormat(undefined, { style: "percent", maximumFractionDigits: 0 });
const changeFormat = new Intl.NumberFormat(undefined, { style: "percent", maximumFractionDigits: 2, signDisplay: "exceptZero" });
const day = new Intl.DateTimeFormat(undefined, { day: "numeric", month: "short" });

/** A wall time (ISO 8601) as a date in the browser's locale and zone: {started}, {played}, {until}. */
export function dateOf(iso: string): string {
  return day.format(new Date(iso));
}

export class Format {
  constructor(private readonly text: Text, private readonly scales: Scales) {}

  /** A quantity as whole items, rounded down: a store shows what it holds, never what it nearly holds. */
  items(quantity: number): string {
    return whole.format(Math.floor(quantity / this.scales.quantity_per_item));
  }

  amount(quantity: number, cap: number): string {
    return this.text.fill(UI.amount, { n: this.items(quantity), cap: this.items(cap) });
  }

  /** A card's need: the store's label, what there is (sampled, rounded down) and what one completion takes, rounded
   * up as costs are, so a need never reads as less than it asks. A `have` given as text (the needs' own mark, cardneeds.ts)
   * goes in as it is, in each of the three needs. A spent need (Need.spent) says nothing is left to come. */
  need(store: string, have: number | string, quantity: number, spent: boolean): string {
    const n = whole.format(Math.ceil(quantity / this.scales.quantity_per_item));
    return this.text.fill(spent ? UI.needsSpent : UI.needs, { store, have: typeof have === "string" ? have : this.items(have), n });
  }

  /** A card's step need: the other card's label, its completions and the count wanted. */
  needStep(card: string, have: number | string, count: number): string {
    return this.text.fill(UI.needsStep, { card, have: typeof have === "string" ? have : this.count(have), n: this.count(count) });
  }

  /** A card's skill-level need: the skill's label, the level it has and the level the card wants. */
  needSkill(skill: string, have: number | string, level: number): string {
    return this.text.fill(UI.needsSkill, { skill, have: typeof have === "string" ? have : this.count(have), n: this.count(level) });
  }

  /** A rate per minute, toward zero, with the fewest digits that tell it apart: no trailing zeros, two decimals at most,
   * except a rate under 0.01 keeps digits down to its first, so a rate that is not zero never reads as zero. A flat
   * line has no sign. */
  perMinute(rate: number): string {
    const per = this.scales.rate_per_item_hour * 60;
    const decimals = Math.min(7, Math.max(2, Math.ceil(-Math.log10(Math.abs(rate / per) || 1))));
    const cut = (BigInt(rate) * 10n ** BigInt(decimals)) / BigInt(per);   // BigInt division cuts toward zero, exactly
    return this.text.fill(UI.perMinute, { n: rateFormat.format(Number(cut) / 10 ** decimals) });
  }

  /** A modifier's signed change in basis points as a percent, toward zero with two decimals at most: +1000 reads +10%,
   * -3333 reads -33.33%. A change that is not zero never reads as zero (a smaller one keeps its digits, down to 0.01%). */
  change(bp: number): string {
    const cut = Math.trunc((bp * 10000) / this.scales.bp);   // hundredths of a percent
    return changeFormat.format((cut === 0 ? Math.sign(bp) : cut) / 10000);
  }

  /** The {pct} and {pct_b} slots of a level's, upside's or chip's text: its changes in the order served. */
  figures(changesBp: readonly number[]): Record<string, string> {
    return Object.fromEntries(changesBp.slice(0, 2).map((bp, i) => [i === 0 ? "pct" : "pct_b", this.change(bp)]));
  }

  /** The {gain} and {gain_b} slots of an answer's cost text: the stores it puts in, in whole items, rounded down. */
  gains(gains: readonly { quantity: number }[]): Record<string, string> {
    return Object.fromEntries(gains.slice(0, 2).map((g, i) => [i === 0 ? "gain" : "gain_b", this.items(g.quantity)]));
  }

  share(bp: number): string {
    return percent.format(bp / this.scales.bp);
  }

  /** A span of game seconds, rounded up so a countdown never shows zero before its moment. From DAYS_FROM_H hours it
   * reads in days and hours, rounded up to the hour. */
  duration(seconds: number): string {
    const s = Math.max(0, Math.ceil(seconds));
    if (s >= DAYS_FROM_H * 3600) {
      const hours = Math.ceil(s / 3600), days = Math.floor(hours / 24), h = hours % 24;
      return h === 0 ? this.text.fill(UI.durationD, { days: whole.format(days) }) : this.text.fill(UI.durationDH, { days: whole.format(days), h: whole.format(h) });
    }
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    if (h > 0 && m === 0) return this.text.fill(UI.durationH, { h: whole.format(h) });
    if (h > 0) return this.text.fill(UI.durationHM, { h: whole.format(h), m: whole.format(m) });
    if (m > 0) return this.text.fill(UI.durationMS, { m: whole.format(m), s: whole.format(sec) });
    return this.text.fill(UI.durationS, { s: whole.format(sec) });
  }

  /** A mix's header: runs for a duration, or runs indefinitely as set (view.runs_out_at null). */
  runs(runsOutAt: number | null, t: number): string {
    return runsOutAt === null ? this.text.get(UI.runsIndefinitely) : this.text.fill(UI.runs, { d: this.duration(runsOutAt - t) });
  }

  count(n: number): string {
    return whole.format(n);
  }

  /** A card's completions against its cap ("3/5"); with no cap, the count alone. */
  completions(n: number, cap: number | null): string {
    return cap === null ? this.count(n) : this.text.fill(UI.cardCount, { n: this.count(n), cap: this.count(cap) });
  }
}
