---
name: md-to-pdf
description: Convert Markdown files into polished, print-ready PDFs on macOS using headless Google Chrome. Output has syntax-highlighted code, styled tables, clickable in-document links and smart page breaks, and renders GitHub-flavoured Markdown faithfully. Use this skill whenever the user wants a PDF of a .md file — a README, notes, cheatsheet, handout, guide, report or docs folder — including phrasings like "make a PDF of this", "export to PDF", "printable version", "handout for students" or "generate a PDF aside it", even if they don't say "Markdown". Requires macOS and Google Chrome.
compatibility: macOS only. Requires Google Chrome (in /Applications or ~/Applications, or set CHROME) and python3 >= 3.9. The first run needs network access to pip-install pinned packages into a private cache.
---

# md-to-pdf

The bundled script `scripts/md_to_pdf.py` (in this skill's base directory) runs this pipeline:

```
Markdown ──Python-Markdown + Pygments──► HTML with print CSS ──headless Chrome──► PDF
```

It produces a clean document style: dark-blue headings, gray code boxes, bordered tables, 10 pt body, Letter or A4. The print CSS keeps code blocks, tables and images in one piece, keeps headings with the content that follows, and keeps an intro line with the code or table under it.

## Prerequisites

- **macOS** and **Google Chrome**. If either is missing, the script exits with code 2 and a clear message. Don't try to work around it with another engine; tell the user what's missing.
- **python3 >= 3.9.** The script creates its own virtualenv under `~/Library/Caches/md-to-pdf/` on first run, with pinned versions of Markdown, Pygments, pymdown-extensions, mdx_truly_sane_lists, pypdfium2 and Pillow. That first run needs network access and takes about 10 seconds. Later runs reuse the cache, and the system Python is never touched.

## Workflow

1. **Convert, with a preview.** Put the preview images somewhere temporary, such as your scratchpad or `/tmp`, not next to the user's files:
   ```bash
   python3 <skill-dir>/scripts/md_to_pdf.py path/to/doc.md --preview /tmp/doc-preview
   ```
   By default the PDF is written next to the input as `doc.pdf`; use `-o` to change that. The script prints the output path, the page count and the detected list indentation.

2. **Look at the result before reporting success.** Read `contact.png` (every page side by side) and open a full page or two (`page-NN.png`) wherever something looks off. Rendering problems never show up as errors, so checking the images is how you catch them. Look for:
   - nested bullets that came out flat, or a list merged into the paragraph above it;
   - a code block, table or image split across pages, or an intro line stranded at the bottom of a page;
   - images shown as a broken icon (the script also prints `warning: image not found`);
   - code lines running past the right edge, or misaligned ASCII diagrams;
   - empty-looking pages. A mostly empty page is usually fine: it means a large unbreakable block moved to the next page.

3. **Fix with options first, and the Markdown source last.**
   - Lists flattened or nested wrongly: pass `--list-indent 2` or `--list-indent 4`. Auto-detection picks 4 only when every nested item in the file uses 4 or more spaces.
   - Style tweaks: write a small CSS file and pass `--css` (recipes below).
   - Only edit the user's Markdown when the source itself is broken (for example a missing closing code fence). Say what you changed. The `.md` is usually their source of truth, and GitHub must still render it.

4. **Report** the PDF path and page count, and mention any warnings or known limits that affected this document. If the PDF lives in a git repo, remember it's generated from the `.md`: regenerate it after edits to the `.md` and commit both together.

## Options

| Option | Effect |
|---|---|
| `-o OUT.pdf` | Output path (default: input path with `.pdf`). Its directory must already exist. |
| `--paper letter\|a4` | Page size (default `letter`). Use `a4` for European or Asian audiences when the user hasn't said. |
| `--page-numbers` | Adds "N / total" at the bottom right of each page. |
| `--css FILE` | Extra CSS appended after the built-in style, so its rules win. |
| `--title TEXT` | PDF title metadata (default: first H1, else the file name). |
| `--list-indent auto\|2\|4` | Spaces per nested-list level (default `auto`). |
| `--preview DIR` | Also writes `page-NN.png` for each page plus `contact.png`. |
| `--keep-html PATH` | Saves the intermediate HTML, for debugging layout with CSS. |

Exit codes: `0` success, `1` Chrome failed or timed out, `2` environment problem (not macOS, no Chrome, Python too old, dependency install failed), `3` bad input (missing file, missing output directory, output path equal to input).

The PDF is written only after Chrome succeeds, so a failed run never replaces an existing PDF.

## What it handles

- **GitHub-style Markdown:**
  - tables, fenced code with highlighting, and code blocks nested inside list items;
  - lists nested by 2 or 4 spaces;
  - a list or table right after a paragraph line, with no blank line;
  - task lists, `~~strikethrough~~`, autolinks, footnotes, definition lists.
- **Heading anchors** are generated the same way as GitHub's, including non-ASCII headings, so `[see](#some-heading)` links work inside the PDF.
- **`<details>` blocks** are printed expanded, with the Markdown inside rendered.
- **Relative images** resolve against the Markdown file's folder, including paths with spaces or `%20`.
- **CJK text** renders with PingFang or Hiragino.
- **Chrome isolation:** each run uses a throwaway Chrome profile. It works while the user's Chrome is open, and several conversions can run in parallel.

## Known limits

Tell the user if their document depends on any of these:
- **No Mermaid diagrams or LaTeX math.** They print as code or plain text.
- **No emoji shortcodes:** `:smile:` stays literal, though actual emoji characters render.
- **Remote images** (`https://…`) need network access at conversion time. Chrome waits up to 10 seconds for them.
- **Duplicate heading names** get `_1`, `_2` anchors, whereas GitHub uses `-1`, `-2`. Links to the second and later copies need adjusting.
- **Raw HTML** passes through as is. Anything relying on JavaScript, or on `iframe`/`video`, won't print usefully.

## CSS recipes for `--css`

```css
/* Larger body text */
body { font-size: 11pt; }

/* Start every H2 section on a new page */
h2 { break-before: page; }
h1 + h2 { break-before: auto; }   /* but not the first one, right after the title */

/* Different accent color */
h1, h2 { color: #8a1c1c; }  h2 { border-bottom-color: #e8c4c4; }

/* Wider margins */
@page { margin: 20mm; }

/* Allow long code blocks to split across pages (default keeps each block whole) */
.hl, pre { break-inside: auto; }
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Google Chrome not found` | Install Chrome, or set `CHROME=/path/to/Google Chrome` (the binary inside the `.app` bundle). |
| `dependency install failed` | Usually there's no network on the first run. Retry once online. Delete `~/Library/Caches/md-to-pdf/` to force a clean reinstall. |
| `Chrome did not finish within 180s` | Usually a remote image that never loads. Try without the remote images, or use local copies. |
| A warning that Chrome is older than 105 | Update Chrome. Older versions ignore the keep-together rules, so intro lines can get separated from their code. |
| Layout needs investigating | Use `--keep-html out.html` and inspect the HTML. The CSS is in its `<style>` tag. |
