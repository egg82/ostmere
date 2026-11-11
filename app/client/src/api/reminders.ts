// PUT and DELETE /api/reminders (CONTRACT.txt, "Reminders"): the endpoint only ever in a body.
import type { Subscribed } from "../app/push";
import { ApiFailure, request } from "./api";
import type { components } from "../../generated/schema";

export type ReminderWindow = components["schemas"]["ReminderWindow"];

export interface RemindersApi {
  /** On with `window`, or with null the browser's stored window; null when it is not on (404). */
  put(keys: Subscribed, tz: string, window: ReminderWindow | null): Promise<ReminderWindow | null>;
  off(endpoint: string): Promise<void>;
}

const JSON_HEADERS = { "Content-Type": "application/json" } as const;

export const httpReminders: RemindersApi = {
  async put(keys, tz, window) {
    try {
      const r = await request("/api/reminders", { method: "PUT", headers: JSON_HEADERS, body: JSON.stringify({ ...keys, tz, window }) });
      return ((await r.json()) as { window: ReminderWindow }).window;
    } catch (e) {
      if (window === null && e instanceof ApiFailure && e.code === "not_found") return null;
      throw e;
    }
  },
  async off(endpoint) {
    await request("/api/reminders", { method: "DELETE", headers: JSON_HEADERS, body: JSON.stringify({ endpoint }) });
  },
};
