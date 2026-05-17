---
name: manage-inbox-notes
description: Process and distribute all notes in the Obsidian vault's 00 Inbox/ folder. Reads vault rules from README.md and AGENTS.md, then classifies each inbox note (diary, block, component, or output), enriches it with proper frontmatter and wiki links to related existing notes, and moves it to the correct vault location. Invoke this skill whenever the user asks to process, manage, triage, clean up, or distribute inbox notes — or whenever they want to push captures into the knowledge base.
---

# manage-inbox-notes

Process every file in `00 Inbox/` and distribute them into the correct vault locations, following the vault's own rules.

## Step 1: Orient

Read these three files from the vault root before doing anything else:

- `README.md` — vault structure, conventions, and the monthly gardening routine
- `AGENTS.md` — agent-specific rules for classification, frontmatter, tags, and naming
- `20 Outputs/Templates/Block.md` — the required block frontmatter template

If any of these is missing, stop and tell the user.

Also list the current contents of `10 Knowledge/Blocks/` and `10 Knowledge/Components/` (filenames only) so you know what already exists for linking.

## Step 2: Survey the Inbox

List all `.md` files in `00 Inbox/`. Read each one. Build a working list of notes with their content and a preliminary classification.

Classify each note into one of three groups:

- **Process**: has body content, or has reference links in frontmatter (`Sources` URLs, `Theme / Questions` wiki links, `Similar`, `Leads to`, etc.) even if the body is empty — these belong in the knowledge base.
- **Skip and flag**: body is empty AND all frontmatter link fields are empty lists — no content and no references. List them in the final report.
- **Conflict check**: before moving any note, verify no file with the same name exists at the destination.

## Step 3: Classify Each Note

Assign each note to exactly one destination:

| Class | Destination | When to use |
|---|---|---|
| `diary` | `01 Daily/` | Date-named files (`YYYY-MM-DD*.md`) or notes with `tags: [diary]` |
| `block` | `10 Knowledge/Blocks/` | Single atomic concept — a term, tool, definition, claim, observation, short example, or API. Explains one thing. |
| `component` | `10 Knowledge/Components/` | Integrates multiple blocks — an overview, framework, survey section, map of related ideas, project knowledge, or personal system. |
| `output` | `20 Outputs/[subfolder]/` | Deliverable — report, summary, proposal, essay, brief. Use the most fitting subfolder from AGENTS.md. |

**When in doubt, classify as a block.** Promote to component only if the note already links to or describes multiple distinct concepts working together.

A note that is long but still focused on a single subject is still a block.

## Step 4: Enrich Each Note Before Moving

### Diary notes
No changes needed. Move as-is.

### Blocks
Ensure the frontmatter is complete and correct. The required format is:

```yaml
---
Time: YYYY-MM-DD ddd
aliases: []
tags:
  - block
Sources: []
Similar: []
Opposite: []
Theme / Questions: []
Leads to: []
---
```

Rules:
- Use the existing `Time` value if present; otherwise use today's date in `YYYY-MM-DD ddd` format (e.g. `2026-05-17 Sun`). Do not include a time component.
- All fields except `Time` must be YAML lists. Use `[]` when empty, inline or block lists otherwise.
- Do not add topical tags. Only `block` belongs in `tags`.
- Fill in relationship fields when you can infer them confidently from the note's content:
  - `Similar`: other blocks with closely related meaning
  - `Opposite`: blocks that contrast with this one
  - `Theme / Questions`: the broader question or theme this note contributes to
  - `Leads to`: natural follow-on concepts
  - Use `[[WikiLink]]` format for all values in these fields.
- Add a `# Title` heading if the note has no heading.
- If the body is a single sparse sentence or a bare list with no context, add a short one-paragraph explanation. Do not fabricate facts — only clarify what is clearly implied by the existing content.

### Components
Ensure the component has a clear structure:

```markdown
# Title

Short explanation of the integrated concept.

## Core Blocks
- [[Block One]]
- [[Block Two]]

## Explanation

Integrated understanding.

## Use Cases

Where this is useful.
```

Link to relevant existing blocks from `10 Knowledge/Blocks/` in the `## Core Blocks` section.

### Outputs
Ensure the output has a `# Title`, a `## Summary` section, and a `## Source Notes` section that links to relevant blocks and components.

Choose the right subfolder based on the content:
- `20 Outputs/Personal Growth/` — learning plans, reflections, personal systems
- `20 Outputs/Academy/` — academic work, course outputs, paper notes
- `20 Outputs/Books/` — book summaries, reading outputs
- `20 Outputs/Drafts/` — anything still being shaped that doesn't fit elsewhere

## Step 5: Add Wiki Links

For every note (all classes), scan the body text for mentions of concepts that match existing notes in `10 Knowledge/Blocks/` or `10 Knowledge/Components/`. Add `[[WikiLink]]` on the first meaningful mention of each matched concept.

Rules:
- Only link to notes that actually exist in the knowledge base.
- Do not link every occurrence — only the first meaningful mention per section.
- Do not create links for passing references or one-off phrases.
- Prefer specific notes over broad hub notes.
- For acronyms, link to the canonical expanded form if that note exists.

## Step 6: Move Each Note

After enriching, move each file to its destination using `mv` via Bash. Use the original filename — do not rename unless the AGENTS.md naming rules are clearly violated (e.g., all-lowercase where a proper noun is expected).

If a file with the same name already exists at the destination, do not overwrite — flag it in the report and leave the inbox file in place.

## Step 7: Report

After processing all files, print a concise report grouped by destination:

```
### Moved to 01 Daily/ (N)
- filename.md

### Moved to 10 Knowledge/Blocks/ (N)
- filename.md — [one-line description of what was enriched]
- ...

### Moved to 10 Knowledge/Components/ (N)
- filename.md — [one-line description]

### Moved to 20 Outputs/... (N)
- filename.md → subfolder/

### Skipped — empty stubs (N)
- filename.md

### Skipped — destination conflict (N)
- filename.md — already exists at [path]
```

Keep the report factual and brief. The user should be able to scan it quickly.

## Step 8: Clean Up the Inbox

After the report, list any files still remaining in `00 Inbox/` and ask the user whether to delete them. If the user confirms, delete all remaining inbox files with `rm`.

## Key Constraints

- Never invent facts. Only reorganize, link, and lightly expand what is already present.
- Never create topical tags. Only `diary`, `block`, and `component` are valid tags.
- Never use deep nesting beyond the established vault structure.
- Never overwrite an existing file without user confirmation.
- Preserve existing filenames unless they violate naming rules.
- Do not touch notes already in `10 Knowledge/` or `20 Outputs/` — only process `00 Inbox/`.
