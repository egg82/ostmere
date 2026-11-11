// The scene's grade on the story's clock (scene/scene.ts, pickGrade; tools/scene/grades.py, pick): the last grade whose
// `when` holds wins, so the end's dusk, pinned by ended_at, gives way to the night and the night to the day.
import { Q } from "../fixtures/content";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { SceneFacts } from "../src/scene/conditions";
import { pickGrade, type SceneGrade } from "../src/scene/manifest";

function expect(label: string, got: unknown, want: unknown): void {
  if (got !== want) throw new Error(`${label}: got ${String(got)}, want ${String(want)}`);
}

const grade = (when: string | null): SceneGrade => ({ when, filter: "none", overlay: "transparent" });
/** The shipped order (grades.py): the default, the opening's two lifts, the end, then the night and the day. */
const GRADES = {
  dark: grade(null), cold: grade("project:look"), warm: grade("chip:warm"), dusk: grade("end:showing"),
  night: grade("feature:night"), day: grade("feature:morning"),
};

function shown(view: View): string | undefined {
  const facts = new SceneFacts();
  facts.observe(view);
  return pickGrade(GRADES, (when) => facts.holds(when, view.at, Q))?.[0];
}

const before = fixtureStep("mid", 100).view;   // the warm chip on, no end
expect("before the end: the warm grade", shown({ ...before, chips: ["warm"] }), "warm");
expect("nothing holds: the first", shown(fixtureStep("start", 0).view), "dark");
const ended = fixtureStep("restrule", 100).view;   // ended ten minutes back
expect("the end: dusk over warm", shown(ended), "dusk");
expect("nightfall: night over the dusk the end pins", shown(dayOneStep("night", 100).view), "night");
expect("morning: day over the night", shown(dayOneStep("morning", 100).view), "day");
expect("a grade with no `when` never wins later", pickGrade({ a: grade("end:showing"), b: grade(null) }, () => true)?.[0], "a");
expect("no grades: none", pickGrade({}, () => true), undefined);
