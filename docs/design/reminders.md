# Opt-in reminders to play

Open-work item 18. Off by default; the player picks how long an absence triggers one notification; one early mention
points at the setting. Nothing in the game waits on the player (`decisions.md`, "No notifications unless the player
asks"), so the reminder is an invitation, never a summons.

## Fit pass

**What it is an instance of:** a scheduled outbound message whose trigger is the *absence* of an event (no visit for
N hours), delivered over a channel the player opted into. Two parts: a pure question ("is this device due now?") and a
delivery (Web Push).

**What already does something like it** (`docs/systems.md`):
- *Accounts and sign-in* owns who the player is and when they were last seen. It holds no email, so the channel has to
  be a device subscription.
- *Lessons* and `AccountPresentation` (`app/ashfall_app/accounts/presentation.py`) keep "done or skipped, once" as a
  flag that only grows and merges by OR across devices. That is the once-store for the mention.
- *Service locator with Null Object defaults* (`app/ashfall_app/services.py`) is how a sender that may be absent (no
  VAPID keys, tests) answers "nobody", never a plausible wrong answer.
- *Logs, job runs, retention*: one logfmt line per run; anything stored gets a stated limit.
- Not found: there is no story digest, no Notifier, no worker or CronJob, no `ashfall_app.jobs` module and no service
  worker or web manifest. Item 6's "Notifier behind a Null Object" is still only a note.

**Pattern.** Nystrom's *Event Queue* (read, gameprogrammingpatterns.com/event-queue.html) is the obvious candidate and
does not fit: it decouples *when an event is sent from when it is processed*, and its own warning is that queued items
go stale. Here nothing happens at the moment the player leaves, and a queued reminder would be wrong the moment they
return. What fits is a **Specification** (a pure `due(visit, after, last_sent, now, tz)`) evaluated by a poll, with a
**compare-and-set claim** so a send happens once (habits' scheduler shape), behind a small **Strategy/Null Object**
`Sender`. "Due" is derived from stored state, so there is no queue, no timer per player and nothing to drift.

**A system row or a module?** By the four tests in `systems.md` it is a module: one caller (the job), so test 1 fails.
It takes a `Sender` protocol with a Null default passed in by the job's entry point. It becomes a locator row only
when a second caller exists (the story digest).

**Fits into:** Accounts (the visit time, the `AccountPresentation` once-flag, the account merge in `accounts/moving.py`),
the locator's Null Object convention for the sender, Logs/job runs/retention for run lines and the prune, and a
compare-and-set scheduler run as the first `python -m ashfall_app.jobs` entry. New: one table, one module
(`app/ashfall_app/reminders/`), one CronJob. No new system row.

## What habits built

| Piece | Verdict |
|---|---|
| `push/config.py` `load_config`: both VAPID keys valid or push is off | **Copy.** Half a configuration is none. |
| `push/sender.py` `send_one`: no redirects, 404/410 means gone, 12 h TTL, endpoint never logged | **Copy**, TTL stays. |
| `push/services.py` `is_push_service`: allow-list of push hosts (the server POSTs to whatever endpoint is subscribed) | **Copy.** An SSRF guard, not optional. |
| `static/sw.js`: push and click only, deliberately no fetch handler | **Copy.** A fetch handler would break "a page only runs its own build's bundle" (`systems.md`, Page shell). Drop its `postMessage({go: "home"})`. |
| `src/app/push.js` `pushCap()`: ok / denied / iOS-not-installed / none | **Copy the four states.** |
| `push/scheduler.py` + `jobs.py` worker: an always-on asyncio tick under a referee lease | **Reject.** Ostmere has no worker and no lease (item 12: no singletons). |
| `push/checkin.py` `mark_checkin_sent` before sending (compare-and-set) | **Copy the idea**: claim, then send; at most once. |
| `checkin.py` daily check-in times and rates, `nudges.py` LLM-written nudges, recency line picker | **Reject.** A daily cadence is the babysitting pressure `decisions.md` removes. |
| `push_devices` `enabled` flag and a per-device list | **Reject.** Off is deleting the row. |
| `push/devices.py` device names | **Reject.** Nothing shows them. |

Why habits' rules do not carry over whole: habits' check-in carries a task whose miss is the person's life, so
reminding is the point. Ostmere's carries no task and no miss.

## Delivery

**Web Push from a service worker covers it**, and it is the only channel that needs no address. Needs:

- **Page:** a `sw.js` served from the root (`app/ashfall_app/web/app.py` `SERVER_EXACT` gains it, served `no-cache`),
  a web manifest (`display: standalone`, icons), and the subscribe call on a tap, never on load. The public VAPID
  key is not secret; the page gets it with `/page-config.json`.
- **iOS and Safari:** Web Push exists only for a web app added to the Home Screen (iOS 16.4 and later), and the
  permission prompt must come from a tap. In a plain Safari tab the setting shows the same sentence as habits'
  `pushCap`: "Add Ostmere to your Home Screen first, then this works." (No prompt is attempted.) Desktop browsers and
  Android need nothing installed.
- **Table (Alembic 0011, expand-only, so either site's build runs on it):** `reminder_devices(id, account_id FK on delete
  cascade, endpoint unique, p256dh, auth, after_hours, tz, send_from_hour, send_until_hour, visited_at, last_sent_at null, created_at)`. One row is a
  device that has reminders on; no row is off. An account merge (`accounts/moving.py`) moves the rows to the surviving account.
- **Visit time.** `sessions.last_seen_at` renews once a day (`RENEW`, `accounts/sessions.py`), far too coarse: it
  would fire reminders early for someone who visited this morning. So `visited_at` is stamped on the open and advance
  requests, only for an account with a row, in one `UPDATE ... WHERE visited_at < now() - interval '10 min'` folded into
  the statement the request already runs, since item 12 counts round trips. Retention: the job deletes rows whose
  `visited_at` is over 180 days old.
- **Sender job** `python -m ashfall_app.jobs reminders`, a CronJob every 5 minutes on **each** site. Due means
  `visited_at + after_hours <= now`, `last_sent_at` is null or before `visited_at`, and the local hour (`tz`, the device's
  IANA zone sent when it subscribed) is inside the player's window, `send_from_hour` up to `send_until_hour`. A window
  may wrap past midnight (22 until 7); equal ends mean any hour; both are 0 to 23 under a CHECK. Claim: `UPDATE reminder_devices SET last_sent_at = now()
  WHERE id = :id AND (last_sent_at IS NULL OR last_sent_at < visited_at) RETURNING id`; only the winner sends. The
  database is the one writable Postgres both sites reach, so two CronJobs cannot both win, and no etcd lease is needed
  (item 12's contract). Claim before send: a crash or timeout loses one reminder, never doubles one. One reminder per
  absence follows from `last_sent_at < visited_at`: nothing more until the player returns. If they return before it is sent,
  it never goes.
- **Expiry:** a 404 or 410 from the push service deletes the row; any other failure keeps it and is logged. The page
  re-syncs on load (browser subscription against the server's row, upserting fresh keys) and shows Off if the
  browser's is gone, so the setting never lies. The 12 h TTL drops a message the phone was off for.
- **Logs:** one line per run (`reminders.run due= sent= gone= failed= ms=`), one per failure with status; never an
  endpoint, key or token.

**Manifest needs for the cluster session (both sites' ashfall manifests in the cluster repo; we do not edit them):**
1. Secret `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` in the secret store, through the
   namespace's ExternalSecret. **The same pair on both sites**: a subscription is bound to the public key.
2. `VAPID_PUBLIC_KEY` also in env on the `web` Deployment and the app (it is served in `/page-config.json`); the
   private key only on the CronJob.
3. A CronJob `reminders` on each site: the app image, command `python -m ashfall_app.jobs reminders`, `*/5 * * * *`,
   `concurrencyPolicy: Forbid`, small requests, the app's `DATABASE_URL` secret (multi-host, read-write).
4. NetworkPolicy egress for that CronJob: DNS, Postgres, and 443 to the push hosts (`fcm.googleapis.com`,
   `*.push.services.mozilla.com`, `*.push.apple.com`, `*.notify.windows.com`).
5. The edge routes `/sw.js` and `/manifest.webmanifest` to the web tier like the other page files.

## What the player sees

- **The setting** sits in the Devices sheet (`app/client/src/ui/devices.ts`) as a row for this device, off at first:
  "Reminders" with the choices **12 hours, a day, 3 days, a week** (data, one file) and the line "One notification when
  you've been away that long. None after it until you're back." Beside the absence length sits the window the
  reminder may arrive in, the player's own: a slider with two handles over the 24 hours, **from** and **until**, first at 9 and 21 (where the
  setting starts, not a rule). Each handle's label shows 24-hour time with 12-hour time beneath it ("21:00", and below
  it "9 PM"). When the start handle sits past the end handle the window wraps past midnight, and the shaded span shows
  that (from 22 until 7). **Any time** is a separate choice beside the slider, which stores equal ends. Turning it on asks the browser's permission, with the
  purpose already on screen: "Ostmere sends one notification after you've been away for the time you pick." Turning
  it off deletes the row and says "Reminders are off."
- **The single mention.** After the opening's end lines have been read and no lesson holds the glow, one quiet row
  with a button: "If you'd like a nudge to come back, there's a setting for it." / `Open settings`. No dot, glow or
  badge (`decisions.md`, "Shown in the design"). It is shown once per account. The store is a new bool in
  `AccountPresentation` (`reminder_mentioned`, merged by OR like `devices_opened`), **written when the row is drawn**,
  not when it is tapped, so taking it up, closing it, ignoring it and loading it on a second device all leave it gone.
  A new anonymous account counts as a new player and gets one.
- **The reminder's words** (rules; a small pool picked by a hash of the account and `visited_at`, so a stateless job
  needs no counter): an invitation to come back, in the present, about the player and not the game. Never: how long
  they have been away, anything earned, full or waiting, "don't miss", "still", a question that implies a duty, an
  exclamation. Never any content from a save, so nothing spoils. Title "Ostmere". Examples of shape, to be put through
  the voice pass before shipping: "The fire's lit if you want to stop by." "Whenever you like, the camp is there."
  Tapping opens `/`.

## Rejected, and why

- **Email.** Accounts hold none, and asking for one breaks "a plain browser game" (`decisions.md`).
- **In-page only.** Cannot reach a player who is not on the page, which is the whole ask.
- **On by default, or asked at the first screen.** The ask is opt-in and never begging; the first minute belongs
  to the opening.
- **Several mentions or a re-ask after "no".** That is begging.
- **A daily or repeating reminder, a streak, a "your camp needs you" message.** Obligation framing (game-design:
  streaks and daily resets read as obligation); it also makes an optimal check-in schedule.
- **Reminder text with game state** (what is full, what finished). It states a loss that does not exist and would spoil.
- **Event Queue, a per-player timer, a worker with a lease.** See the fit pass; derived "due" needs none.
- **A Notifier system row now.** One caller; the module takes a `Sender` instead.
- **A reminder per save.** The player is away from the game, not from a save.

## Build plan

Each step is one MR; each ships with its test, proven able to fail.

1. **Docs.** `decisions.md` amendment (done with this note), `systems.md` module row and `open-work.md` item 18's "Fits
   into:" line. Test: the citation test over `systems.md`.
2. **Table and due query.** Alembic 0011, `reminders/due.py` (pure), `db/reminders.py` with the claim and prune. Tests:
   a Hypothesis property that `due` fires at most once per `visited_at`; a two-connection Postgres race where exactly
   one claim wins; the prune keeps in-limit rows and drops past-limit ones; a plant (claim without the
   `last_sent_at < visited_at` guard) goes red.
3. **Sender and job.** `reminders/sender.py` (copied from habits, with the Null default), `ashfall_app/jobs.py`
   `reminders`, the logfmt lines. Tests: a fake push service returns 201, 410 and 500 (row kept or deleted, one line
   each); the allow-list refuses a non-push host and a redirect; no endpoint appears in captured logs.
4. **API.** `PUT` and `DELETE /api/reminders` (endpoint in the body, never a URL), `visited_at` stamp, merge handling,
   `reminder_mentioned` in `AccountPresentation` and `CONTRACT.txt`. Tests: the stamp writes at most once per ten
   minutes; a merge moves the rows; the flag ORs across two sessions; the round-trip count on open does not rise.
5. **Page.** `sw.js`, manifest, the Devices row, `pushCap` states, the single mention. Tests: a headless render of the
   row in each state and the iOS-not-installed sentence; the mention draws once, then not after a reload, a second
   device, or a tap. Copy goes through the `writing-craft` voice pass before this merges.
6. **Live check** after deploy and the out-of-band steps: subscribe on a desktop browser, set the shortest
   choice with a clock override in a test account, and watch one notification arrive and no second.

**Out-of-band, by whom:** generating the VAPID pair and putting it in the secret store (the owner or the orchestrator, once, before
step 6); the five manifest items above (the cluster session, `kubernetes-c3`, on both sites, before step 3 deploys
anything that runs); the Home Screen test on an iPhone (the owner, given one; otherwise unproven on iOS and said so).
Merging steps 1 to 5 deploys nothing that sends, since the job runs only where the CronJob exists and the sender is
Null without keys.
