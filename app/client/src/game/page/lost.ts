// What the page does when its session is gone. Normally it reloads, which starts over from the front page. A game
// just started inside another site's frame whose cookie the browser refuses (Safari, every iOS browser) is gone on
// the very next request; reloading would only start another game, so the page says so and offers its own tab.

/** What a window says of where it sits: Window has both. */
export interface FrameView { readonly top: unknown; readonly self: unknown }

/** Whether the page runs inside another page's frame. A window that cannot be read is taken to be framed. */
export function framed(win: FrameView): boolean {
  try {
    return win.top !== win.self;
  } catch {
    return true;
  }
}

/** `fresh`: the session was begun on this page and has not been answered since. */
export function onLost(win: FrameView, fresh: boolean, unkept: () => void, reload: () => void): void {
  if (fresh && framed(win)) unkept();
  else reload();
}
