---
name: daily-ops
description: Blake's recurring personal operations: the Morning Brief, Snowcast, reminders, calendar events and other scheduled jobs. Use to run, change or add a recurring task or a reminder.
---

# Daily ops

1. **Existing jobs first.** The Morning Brief lives in `morning-brief/` (spec,
   style, renderer and contract C1). Change it there; C1 is frozen, so a shape
   change goes to the review queue.
2. **Scheduling.** Use the session's scheduled-task tools, not in-session cron.
   Run each job on the lowest tier that passes its check (Haiku or Sonnet).
3. **Phone.** Reminders and calendar events go through the phone app's
   calendar and reminder tools when they are available.
4. **Mail.** Read and summarise; drafts only. Sending is Blake's.
5. Needs the Mac, a signed-in browser or a secret: queue it in
   `.claude/handoff/QUEUE.md`. Don't hand it to Blake.
