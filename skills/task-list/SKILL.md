---
name: task-list
description: List and browse all tasks across the project. Searches tasks/ folders at the root and all subfolders, groups by status (pending/completed/discarded), sorted by date descending. Supports filters, wildcards, and per-group limits. Use this skill whenever the user says "/task-list", "show tasks", "list tasks", "what tasks do I have", "task status", "my tasks", "pending tasks", "show completed tasks", or any request to see an overview of tracked tasks.
---

# Task List

Scan the project for task directories and present a grouped, filterable summary.

## Invocation

```
/task-list [filter] [limits]
```

**Examples:**
```
/task-list                           # defaults
/task-list *switch*                  # wildcard filter on task name
/task-list filter by starlink        # keyword filter
/task-list pending:10 completed:5    # custom limits per group
/task-list *refactor* pending:20     # combine filter + limits
```

## How to find tasks

Search for `tasks/` directories at the repository root and recursively within all subdirectories. A valid task directory:

1. Lives inside a `tasks/` parent folder
2. Has a name starting with a date prefix like `YYYYMMDD-` (e.g., `20260309-fast-switch-analysis`)
3. Contains at least one of: `plan.md`, `todo.md`, `report.md`, `lesson.md`

Use `find` or glob patterns to locate all matching directories. Common locations include:
- `tasks/`
- `scripts/*/tasks/`
- `scripts/*/*/tasks/`

## How to determine task status

Read each task's files to classify its status:

### Completed
- `report.md` contains `**Status**: Complete` or `**Status**: Completed`
- OR `todo.md` has all items checked (`[x]`) with none remaining (`[ ]`)

### Discarded
- `report.md` contains `**Status**: Discarded`
- OR `todo.md` contains `**Discarded**:` marker
- OR `todo.md` has items marked with `[~]`

### Pending (default)
- Everything else — tasks with unchecked items remaining, or newly created tasks

## Sorting

Sort tasks within each group by the date prefix in **descending** order (newest first). The date is extracted from the folder name: `YYYYMMDD-task-name` → `YYYYMMDD`.

## Default display limits

| Group | Default limit |
|-------|--------------|
| Pending | 5 |
| Completed | 2 |
| Discarded | 0 (hidden) |

The user can override any limit with `group:N` syntax (e.g., `pending:20`, `completed:10`, `discarded:5`). A limit of `0` means the group header is shown with a count but no individual items listed.

## Filtering

Filters narrow the task list before grouping:

- **Wildcards**: `*keyword*` matches against the full directory name (e.g., `*switch*` matches `20260309-fast-switch-analysis`)
- **Keyword filter**: `filter by keyword` does a case-insensitive substring match on the directory name
- Multiple filter terms are ANDed together

## Output format

Present the results as a clean markdown summary. The goal is a quick at-a-glance dashboard — enough to orient the user without overwhelming them.

```markdown
# Tasks

## Pending (N total, showing M)
| Date | Task | Location | Progress |
|------|------|----------|----------|
| 2026-03-09 | fast-switch-analysis | scripts/cross_us_trip_202508/tasks/ | 23/25 done |
| 2026-02-23 | augment-network-kpis | scripts/cross_us_trip_202508/tasks/ | 0/8 done |

## Completed (N total, showing M)
| Date | Task | Location | Completed |
|------|------|----------|-----------|
| 2026-03-01 | data-cleanup | tasks/ | 2026-03-05 |

## Discarded (N total)
_(showing 0 — use `discarded:N` to expand)_
```

### Progress column

For pending tasks, count checked `[x]` vs total checkbox items in `todo.md` to show `X/Y done`. If no `todo.md` exists, show `—`.

### Completed date

For completed tasks, extract the completion date from `report.md` (look for `**Completed**:` or `**Last Updated**:`) or from the latest `[x]` date stamp in `todo.md`.

### Location column

Show the relative path from the repo root to the `tasks/` parent directory (not the full path to the task itself). This helps when tasks live in different parts of the project.

## Edge cases

- If no tasks are found anywhere, say so clearly: "No task directories found in this project."
- If a task directory exists but has no markdown files, skip it silently
- If `todo.md` has no checkboxes, treat progress as `—`
- Dates that can't be parsed from folder names: sort them last, show the raw folder name
