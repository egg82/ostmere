# Drift judge

The readout reports (`sim-invariants.md`) stop a rhythm changing unseen, but each change is committed one
pull request at a time, so slow movement across many commits passes. After a merge that changes a readout, a fresh
Claude Code subagent compares the cumulative movement since the build the owner last played against the owner's direction. It is
advice: no verdict gates a pipeline, and nothing in CI calls a model.

## Fit pass

- **What it is an instance of:** a post-merge reader of the simulator's readouts. The readouts and their snapshots
  already are the instrument; this adds a reader for the history they leave in git.
- **Systems row:** none. `systems.md`'s "Writer" row is Claude writing the game's lines at runtime; this is a tool with
  one caller, no second implementation and no game state, so it fails the four-part test. It lives in
  `app/tools/drift_judge/`, a plain package beside the other tools.
- **How games and services solve it:** a nightly regression digest is the usual shape (rejected below); the one worth
  borrowing is a baseline that a person moves (`ANCHOR`), as a snapshot test moves its approved text.

## Decisions

- **Code gathers, a session judges.** `python -m tools.drift_judge --brief [BEFORE_SHA]`, run from `app/` with
  `PYTHONPATH=.`, prints one self-contained brief: the instructions, `direction.md` (the pacing direction from `decisions.md`),
  the commit subjects since `app/tests/readouts/ANCHOR`, the cumulative readout diff since it and the diff of the merge
  just landed (`BEFORE_SHA` is main's tip before the merge; default HEAD's parent). A diff or subject list over its size
  limit is cut with a count of what was omitted, so the reader knows it is partial. With no readout change since
  `ANCHOR` it prints one line saying there is nothing to judge, and exits 0.
- **Who runs it:** the session that merges a pull request which changed `app/tests/readouts/`, with main's tip before
  the merge as `BEFORE_SHA`. The session starts a fresh subagent with the brief as its prompt; the subagent has no stake in the
  change it reads.
- **What happens to a verdict:** nothing is filed. On `fine` the session does nothing. On `drift` it first looks for the
  cause in what it just landed, and when the cause is a mechanical side effect it fixes it there, as a follow-up pull
  request. Only when the drift is a taste call that only the owner can make does the session put one question in its report to
  the owner, with a recommendation. Beats are named by id, never by what happens (`CLAUDE.md`, "Never spoil the owner"); the brief
  says so, and no filter reads the question's wording.
- **Moving the baseline:** whichever session receives the owner's play feedback writes the sha of the build that was played into
  `ANCHOR`. Moving `ANCHOR` alone changes no readout, so it prompts no run.

## Rejected, and why

- **A CI job with an API caller.** Keys, a token and CI machinery for advice a session can give on the
  subscription. It needed an API key, a project access token to file issues (`CI_JOB_TOKEN` cannot create them), and a
  controls script to check the model.
- **A judge that gates CI.** A model's verdict varies between runs, so a red judge would be re-run until green.
- **A weekly digest.** Nobody reads it; a question that is asked only when something moved gets read.
- **Filing an issue or a pull request comment.** The session that landed the change is the one placed to fix it, and
  a taste question reaches the owner in the report the owner already reads.
- **Asking the model per commit.** The cost is in the cumulative reading; the per-merge diff is only the trigger and
  the cause.
- **A regex or keyword scan of the question for spoilers.** Behaviour gated on words in prose misfires; the safety is
  the inputs and the instruction.
