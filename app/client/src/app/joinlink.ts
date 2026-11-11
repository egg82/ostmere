// A join link (CONTRACT.txt, TransferCode.join_url) carries its code in the fragment: #join=ABCD-EFGH. It is read and
// taken off the address bar before anything else runs, analytics included, so no page view, history entry or copied
// link carries it. The code then waits in a join box for the player's tap: a link never joins by itself.

export function takeJoinLink(): string | null {
  const m = /^#join=([^&]*)$/.exec(location.hash);
  if (!m) return null;
  history.replaceState(history.state, "", location.pathname + location.search);
  try {
    return decodeURIComponent(m[1] ?? "") || null;
  } catch {
    return null;
  }
}
