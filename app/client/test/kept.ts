// Keeps for tests from one flat record of what the account and the save keep: most suites set a lesson and a ledger
// line side by side and read back the page's whole copy, whichever half a keep went to. Which half each keep goes to is
// keeps.test.ts's.
import type { AccountPresentation, AccountSettings, SavePresentation } from "../src/api/types";
import { Keeps, NEW_ACCOUNT, NEW_SAVE } from "../src/game/keeps";

export type Flat = AccountPresentation & SavePresentation;
export const NEW_FLAT: Flat = { ...NEW_ACCOUNT, ...NEW_SAVE };

function pick<T extends object>(shape: T, from: Flat): T {
  return Object.fromEntries(Object.keys(shape).map((k) => [k, structuredClone(from[k as keyof Flat])])) as T;
}

/** Keeps holding `flat`; each send (to either half) pushes the page's whole copy, flat, onto `sent`. */
export function keepsOf(flat: Partial<Flat> = {}, sent: Flat[] | null = null, settings?: AccountSettings): Keeps {
  const whole: Flat = { ...NEW_FLAT, ...flat };
  const record = (): void => { sent?.push({ ...keeps.kept.account, ...keeps.kept.save }); };
  const keeps: Keeps = new Keeps({ account: pick(NEW_ACCOUNT, whole), save: pick(NEW_SAVE, whole), settings }, { account: record, save: record });
  return keeps;
}
