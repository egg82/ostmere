// The words of an answer_kind rule (issue 69): it answers every future ask of a kind, so it is worded by the kind's own
// label for the role, never by the label of one ask's answer; an answer_offer keeps its ask's own label.
import { install } from "../../fake-dom";
import { fixtureContent } from "../../../fixtures/content";
import type { Content } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { answerWords } from "../../../src/game/town/lanes";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

// The fixture's "ask" offer, made a kind of its own: its answer "go" is the role "yes" and reads "Go now"; the fixture's
// kind has its own labels for the roles.
const content: Content = {
  ...fixtureContent,
  offer_infos: fixtureContent.offer_infos.map((o) => (o.offer !== "ask" ? o
    : { ...o, kind: "q", answers: o.answers.map((a) => ({ ...a, role: a.answer === "go" ? "yes" : "no" })) })),
};
const catalog = new Catalog(content);

expect("a kind rule, by the kind's label", answerWords(catalog, { kind: "answer_kind", offer_kind: "q", role: "yes" }), "Answer: Say yes");
expect("a kind rule's other role", answerWords(catalog, { kind: "answer_kind", offer_kind: "q", role: "no" }), "Answer: Say no");
expect("an offer rule, by its ask's label", answerWords(catalog, { kind: "answer_offer", offer: "ask", answer: "go" }), "Answer: Go now");
