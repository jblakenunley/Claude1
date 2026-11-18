---
description: Work the Claude Code handoff queue on Blake's Mac — the items cloud sessions could not do.
---

You are Claude Code on J Blake Nunley's Mac, in his `claude1` repo. Work the handoff
queue in `.claude/handoff/QUEUE.md`. Read `/CLAUDE.md` first; its root rule governs.

1. `git pull` on main. Read the queue's Open table.
2. **Prerequisites first.** Items 1 and 2 (GitHub CLI signed in with workflow scope;
   Claude in Chrome connected) unblock most others. If either is open, do it first.
3. **Ask once, together.** Collect every point in the open items that is genuinely
   Blake's — a sign-in prompt only he can approve, a key only he holds, a choice only he
   can make (the `choice` items) — and ask for all of them in one message before starting.
   Ask for nothing else. Never hand him a step you can run yourself.
4. Work the rest top-down. For each item: do it, verify the "Done when" condition with
   real output, then move the row to Done with the date, `Claude Code`, and a one-line result
   naming the evidence. If an item cannot finish, leave it open, add one line under it saying
   what was tried and what blocks it, and move on.
5. Secrets go to the macOS keychain or GitHub secrets, never to a file, a commit, the queue
   or the chat transcript. Private details go to the private Drive folder
   "Chablis Data (private)", never to this public repo.
6. Commit the queue with `handoff: <items done>` and push.
7. Report in five lines or fewer: items done, items still open and why, and anything new
   that should be queued.

**Adding items (any session).** When a step needs the Mac, a browser signed in as Blake,
GitHub settings or secrets, local files, or an unrestricted network: append a row to Open
with the next number, today's date, the project it came from, its needs, the task in
public-safe words, and a verifiable "Done when". Then carry on with everything else. Do not
ask Blake to do the step.
