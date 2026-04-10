---
name: task-update
description: Update an existing task's plan.md, todo.md, report.md, and/or lesson.md files with new progress, findings, or corrections. Use this skill whenever the user says "/task-update", wants to record progress on a task, update task documentation, log findings, mark items done, or capture lessons learned. Triggers on phrases like "update task", "log progress", "record findings", "mark done", "add lesson".
---

# Task Update

Update an existing task's documentation files based on new information, progress, or corrections.

## Invocation

```
/task-update <task-name> [update content...]
```

The task name can be partial — match against existing task directory names. The update content describes what changed, what was discovered, or what progress was made.

## Workflow

### 1. Find the task directory

Search for a task directory matching the provided name. Match flexibly:
- Exact match: `20260314-optimize-query`
- Partial match: `optimize-query` → finds `20260314-optimize-query`
- If ambiguous, list matches and ask the user to pick

### 2. Read all four files

Read plan.md, todo.md, report.md, and lesson.md to understand current state.

### 3. Analyze the update content

Determine what type of update this is:
- **Progress**: Items completed, phases advanced → update todo.md and report.md
- **Discovery**: New information, data, observations → update report.md and possibly plan.md
- **Correction**: Something was wrong or needs adjustment → update lesson.md and plan.md
- **Scope change**: Goals or approach changed → update plan.md and todo.md

### 4. Apply updates to the relevant files

#### todo.md updates
- Mark completed items: `- [ ]` → `- [x] <item> — YYYY-MM-DD`
- Add new items if scope expanded
- Add summary notes under completed phases (statistics, key results)

#### report.md updates
- Add new sections with date headers for findings
- Include data tables, statistics, file paths as appropriate
- Update the "Last Updated" date
- Keep previous content — append, don't overwrite

#### plan.md updates
- Update approach if strategy changed
- Add new caveats discovered during work
- Revise goals if scope shifted
- Keep original context intact

#### lesson.md updates
- Add entries under today's date header
- Categorize by topic (e.g., "Data handling", "Domain understanding", "Tooling")
- Include both the lesson and why it matters
- Capture corrections from the user verbatim — these are gold

### 5. Confirm changes

Summarize what was updated across which files. Keep it brief — the user can read the files.

## Guidelines

- Always include date stamps on completed todo items: `— YYYY-MM-DD`
- Append to report.md chronologically — don't reorganize previous entries
- Lesson entries should be actionable, not just observations
- If the update reveals the plan needs significant revision, flag it explicitly
- When marking multiple todos done, include brief result summaries as sub-bullets
