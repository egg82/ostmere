// The hour's light over the scene: dimmer and cooler towards night. 1 is full day and changes nothing (the game's own
// scene never dims; the front page lets the visitor's clock do it).

/** 1 at 13:00, 0 through the night; `hours` is the hour of day with minutes as a fraction. */
export function daylight(hours: number): number {
  const d = Math.cos(((hours - 13) / 24) * Math.PI * 2);
  return Math.max(0, Math.min(1, (d + 0.35) / 1.1));
}

/** The visitor's hour of day, minutes as a fraction. */
export function hoursNow(): number {
  const now = new Date();
  return now.getHours() + now.getMinutes() / 60;
}

/** The grade's filter with the hour's dimming and desaturation appended. */
export function lightFilter(filter: string, day: number): string {
  if (day >= 1) return filter;
  const base = filter === "none" ? "" : `${filter} `;
  return `${base}brightness(${(0.66 + 0.34 * day).toFixed(2)}) saturate(${(0.78 + 0.22 * day).toFixed(2)})`;
}

/** The cold wash laid over the grade at night, or null by day. */
export function duskWash(day: number): string | null {
  return day >= 1 ? null : `rgba(16, 22, 44, ${(0.26 * (1 - day)).toFixed(2)})`;
}
