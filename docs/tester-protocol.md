# Tester protocol

How a cold tester judges the open-work item "Teach the mix system where it is first needed", and any later lesson. One
tester at a time, fix between testers, stop by a rule written before the first one. The why, with sources, is
`docs/research/design-101.md` §1 ("watch newcomers in small rounds") and §3 proposals 1 and 4. Never the owner, who knows the
design, and a genre-literate player hides the gaps a newcomer hits.

## Before the first session

**Pass.** The tester reaches their first built mix and their first built rule without help, and, in the sheet, a
`first built mix` and a `first built rule` row that are not "none yet". A mix the tester built by accepting an offer
counts; one the observer built or talked them through does not.

**Stop.** Three testers in a row pass with no change to the game between them. A change to anything the lesson touches
resets the count to zero. Write the build id of each session beside its sheet.

**Who.** Someone who does not play idle or incremental games and has not seen this one. One screening question
("do you play games like Cookie Clicker or Universal Paperclips?") and a no is the only entry. Not a relative who has
heard the design explained.

## Running a session

1. Open the live site in a fresh browser profile, so the save is new. Afterwards take its save id from the newest
   row of `saves` (read-only). Start the screen recording with the tester's consent.
2. Say only: "Play as you would at home. Say what you are thinking if you can. I will not answer questions about how it
   works." Start the clock when they first see the page. Play 20 minutes, or until they stop.
3. **The observer stays silent.** No pointing, no "try the tab", no sighs. Write what they do, with the clock.
4. **When they ask for help,** answer "What would you try?" once. If they are still stuck, or ask a second time, mark
   the session as helped in the notes (clock time and what was on screen), give the smallest nudge that unblocks them,
   and carry on. A helped session does not pass. A tester stuck for five minutes with no input is also a note: ask what they
   were about to do, then proceed as for help.
5. At the end, ask in this order, writing the answers word for word:
   - Did you choose what the camp did?
   - Did it work?
   - Would you come back without being told?
   - What were you about to do? (also at any point they stop mid-action)

## The sheet

Print the mechanical rows with `app/tools/tester_sheet.py` (usage in its docstring: one read-only query, piped to the
tool) once the save has been left, then add the observer's.

| Row | Source |
|---|---|
| Time to first tap | mechanical: save start and the first `tap_card` in the decision log |
| First built mix, first built rule | mechanical: first `save_mix`, first `set_orders` with an order left standing |
| First idle gap over a minute | mechanical: wall times of the decision log |
| What was on screen then | proxy: the mix running and chips shown at the decision before the gap; the observer's note is the real row |
| Offers answered | mechanical: the save's mix dots touched, and the account's other offers (all its saves) |
| Offers shown, taken against declined | observer: not recorded |
| How each lesson ended (done or skipped, step, longest wait) | mechanical when the save's presentation holds `lesson_ends`; a lesson without one prints as not recorded |
| Last action before leaving | mechanical for the last decision; the leave itself is the observer's |
| Helped or not, and where | observer |
| The three questions and "what were you about to do?" | observer |

A row with no recorded source prints `— not recorded (observer notes)`, never 0 or empty: the observer fills it from
the recording. The decision log is deleted past 30 days, so print the sheet the same day. The leave beacon, the
`lesson.end` log line and the Umami events carry no save id, so a sheet cannot read them.

## Reporting

Say what the rounds can rule out, not that something is verified: after three clean testers, "no problem hitting more
than about half of testers"; after ten, "more than about one in seven". Name what was seen (a step, a count of testers)
and list the changes made between testers. Survey ratings and "I liked it" decide nothing at this size. Take the problem
they hit and discard the fix they propose.

## The gapped variant

For repeat offers and the return screen. Two or three cold testers each play two short sittings a few hours apart, the
second opened from the return screen, not a new game. Read the sheet for both, and from the decision log and the
recording: do the repeat offers appear and get taken after the return, and what is the first thing the tester does? The
pass and stop rules are the same, and so is the silence. It is the only instrument that sees a return before the public
build. Its result feeds "The night visits go quiet" in `docs/open-work.md`.
