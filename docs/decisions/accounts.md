# Accounts and sign-in

Who is playing, with no sign-up.

## A plain browser game: the account is the browser

No Authentik, no hearth, no sign-up (since the game is meant for the public): the first visit makes an anonymous account held by a cookie, with no passwords or
email. A short transfer code (or a QR code for a camera) joins another device to the same account, so a game moves
between phone and computer. Each account has several saves (below). Nobody's Claude access is managed: every save
shares one daily budget (below), so no account can drain anything. Joining a device to an account is to move that device's
own games into it, after a confirmation, so nothing is lost (refused while the two together would pass the cap on games); a "write this down" recovery phrase is a second way back
for a player whose only device is gone. The phrase is four words, made when the player asks and
shown once, offered to the browser's password manager, and replaced whole by new words; the game marks the way to
make them with a dot once a game has had a few days of play.

The game plays inside another site's page too (galaxy.click lists games in a frame on its own site;
2026-10-18). The session cookie is SameSite=None and Partitioned, so a browser keeps one account for the game at its
own address and another for each site that embeds it; a transfer code or the recovery words join them, as between
devices. With the cookie on cross-site requests, writes are held to this site by the Origin check alone (an https
Origin naming this host), never by SameSite. Safari refuses cookies in a cross-site frame, so the embedded game keeps
no session there and cannot be played; those players play at the game's own address. No token-in-storage fallback.

## Accounts, logs and reminders, as built

How these stand today, moved from their rows in `systems.md`.

Accounts and sign-in: an anonymous account per browser; a transfer code (or QR) joins another device to it; no
external sign-in (`decisions.md`, "A plain browser game"). Several saves per account. Tests sign in through sessions.
Built: `app/ashfall_app/accounts/interface.py` (null: no database), the session cookie, the limits
(`app/ashfall_app/accounts/limits.py`), moving to another device (`app/ashfall_app/accounts/moving.py`), and the list
of an account's devices, one per session, whose removal signs that browser out (`app/ashfall_app/api/device_routes.py`):
a transfer code with its link and QR, recovery words, and the join made with either one, which folds an empty device's
account into the other; a join moves every save of the account. A device with games of its own is asked first, then
merges: its saves move into the other account, numbered after that account's, in one transaction, refused when the two
together would pass the cap on games (`app/ashfall_app/accounts/join.py`).

Logs, job runs, retention: the setup is in `docs/engineering.md`. Records the owner reads back are tables whose writer
deletes past a limit on insert: tester feedback (`app/ashfall_app/feedback/service.py`, 180 days), counted by the same
tries limit as new accounts (`app/ashfall_app/accounts/limits.py`). Read with `python -m ashfall_app.feedback list`.
Deleted saves are held 30 days, then deleted for good by the next delete or new game
(`app/ashfall_app/saves/games.py`). The page reports pageviews and events to Umami (stats.yggdrasil.pub), and errors
and where the player left to `/api/client-errors`, which logs them (log retention: Loki's, 60 days); ids and counts
only (`app/client/src/telemetry.ts`; config `app/ashfall_app/page_config.py`).

Reminders: `app/ashfall_app/reminders/`, run as `app/ashfall_app/jobs/`; the table is `reminder_devices`
(`app/ashfall_app/db/reminders.py`). Only the job asks its question: the api and page config read its offered absences
and push-host check, and accounts and saves touch the table, not the module. That fails the many-callers test, so it is
not a system; it becomes a locator row when a second caller of `due` (the story digest) exists. Off is no row. Design:
`docs/design/reminders.md`.
