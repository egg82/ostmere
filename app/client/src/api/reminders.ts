// PUT and DELETE /api/reminders (CONTRACT.txt, "Reminders"): the endpoint only ever in a body.
import type { Subscribed } from "../app/push";
import { ApiFailure, request } from "./api";
import type { components } from "../../generated/schema";

export type ReminderWindow = components["schemas"]["ReminderWindow"];
/** What this browser has on: the absence reminder's window (null: off) and the hands-free notice. */
export type Reminder = components["schemas"]["Reminder"];

export interface RemindersApi {
  /** On as `choice` says, or with null the browser's stored choice; null when it is not on (404). */
  put(keys: Subscribed, tz: string, choice: Reminder | null): Promise<Reminder | null>;
  off(endpoint: string): Promise<void>;
}

const JSON_HEADERS = { "Content-Type": "application/json" } as const;

export const httpReminders: RemindersApi = {
  async put(keys, tz, choice) {
    try {
      const body = { ...keys, tz, window: choice?.window ?? null, hands_free: choice ? choice.hands_free : null };
      const r = await request("/api/reminders", { method: "PUT", headers: JSON_HEADERS, body: JSON.stringify(body) });
      return (await r.json()) as Reminder;
    } catch (e) {
      if (choice === null && e instanceof ApiFailure && e.code === "not_found") return null;
      throw e;
    }
  },
  async off(endpoint) {
    await request("/api/reminders", { method: "DELETE", headers: JSON_HEADERS, body: JSON.stringify({ endpoint }) });
  },
};
