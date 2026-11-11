// The text keys of the reminders row in the "Another device" sheet and its one mention (merged into `UI`, game/text.ts).
export const REMINDER_KEYS = {
  remindersHeading: "ui.reminders.heading",
  remindersLead: "ui.reminders.lead",   // what turning on does, on screen before the browser asks
  remindersAway: "ui.reminders.away",   // the absence choices' legend
  remindersH12: "ui.reminders.h12",   // "{n}" hours
  remindersH24: "ui.reminders.h24",
  remindersH72: "ui.reminders.h72",   // "{n}" days
  remindersH168: "ui.reminders.h168",
  remindersWindow: "ui.reminders.window",   // the slider's legend
  remindersFrom: "ui.reminders.from",   // the start handle's name
  remindersUntil: "ui.reminders.until",   // the end handle's name
  remindersWindowSaid: "ui.reminders.window_said",   // "{from} until {until}": the window in words, each a time
  remindersAnyTime: "ui.reminders.any_time",
  remindersOn: "ui.reminders.turn_on",
  remindersOffButton: "ui.reminders.turn_off",
  remindersIsOn: "ui.reminders.is_on",
  remindersIsOff: "ui.reminders.is_off",
  remindersUnavailable: "ui.reminders.unavailable",   // no VAPID key on this server
  remindersInstall: "ui.reminders.install",   // iOS, not added to the Home Screen
  remindersDenied: "ui.reminders.denied",
  remindersNone: "ui.reminders.none",   // this browser has no Web Push
  remindersFailed: "ui.reminders.failed",
  remindersMention: "ui.reminders.mention",
  remindersMentionOpen: "ui.reminders.mention_open",
} as const;

/** The key naming an absence of `hours` (reminders.after_hours in /page-config.json), and its {n}: days when whole. */
export function awayKey(hours: number): { key: string; n: number } {
  return { key: `ui.reminders.h${hours}`, n: hours % 24 === 0 ? hours / 24 : hours };
}
