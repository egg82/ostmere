// /page-config.json's reminders, fetched once. `undefined`: the server is a build from before reminders (no key at
// all), so the page offers nothing; null: reminders are not available here (no VAPID key).
export interface RemindersConfig {
  public_key: string;
  after_hours: number[];
}

let asked: Promise<RemindersConfig | null | undefined> | null = null;

export function remindersConfig(): Promise<RemindersConfig | null | undefined> {
  asked ??= fetch("/page-config.json")
    .then((r) => (r.ok ? (r.json() as Promise<{ reminders?: RemindersConfig | null }>) : { reminders: undefined }))
    .then((cfg) => cfg.reminders)
    .catch(() => undefined);
  return asked;
}
