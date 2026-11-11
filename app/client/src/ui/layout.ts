// The media queries the game screen's layout switches on (game.css holds the matching rules).

/** Where the skills and ledger sit under the scene (game.css, ".low"): a desktop window tall enough for it. */
export const LOW_UNDER_SCENE = "(min-width: 1024px) and (min-height: 600px)";

/** The phone layout (game.css): chips and the Camp bar sit above the art, and the stage takes the art's own height. */
export const PHONE = "(max-width: 1023px) and (orientation: portrait), (max-width: 639px)";
