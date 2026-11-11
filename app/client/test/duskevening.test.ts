// The light goes over the evening (tools/scene/grades.py, dusk; scene/conditions.ts, action:; scene/scene.ts,
// gradeStep): `action:<id>` holds while the standing action is in view.standing; a grade whose `when` names the
// evening's action is picked from when the evening starts, before the end; and a grade with ease_s takes that many
// seconds to come on, one without it GRADE_S (2.5).
import { Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { SceneFacts } from "../src/scene/conditions";
import { gradeStep, pickGrade, type SceneGrade } from "../src/scene/manifest";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const mid = fixtureStep("mid", 100).view;
const evening: View = { ...mid, standing: [...mid.standing, { action: "evening", run: "full" }] };
const holds = (view: View, when: string): boolean => {
  const facts = new SceneFacts();
  facts.observe(view);
  return facts.holds(when, view.at, Q);
};
expect("no evening yet: action:evening does not hold", holds(mid, "action:evening"), false);
expect("the evening in view.standing: it holds", holds(evening, "action:evening"), true);
expect("another action's id does not", holds(evening, "action:dawn"), false);

const grade = (when: string | null, ease_s?: number): SceneGrade => ({ when, filter: "none", overlay: "transparent", ...(ease_s === undefined ? {} : { ease_s }) });
const GRADES = { dark: grade(null), warm: grade("chip:cold"), dusk: grade("action:evening|end:showing", 40) };
const shown = (view: View): string | undefined => pickGrade(GRADES, (when) => holds(view, when))?.[0];
expect("before the evening: warm", shown(mid), "warm");
expect("the evening started, no end yet: dusk", shown({ ...evening, ended_at: null }), "dusk");

expect("an eased grade: a second is 1/40 of the way", gradeStep(GRADES.dusk, 1), 1 / 40);
expect("a grade with no ease_s: 2.5 s", gradeStep(GRADES.warm, 1), 1 / 2.5);
expect("no grade: 2.5 s", gradeStep(null, 1), 1 / 2.5);
