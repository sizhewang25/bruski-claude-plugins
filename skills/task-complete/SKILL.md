---
name: task-complete
description: Mark a task as complete — check off all remaining todos, set report status to complete, and add completion timestamps. Use this skill whenever the user says "/task-complete", wants to finish a task, close out task tracking, or mark a task as done. Triggers on "complete task", "finish task", "close task", "task is done", "wrap up task".
---

# Task Complete

Mark a task as complete by finalizing all documentation files with completion status and timestamps.

## Invocation

```
/task-complete <task-name>
```

The task name can be partial — match against existing task directory names.

## Workflow

### 1. Find and read the task

Locate the task directory and read all four files to understand current state.

### 2. Review before completing

Before marking complete, check:
- Are there unchecked todo items that weren't actually done? Flag them to the user.
- Is the report missing key findings or conclusions? Note what's missing.
- If everything looks good, proceed.

### 3. Update todo.md

- Mark any remaining `[ ]` items as `[x]` with today's date
- If items were skipped (not done but no longer needed), mark them with `[~]` and note why
- Add a completion summary at the bottom:

```markdown
---
**Completed**: YYYY-MM-DD
```

### 4. Update report.md

- Set status to Complete: `**Status**: Complete`
- Update `**Last Updated**`: today's date
- Add `**Completed**: YYYY-MM-DD`
- Ensure the Conclusions section has content — if empty, draft conclusions based on the findings documented in the report
- Add a final summary if the report has been built up incrementally

### 5. Update lesson.md

- Add any final lessons from the completion process
- If no new lessons, leave as-is

### 6. Confirm completion

Show:
- Task name and directory path
- Completion date
- Brief summary of what was accomplished (from report)
- Any items that were marked as skipped rather than done

## Guidelines

- Don't silently skip incomplete items — ask the user if they should be marked done or skipped
- The completion timestamp should be consistent across all files
- If the report has no substantive content, warn the user before completing
