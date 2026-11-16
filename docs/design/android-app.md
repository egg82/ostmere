# The Android app

**Decision: a Trusted Web Activity (TWA) that opens the live site, with reminders staying Web Push through the
browser. Nothing is rebuilt natively.** One signing key, one APK, shipped three ways: GitHub releases for Obtainium
first, then an own F-Droid repo, then main F-Droid if the owner wants it. A shell change is the only reason to
ship a new APK, since the game itself updates on the server.

This is the owner's "a fancy browser with push" (`#82`). The web side already exists: the manifest
(`app/ashfall_app/static/push/manifest.webmanifest`), the service worker, and the reminders in
`docs/design/reminders.md`.

## Shell

**TWA, built on `androidbrowserhelper`** (Apache-2.0, checked against the repo's licence metadata and README). The
APK holds a launcher activity and a verified link to the site. The browser draws the page, so the page keeps its own
service worker, cache and Web Push; the shell adds no second copy of any of it.

- A plain Gradle project in `android/`, not a Bubblewrap scaffold. Bubblewrap needs Node at build time and F-Droid
  builds from a Gradle recipe; a project we can read builds the same way in both places. (Bubblewrap's licence is
  Apache-2.0, checked; what it generates is unverified.)
- The shell declares no Play Services, Firebase or Play Billing dependency. The library has optional Play Billing and
  location-delegation modules; the shell does not include them.
- **Needs a TWA-capable browser on the phone.** Chrome, Brave and Vivaldi support TWAs and notification delegation;
  Firefox, Edge and Samsung Internet support TWAs without delegation; others do not launch one at all
  ([browser support table](https://github.com/GoogleChrome/android-browser-helper/blob/main/docs/trusted-web-activity-browser-support.md),
  which its authors say they keep up to date; read today). A sideloaded browser that is not the user's default is
  downgraded to a Custom Tab (read from the library README). The shell sets the fallback to a Custom Tab, so a phone
  with no TWA browser still plays, with a browser bar.

## Push

**Web Push through the browser, in every channel.** The reminder sender, subscription table and `push.ts` do not
change. The browser owns the permission and the subscription; with delegation (Chrome, Brave, Vivaldi) the
notification can carry the app's identity (the Chromium architecture notes say permissions granted to the app shell
"can be delegated to the web origin", and that for a WebAPK Chrome hands notifications to the app to display; for a
TWA the notes do not describe push at all).

- **Unverified:** that a TWA's Web Push works end to end with no code in the shell, and what the delegation service
  must contain. I could not find the Chrome page that states it (`notification-delegation` was a 404). The first
  device test (step 3 below) is the proof; if it fails, the shell gains a `DelegationService` and nothing else.
- **Unverified:** what push transport each browser uses. Chrome's Web Push probably rides Google's services; that
  belongs to the browser, not to the APK, so it does not touch F-Droid's rule on the app's own dependencies.
- **Main F-Droid users on a phone with no Google services** need a browser whose Web Push works there. That is not
  a goal until the owner says it is. If it becomes one, add UnifiedPush (below) rather than FCM.

## Signing and the site's link to the app

- **Key:** one RSA keystore made once with `keytool`, with the release alias. It lives as a GitHub Actions secret
  (base64 keystore plus its passwords) and as an offline backup the owner holds. Losing it ends updates for every
  installed copy, because an Android update must be signed by the same key (Android's own rule, not fetched here).
- **`/.well-known/assetlinks.json`:** a static file served from the web app (`web/page.py`, as the manifest is),
  holding the `delegate_permission/common.handle_all_urls` relation, the package name and the key's SHA-256
  fingerprint ([Digital Asset Links](https://developers.google.com/digital-asset-links/v1/getting-started):
  location, relation and fields read there). Without it the TWA opens as a Custom Tab with a bar. The Google page does
  not say what content type or redirects it accepts; serve `application/json` and no redirect, and treat that as
  unverified until the device test.
- **Same key in every channel.** Main F-Droid normally signs its own build, which would give a different signature
  and make users reinstall to switch. It can instead publish our signed APK after rebuilding it and finding the
  two identical, pinned with `AllowedAPKSigningKeys`
  ([reproducible builds](https://f-droid.org/docs/Reproducible_Builds/)). So the build is reproducible from the
  start: pinned `build-tools` 34 (that page says `apksigner` from 35.0.0-rc1 on fails verification), a pinned JDK, a
  clean checkout of the tag, no timestamps in the output.

## Channels and updates

| Channel | How it updates | Needs |
|---|---|---|
| GitHub releases + [Obtainium](https://github.com/ImranR98/Obtainium) | Obtainium reads the releases page and notifies on a new release (read there). How it picks the APK among a release's files is not stated; ship exactly one `.apk`. | The release workflow signs and attaches the APK. |
| Own F-Droid repo | `fdroid update` over the APK folder, then `fdroid deploy` to static hosting; users add the repo URL in F-Droid's Manage Repos ([setup guide](https://f-droid.org/docs/Setup_an_F-Droid_App_Repo/)). The repo has its own index-signing key, apart from the app key. | A host for the folder, and that second key kept off the public machine. How users check the repo fingerprint is not covered by that page. |
| Main F-Droid | F-Droid rebuilds from a public source tag using a recipe in `fdroiddata`. | The recipe, and the points below. |

**Main F-Droid, what the sources say** ([inclusion policy](https://f-droid.org/docs/Inclusion_Policy/),
[anti-features](https://f-droid.org/docs/Anti-Features/)):
- The app must be FLOSS and built from public source with no proprietary build tools. The repo has a LICENSE.
- Proprietary tracking or advertising libraries are forbidden, and the policy names Google Play Services and Firebase.
  An app that fails to rebuild "such as requiring Play Services" is rejected. The shell uses none.
- **Unverified:** whether reviewers would tag the app `NonFreeNet` ("depend entirely on a proprietary network
  service": the service here is the owner's own server, which is free software) or `NonFreeDep` (it needs a browser
  that may not be free software). Ask F-Droid in the inclusion request before building the recipe.
- Metadata (name, summary, icons, changelog) goes in the recipe; the fields were not fetched.

## Steps, each its own PR

| # | Step | Needs from the owner |
|---|---|---|
| 1 | `android/` Gradle project: TWA launcher, Custom Tab fallback, debug APK in CI. Pins build tools and JDK. | Nothing. |
| 2 | `assetlinks.json` route and test, fingerprint from a config value. | The key's SHA-256 fingerprint, after step 4. |
| 3 | Device test: install the debug APK, check the bar is gone, subscribe, receive a reminder. Fixes the two unverified push and link points above. | A phone, and the name of the browser on it. |
| 4 | Generate the keystore; release workflow signs the APK and attaches it to a GitHub release on an `android-vMAJOR.MINOR.PATCH` tag (versionCode is `major*10000 + minor*100 + patch`), failing unless the signer matches `android/release-key.sha256`. | Run `keytool`, add the secrets, keep the backup. |
| 5 | Obtainium check: add the repo, install, publish a newer tag, see it update. | The phone again. |
| 6 | Own F-Droid repo: workflow builds the index and deploys it. | A hosting target and the repo key. |
| 7 | Main F-Droid: `fdroiddata` recipe, reproducibility check, inclusion request. | The owner's yes, and answers to the `NonFreeNet` and `NonFreeDep` questions. |

## Rejected, and why

- **A WebView shell.** It would carry its own cookie jar, service worker and web-push story, and Android WebView does
  not deliver Web Push to a page (unverified here; the reminders design needs a browser's push service). The TWA
  gives push for free. The library offers a WebView as a fallback only when no TWA browser exists; we use a Custom
  Tab instead, which keeps the browser's behaviour.
- **Native FCM.** It needs Google Play services in the app, which main F-Droid forbids by name, plus a Firebase project
  and a second sender beside Web Push. Web Push already does the job.
- **UnifiedPush (ntfy or another distributor) now.** It works without Google services
  ([distributors](https://unifiedpush.org/users/distributors/): ntfy, Sunup and others; whether each needs Google
  services is not stated there), but it needs a native receiver in the shell, a distributor installed on the phone
  and a second delivery path in the sender. Kept as the fallback if Web Push fails on a phone the owner cares about.
- **Bubblewrap-generated project.** Fine for a first try; not kept, for the build-reproducibility reason above.
- **A native rebuild of any screen.** No reason found: the shell shows the live site, so every feature ships as
  soon as the site does.
