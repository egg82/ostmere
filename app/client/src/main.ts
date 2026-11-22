// The front page's entry (bundled to game.js, served at /build/<build>/): the game against the real server.
import "./controls.css";
import "./game.css";
import "./front.css";
import "./fights.css";
import "./reminders.css";
import "./slider.css";
import "./map.css";
import { boot } from "./app/boot";

boot();
// The page loaded whole: a later failed boot may reload once again (static/index.html, bootFailed).
addEventListener("load", () => {
  if ("ashfallBootFailed" in window) return;
  try { sessionStorage.removeItem("ashfall.boot.reloaded"); } catch { /* no storage: no mark either */ }
});
