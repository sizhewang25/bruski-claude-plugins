---
name: task-read
description: Load a task's full context (plan, todo, report, lesson) so you can resume work on it. Use this skill whenever the user says "/task-read", "resume task", "continue task", "pick up task", "load task", "where was I on task X", "get back to task", or wants to continue working on a previously tracked task. Also triggers on "what's left on task X" or "show me the task status for X".
---

# Task Read

Load a task's documentation into context so work can resume seamlessly. The goal is to reconstruct the full picture — what was planned, what's done, what's left, and what lessons have been learned — so you can pick up exactly where things left off.

## Invocation

```
/task-read <task-name>
```

The task name can be partial — match against existing task directory names. For example, `fast-switch` matches `20260309-fast-switch-analysis`.

## Workflow

### 1. Find the task

Search for task directories matching the name. Look in:
- `tasks/` at repo root
- `scripts/*/tasks/`
- `scripts/*/*/tasks/`
- Any other `tasks/` directories in the project

If multiple matches are found, list them and ask the user to pick one. If no match, say so.

### 2. Read all four files

Read the task's documentation files in this order (each may or may not exist):

1. **plan.md** — Background, goals, data locations, approach
2. **todo.md** — What's been done and what remains
3. **report.md** — Findings, results, verification so far
4. **lesson.md** — Gotchas and corrections discovered along the way

### 3. Present a resume briefing

After reading, present a concise briefing to the user. This is the critical part — it should feel like a teammate handing off context at shift change. Structure it as:

```markdown
## Task: <full task name>
**Location**: <path to task directory>
**Status**: <Pending | Completed | Discarded>

### Where things stand
<1-3 sentences summarizing current state — what's been accomplished, key findings so far>

### Remaining work
<Bulleted list of unchecked items from todo.md, grouped by phase if applicable>

### Key context to keep in mind
<Important caveats, lessons, or domain knowledge from lesson.md and plan.md that someone resuming this work needs to know — things that aren't obvious from the code>
```

If the task is completed or discarded, adjust the briefing accordingly — focus on summarizing what was done and the conclusions rather than remaining work.

### 4. Ready to work

After the briefing, you're primed to continue the task. The user can immediately give instructions like "pick up from phase 3" or "finish the remaining items" and you'll have the full context needed to proceed.

When the user gives follow-up instructions, use the task management skills naturally:
- Update `todo.md` as items are completed (mark with `[x]` and date)
- Add findings to `report.md`
- Capture any new lessons in `lesson.md`

## Edge cases

- If only some files exist (e.g., just `todo.md`), work with what's available — don't complain about missing files
- If the task directory is empty or has no markdown files, tell the user
- If the task name matches multiple directories, show all matches with their dates and paths so the user can disambiguate
