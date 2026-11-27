// The pot's lesson (decisions/mixes.md, "One pot on the fire"): the first time a station (the pot on the fire) has a
// second task, ui/town/lanerows.ts marks its Change; taught on Change, the kinds on its page, and the rules that can switch them.
import type { Lesson } from "./lessons";
import { UI } from "./text";

export const POT = "pot";

export const POT_LESSON: Lesson = {
  id: POT,
  may: () => true,
  trigger: `[data-teach="pot-change"]`,
  steps: [
    { target: () => `[data-teach="pot-change"]`, line: (c) => c.text.get(UI.lessonPotChange), ends: "touch" },
    { target: () => `.person-page .person-cards`, line: (c) => c.text.get(UI.lessonPotPick), ends: "read" },
    { target: () => `.person-page .person-rules`, line: (c) => c.text.get(UI.lessonPotRule), ends: "read" },
  ],
};
