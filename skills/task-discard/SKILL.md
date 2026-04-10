---
name: task-discard
description: Discard a task — cross off all remaining todos and mark report status as discarded. Use this skill whenever the user says "/task-discard", wants to abandon a task, cancel task tracking, or mark a task as no longer needed. Triggers on "discard task", "abandon task", "cancel task", "drop task", "task no longer needed".
---

# Task Discard

Mark a task as discarded — cross off remaining todos and update report status.

## Invocation

```
/task-discard <task-name>
```

The task name can be partial — match against existing task directory names.

## Workflow

### 1. Find and read the task

Locate the task directory and read all four files.

### 2. Update todo.md

- Strike through or cross off all remaining `[ ]` items using `[~]`:
  ```
  - [~] <item> — discarded YYYY-MM-DD
  ```
- Items already marked `[x]` stay as-is (work that was done is still done)
- Add at the bottom:

```markdown
---
**Discarded**: YYYY-MM-DD
**Reason**: <reason if provided by user, otherwise "Task no longer needed">
```

### 3. Update report.md

- Set status: `**Status**: Discarded`
- Update `**Last Updated**`: today's date
- Add `**Discarded**: YYYY-MM-DD`
- Add a brief note on why the task was discarded (if the user provided a reason)
- Preserve any existing findings — they may still be valuable

### 4. Update lesson.md

- Add an entry capturing why the task was discarded, if there's a useful lesson:
  - Was the approach wrong?
  - Did requirements change?
  - Was it superseded by another task?
- If no lesson, leave as-is

### 5. Confirm discard

Show:
- Task name and directory path
- Discard date
- Number of items that were completed vs discarded
- Any findings from the report that might still be useful

## Guidelines

- Don't delete the task directory — discarded tasks still have historical value
- Preserve all completed work and findings
- If the user doesn't give a reason, that's fine — just mark as discarded
- This is a soft close — the task can be revisited later if needed
