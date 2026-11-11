// The game, started in place on the front page: a Session on the save the server holds, a Screen drawing it, the
// Scene inside it, and one animation frame loop sampling the view against the page's clock.
import type { GameApi } from "./api/api";
import type { Account } from "./api/types";
import { Catalog } from "./game/catalog";
import { onLost } from "./game/lost";
import type { Keeps } from "./game/keeps";
import { Session } from "./game/session";
import { Scene, SCENE_MANIFEST } from "./scene/scene";
import { SelfUpdate } from "./app/selfupdate";
import { browserStraight, type Straight } from "./app/straight";
import { noteGame } from "./telemetry";
import { CatchingUp } from "./ui/catchingup";
import { Devices } from "./ui/devices";
import { remindersConfig } from "./app/pageconfig";
import { browserEnv, pushCap } from "./app/push";
import { ReminderMention } from "./ui/remindermention";
import { GamesSheet } from "./ui/games";
import { Screen } from "./ui/screen";

/** Which save to play: one to open (the account's newest), or a new one (Begin). */
export interface Play {
  resume: number | null;
  /** Begin was refused for now (too many new games from here): the front page says so. */
  limited?: () => void;
  /** A game just begun inside another site's frame was lost at once (the browser keeps no cookie there). */
  unkept?: () => void;
  /** This browser's account as GET /api/me answered it (recovery words, their dot). */
  account?: Account | null;
  /** A join link's code: the game opens with the "Another device" sheet's join box holding it. */
  join?: string | null;
}

export function play(api: GameApi, host: HTMLElement, what: Play, sceneManifest = SCENE_MANIFEST): Session {
  let screen: Screen | null = null;
  let scene: Scene | null = null;
  let devices: Devices | null = null;
  let games: GamesSheet | null = null;
  let catching: CatchingUp | null = null;
  let mention: ReminderMention | null = null;
  let join = what.join ?? null;
  // held while a dialog is open, and while the screen still reveals in turn (a reload never cuts a line short)
  const updater = new SelfUpdate(() => document.querySelector("dialog[open]") !== null || (screen?.revealing ?? false));
  const session: Session = new Session(api, {
    started(content, step, keeps, history) {
      const carried = screen?.storyPast ?? null;   // a deploy redraws the screen: its story stays
      keepGame(step.save_id);
      screen?.root.remove();
      scene = null;
      const catalog = new Catalog(content);
      screen = new Screen(catalog, (d) => void session.decide(d), (ds) => session.dryRun(ds), keeps, (t) => session.feedback(t));
      host.append(screen.root);
      devices?.root.remove();
      devices = new Devices(api, catalog.text, catalog.format, content.transfer_code_s, keeps, what.account ?? null);
      screen.foot.append(devices.button);   // beside Feedback, in the panel's last row
      host.append(devices.root);
      games?.root.remove();
      games = gamesSheet(api, catalog, session, step.save_id, skipLessons(keeps, () => screen?.redraw()));
      screen.foot.append(games.button);   // beside Another device
      host.append(games.root);
      catching?.hide();
      catching?.root.remove();
      catching = new CatchingUp(catalog.text);
      host.append(catching.root);
      const opened = devices;
      mention = new ReminderMention(keeps, catalog.text, () => { opened.open(null); opened.reminders.focus(); }, remindersConfig,
        () => pushCap(browserEnv()));
      if (join !== null) devices.open(join);
      join = null;
      screen.restore(history ?? carried ?? []);
      screen.show(step);
      const { sceneBox, sceneCanvas } = screen;
      sceneBox.classList.add("loading");
      void Scene.load(sceneCanvas, sceneManifest, content.scales.quantity_per_item).then((s) => {
        scene = s;
        sceneBox.classList.remove("loading");
        sceneBox.classList.toggle("no-art", s === null);
        if (s && session.view) s.update(session.view);
      });
    },
    stepped(step, _prev, away) {
      catching?.hide();
      screen?.show(step, away);
      scene?.update(step.view);
      if (screen) void mention?.check(screen.moment, screen.foot);
    },
    build(build) {
      updater.seen(build);
    },
    refused() {
      catching?.hide();
      screen?.redraw();
    },
    connected(ok) {
      document.body.classList.toggle("reconnecting", !ok);
    },
    lost(fresh) {
      onLost(window, fresh, () => { catching?.hide(); takeDown(screen, devices, games, catching); what.unkept?.(); }, () => location.reload());
    },
    limited() {
      what.limited?.();
    },
    catchingUp(at, to) {
      catching?.show(session.view?.at ?? at, at, to);   // the view in hand is the one the player last saw
    },
  }, { account: what.account?.presentation, settings: what.account?.settings });

  run(session, () => screen, () => scene);
  const started = what.resume === null ? session.begin() : session.resume(what.resume);
  void started.catch((e: unknown) => console.error("ashfall: the game could not start", e));
  return session;
}

/** One animation frame loop sampling the view against the session's clock, drawing the screen and scene in hand; and a
 * return asked for when the page is shown again. */
function run(session: Session, screen: () => Screen | null, scene: () => Scene | null): void {
  let last = performance.now();
  const frame = (now: number) => {
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    session.tick();
    const view = session.view;
    if (view && document.visibilityState === "visible") {
      const t = session.clock.sampleTime(view);
      screen()?.tick(t);
      scene()?.draw(t, dt);
    }
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && session.view) void session.advance(true);   // reopening: what it brings is revealed in turn
  });
}

/** The game's screen and its sheets come down, so the front page beneath is the one in view. */
function takeDown(...parts: ({ readonly root: HTMLElement } | null)[]): void {
  for (const part of parts) part?.root.remove();
}

/** The Games sheet of the save this page plays: a switch or a new game plays in place, and the tab keeps its game. */
function gamesSheet(api: GameApi, catalog: Catalog, session: Session, playing: number, skip: Straight): GamesSheet {
  return new GamesSheet(api, catalog.text, {
    playing: () => playing,
    open: (id) => { noteGame("switch", id); void session.resume(id); },
    begun: (made) => { noteGame("new", made.save.save_id); void session.begin(made); },
    straight: browserStraight(),
    skipLessons: skip,
  });
}

/** The lessons setting as the Games sheet's "skip" checkbox; a change redraws the screen, so a guided offer turns to its
 * one tap (or back) at once. */
function skipLessons(keeps: Keeps, redraw: () => void): Straight {
  return { get: () => !keeps.lessonsOn(), set: (skip) => { keeps.keepLessonsOn(!skip); redraw(); } };
}

/** The tab's game, kept in its address (#game=ID) as it starts, so a reload opens it again whatever the front page's setting (begin.ts). */
function keepGame(saveId: number): void {
  history.replaceState(history.state, "", `${location.pathname}${location.search}#game=${saveId}`);
}
