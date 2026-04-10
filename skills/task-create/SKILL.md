---
name: task-create
description: Create a new task directory with plan.md, todo.md, report.md, and lesson.md. Use this skill whenever the user says "/task-create", wants to start a new task, begin tracking a piece of work, or set up task documentation. Triggers on phrases like "create a task", "new task", "start task", "set up task tracking", or any mention of creating plan/todo/report/lesson files for a project task.
---

# Task Create

Create a new task directory with structured documentation files (plan.md, todo.md, report.md, lesson.md) based on user-provided context.

## Invocation

```
/task-create <task-name> [context...]
```

The first argument is the task name (kebab-case). Everything after is context — could be a description, requirements, paste from a conversation, links to files, or any background information.

## Workflow

### 1. Determine the tasks folder

Look for an existing `tasks/` directory in the project. Common locations:
- `tasks/` at the repo root
- `scripts/<project>/tasks/` (e.g., `scripts/cross_us_trip_202508/tasks/`)

If multiple exist, pick the one most relevant to the current work context. If none exist, create `tasks/` at the repo root.

### 2. Create the task directory

Name format: `YYYYMMDD-<task-name>` using today's date.

Example: `tasks/20260314-optimize-query-performance`

### 3. Analyze the provided context

Read and understand the context the user provided. This could be:
- A plain text description of the goal
- Pasted error logs or bug reports
- File paths to examine
- Requirements or specifications
- Conversation history about what needs to be done

Use this context to populate all four files intelligently — don't just echo it back.

### 4. Create the four files

#### plan.md

```markdown
# <Task Title> — Plan

## Background

<Why this task exists. What problem it solves or what goal it advances.>

## Context

<Relevant technical details, data locations, dependencies, related systems.>

## Goals

<Specific, measurable outcomes this task should achieve.>

## Approach

<High-level strategy for accomplishing the goals.>

## Caveats

<Known risks, edge cases, or constraints to be aware of.>
```

#### todo.md

```markdown
# <Task Title> — Todo

## Phase 0: Setup & Discovery
- [ ] <task item>
- [ ] <task item>

## Phase 1: Implementation
- [ ] <task item>
- [ ] <task item>

## Phase 2: Verification
- [ ] <task item>
- [ ] <task item>
```

Break work into logical phases. Each item should be specific and actionable. Don't over-decompose — 3-8 items per phase is typical.

#### report.md

```markdown
# <Task Title> — Report

**Status**: In Progress
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Summary

<To be filled as work progresses.>

## Findings

<Results, data, observations as they emerge.>

## Conclusions

<Final assessment when task completes.>
```

#### lesson.md

```markdown
# <Task Title> — Lessons

## YYYY-MM-DD

<Lessons will be captured here as corrections and discoveries occur during the task.>
```

### 5. Confirm to the user

After creating all files, show:
- The full path to the task directory
- A brief summary of the plan
- The todo items organized by phase
- Any questions or ambiguities that need clarification before starting

## Guidelines

- Populate files with real content derived from the context, not placeholder text
- If the context is thin, still create the structure but note what needs clarification in plan.md
- Use the project's existing naming patterns (check sibling task directories for style)
- Mark todo items with `[ ]` (unchecked) — never pre-check items
- Keep the plan focused — this is a working document, not a dissertation
