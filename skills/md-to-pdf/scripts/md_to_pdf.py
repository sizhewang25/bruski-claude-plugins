#!/usr/bin/env python3
"""Convert a Markdown file to a styled, print-ready PDF.

Pipeline: Markdown --(Python-Markdown + Pygments)--> HTML --(headless Google Chrome)--> PDF

Prerequisites: macOS, Google Chrome, python3 >= 3.9. The Python packages are
installed on first run into a private virtualenv under ~/Library/Caches/md-to-pdf/
(override with MD_TO_PDF_CACHE), so nothing touches the system Python.

Usage:
    md_to_pdf.py INPUT.md [-o OUTPUT.pdf] [--paper letter|a4] [--page-numbers]
                 [--css EXTRA.css] [--title TITLE] [--list-indent auto|2|4]
                 [--preview DIR] [--keep-html PATH]

Exit codes: 0 success, 1 conversion failed, 2 environment problem (not macOS,
no Chrome, Python too old, dependency install failed), 3 bad input.
"""

import argparse
import hashlib
import html
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

REQUIREMENTS = [
    "Markdown==3.9",
    "Pygments==2.21.0",
    "pymdown-extensions==10.21.3",
    "mdx_truly_sane_lists==1.3",
    "pypdfium2==5.15.2",   # page count + --preview rendering
    "pillow==11.3.0",      # --preview contact sheet
]
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
CHROME_TIMEOUT_S = 180
MIN_CHROME_MAJOR = 105  # CSS :has(), used to keep intro lines with their code/table


def die(code, msg):
    print(f"md_to_pdf: {msg}", file=sys.stderr)
    sys.exit(code)


# --------------------------------------------------------------------------- environment

def check_platform():
    if platform.system() != "Darwin":
        die(2, f"this tool supports macOS only (detected {platform.system()}).")
    if sys.version_info < (3, 9):
        die(2, f"python3 >= 3.9 required (running {platform.python_version()}).")


def venv_dir():
    base = Path(os.environ.get("MD_TO_PDF_CACHE", "~/Library/Caches/md-to-pdf")).expanduser()
    tag = hashlib.sha256("\n".join(REQUIREMENTS).encode()).hexdigest()[:10]
    return base / f"venv-py{sys.version_info[0]}{sys.version_info[1]}-{tag}"


def ensure_venv_and_reexec():
    """Re-run this script inside a private venv with pinned dependencies."""
    venv = venv_dir()
    if Path(sys.prefix).resolve() == venv.resolve():
        return
    py = venv / "bin" / "python"
    # `.complete` is written only after a successful install, so an interrupted
    # first run is detected and rebuilt from scratch next time.
    if not (venv / ".complete").exists():
        print(f"md_to_pdf: first run, installing dependencies into {venv} ...", file=sys.stderr)
        shutil.rmtree(venv, ignore_errors=True)
        venv.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
            subprocess.run([str(py), "-m", "pip", "install", "--quiet",
                            "--disable-pip-version-check", *REQUIREMENTS], check=True)
        except (subprocess.CalledProcessError, OSError) as e:
            shutil.rmtree(venv, ignore_errors=True)
            die(2, f"dependency install failed ({e}). Check network access and retry.")
        (venv / ".complete").write_text("\n".join(REQUIREMENTS) + "\n")
    os.execv(str(py), [str(py), "-I", os.path.abspath(__file__), *sys.argv[1:]])


def find_chrome():
    override = os.environ.get("CHROME")
    candidates = [override] if override else CHROME_CANDIDATES
    for c in candidates:
        p = Path(c).expanduser()
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)
    if override:
        die(2, f"CHROME={override} is not an executable file.")
    die(2, "Google Chrome not found in /Applications or ~/Applications. Install it from "
           "https://www.google.com/chrome/ or set CHROME=/path/to/chrome-binary.")


def chrome_major(chrome):
    try:
        out = subprocess.run([chrome, "--version"], capture_output=True, text=True, timeout=30).stdout
        m = re.search(r"(\d+)\.\d+", out)
        return int(m.group(1)) if m else None
    except (OSError, subprocess.TimeoutExpired):
        return None


# --------------------------------------------------------------------------- markdown

FENCE_RE = re.compile(r"^\s*(```|~~~)")
ITEM_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s")


def iter_outside_fences(lines):
    """Yield (line, in_fence) pairs; fence-delimiter lines count as inside."""
    fence = None
    for line in lines:
        m = FENCE_RE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)
                yield line, True
                continue
            if m.group(1) == fence:
                fence = None
                yield line, True
                continue
        yield line, fence is not None


def detect_list_indent(lines):
    """2 if nested list items are indented by 2-3 spaces (GitHub style), else 4."""
    indents = [len(m.group(1)) for line, f in iter_outside_fences(lines)
               if not f and (m := ITEM_RE.match(line)) and m.group(1)]
    return 4 if indents and min(indents) >= 4 else 2


def gfm_compat(text):
    """Patch GitHub-isms that Python-Markdown parses differently."""
    out, prev = [], ""
    for line, in_fence in iter_outside_fences(text.splitlines()):
        if not in_fence:
            starts_block = ITEM_RE.match(line) or line.lstrip().startswith("|")
            prev_is_text = (prev.strip() and not ITEM_RE.match(prev)
                            and not prev.lstrip().startswith(("|", "#", ">", "<"))
                            and not prev.startswith((" ", "\t")))
            # GitHub starts a list/table right after a paragraph line; Python-Markdown
            # needs a blank line first, otherwise it glues them into the paragraph.
            if starts_block and prev_is_text:
                out.append("")
            # Let Markdown inside <details> render, as it does on GitHub.
            line = re.sub(r"<details(?![^>]*\bmarkdown=)", '<details markdown="1"', line)
        out.append(line)
        prev = line
    return "\n".join(out) + "\n"


def github_slug(value, separator="-"):
    """Heading anchors that match GitHub's, so [x](#some-heading) links keep working."""
    value = re.sub(r"<[^>]+>", "", value).strip().lower()
    value = re.sub(r"[^\w\- ]", "", value)
    return value.replace(" ", separator)


def to_html_body(text, list_indent):
    import markdown  # noqa: E402  (available only inside the venv)
    md = markdown.Markdown(
        extensions=["pymdownx.superfences", "pymdownx.highlight", "tables", "toc",
                    "md_in_html", "mdx_truly_sane_lists", "pymdownx.tasklist",
                    "pymdownx.tilde", "pymdownx.magiclink", "attr_list", "def_list",
                    "footnotes", "abbr"],
        extension_configs={
            "pymdownx.highlight": {"guess_lang": False, "css_class": "hl", "use_pygments": True},
            "toc": {"slugify": github_slug},
            "mdx_truly_sane_lists": {"nested_indent": list_indent, "truly_sane": True},
            "pymdownx.tasklist": {"custom_checkbox": False},
        },
    )
    body = md.convert(text)
    # A code block can come out wrapped in <p>; the browser then splits it into an empty
    # paragraph and the "keep intro with code" rule stops working.
    body = body.replace('<p><div class="hl">', '<div class="hl">').replace("</div></p>", "</div>")
    # Expand <details> so collapsed content is printed.
    body = re.sub(r"<details(?![^>]*\bopen\b)", "<details open", body)
    return body


def absolutize_images(body, base_dir):
    """Rewrite relative <img src> to file:// URLs; Chrome renders from a temp dir."""
    def fix(m):
        src = html.unescape(m.group(2))
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:|^//|^#", src):
            return m.group(0)
        path = (base_dir / urllib.parse.unquote(src)).resolve()
        if not path.exists():
            print(f"md_to_pdf: warning: image not found: {src}", file=sys.stderr)
        return f'{m.group(1)}"{html.escape(path.as_uri())}"'
    return re.sub(r'(<img\b[^>]*?\bsrc=)"([^"]*)"', fix, body)


def extract_title(body, fallback):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else fallback


CSS = """
@page { size: %(paper)s; margin: 14mm 14mm 16mm 14mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font: 10pt/1.42 -apple-system, "Helvetica Neue", "PingFang SC", "Hiragino Sans", Arial, sans-serif;
       color: #1d1d1f; background: #fff; margin: 0; }
h1 { font-size: 20pt; margin: 0 0 4pt; color: #0b3d91; }
h2 { font-size: 13.5pt; color: #0b3d91; border-bottom: 1.5px solid #c9d6ea; padding-bottom: 2pt;
     margin: 14pt 0 6pt; }
h3 { font-size: 11pt; margin: 10pt 0 4pt; }
h4, h5, h6 { font-size: 10pt; margin: 8pt 0 3pt; }
h1, h2, h3, h4, h5, h6 { break-after: avoid; }
p, li { margin: 3pt 0; }
ul, ol { padding-left: 16pt; margin: 4pt 0; }
li > ul, li > ol { margin: 1pt 0; }
hr { border: 0; border-top: 1px solid #d0d7de; margin: 10pt 0; }
hr:has(+ h1), hr:has(+ h2) { display: none; }  /* those headings draw their own rule */
a { color: #0b3d91; text-decoration: none; }
img { max-width: 100%%; break-inside: avoid; }
blockquote { margin: 5pt 0; padding: 2pt 10pt; border-left: 3px solid #c9d6ea; color: #444; }
code { font-variant-ligatures: none; font: 8.6pt/1.35 Menlo, Monaco, monospace;
       background: #f1f3f6; padding: 0 2px; border-radius: 3px; }
.hl, pre { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 4px; break-inside: avoid; }
.hl { margin: 5pt 0; }
.hl pre, pre { margin: 0; padding: 6pt 8pt; white-space: pre-wrap; overflow-wrap: anywhere; }
.hl pre { border: 0; background: none; }
pre code { background: none; padding: 0; }
li .hl { margin: 3pt 0; }
table { border-collapse: collapse; width: 100%%; margin: 5pt 0; font-size: 9pt; break-inside: avoid; }
th, td { border: 1px solid #d0d7de; padding: 3pt 6pt; text-align: left; vertical-align: top; }
th { background: #eef2f8; }
tr { break-inside: avoid; }
p:has(+ .hl), p:has(+ table), p:has(+ ul), p:has(+ ol), p:has(+ pre) { break-after: avoid; }
details { margin: 4pt 0; }
summary { font-weight: 600; list-style: none; }
summary::-webkit-details-marker { display: none; }
.task-list-item { list-style: none; margin-left: -14pt; }
.footnote { font-size: 8.5pt; color: #444; }
"""


def build_html(src, args):
    text = src.read_text(encoding="utf-8")
    lines = text.splitlines()
    indent = detect_list_indent(lines) if args.list_indent == "auto" else int(args.list_indent)
    body = to_html_body(gfm_compat(text), indent)
    body = absolutize_images(body, src.parent)
    from pygments.formatters import HtmlFormatter  # noqa: E402
    css = CSS % {"paper": "A4" if args.paper == "a4" else "Letter"}
    css += HtmlFormatter(style="friendly").get_style_defs(".hl")
    if args.page_numbers:
        css += ('\n@page { @bottom-right { content: counter(page) " / " counter(pages);'
                " font: 8pt -apple-system, sans-serif; color: #888; } }\n")
    if args.css:
        css += "\n/* --css */\n" + Path(args.css).expanduser().read_text(encoding="utf-8")
    title = args.title or extract_title(body, src.stem)
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f"<title>{html.escape(title)}</title><style>{css}</style></head>"
            f"<body>{body}</body></html>"), indent


# --------------------------------------------------------------------------- chrome + checks

def print_pdf(chrome, html_path, pdf_path, workdir):
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--disable-extensions", "--disable-sync",
           f"--user-data-dir={workdir / 'chrome-profile'}",  # never touch the user's profile
           "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
           "--virtual-time-budget=10000",                    # let images and fonts load
           f"--print-to-pdf={pdf_path}", html_path.as_uri()]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CHROME_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        die(1, f"Chrome did not finish within {CHROME_TIMEOUT_S}s.")
    data = pdf_path.read_bytes() if pdf_path.exists() else b""
    if not data.startswith(b"%PDF"):
        tail = "\n".join((proc.stderr or "").strip().splitlines()[-15:])
        die(1, f"Chrome did not produce a PDF (exit {proc.returncode}).\n{tail}")


def page_count(pdf_path):
    import pypdfium2 as pdfium  # noqa: E402
    doc = pdfium.PdfDocument(str(pdf_path))
    try:
        return len(doc)
    finally:
        doc.close()


def render_preview(pdf_path, out_dir):
    """Write page-NN.png for every page plus contact.png (all pages side by side)."""
    import pypdfium2 as pdfium  # noqa: E402
    from PIL import Image  # noqa: E402
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("page-*.png"):
        old.unlink()
    doc = pdfium.PdfDocument(str(pdf_path))
    try:
        pages = [doc[i].render(scale=1.1).to_pil() for i in range(len(doc))]
    finally:
        doc.close()
    for i, im in enumerate(pages, 1):
        im.save(out_dir / f"page-{i:02d}.png")
    w, h = pages[0].size
    s, cols = 0.5, min(5, len(pages))
    rows = -(-len(pages) // cols)
    sheet = Image.new("RGB", (int(w * s) * cols, int(h * s) * rows), "white")
    for k, im in enumerate(pages):
        sheet.paste(im.resize((int(w * s), int(h * s))), ((k % cols) * int(w * s), (k // cols) * int(h * s)))
    sheet.save(out_dir / "contact.png")
    return len(pages)


# --------------------------------------------------------------------------- main

def parse_args():
    p = argparse.ArgumentParser(description="Markdown to styled PDF via headless Google Chrome (macOS).")
    p.add_argument("input", help="Markdown file")
    p.add_argument("-o", "--output", help="PDF path (default: INPUT with .pdf)")
    p.add_argument("--paper", choices=["letter", "a4"], default="letter")
    p.add_argument("--css", help="extra CSS file appended after the built-in style")
    p.add_argument("--page-numbers", action="store_true", help='add "N / total" at the bottom right')
    p.add_argument("--title", help="PDF title metadata (default: first H1, else file name)")
    p.add_argument("--list-indent", choices=["auto", "2", "4"], default="auto",
                   help="spaces per nested-list level (default: detect from the file)")
    p.add_argument("--preview", metavar="DIR", help="also render page PNGs + contact.png into DIR")
    p.add_argument("--keep-html", metavar="PATH", help="also save the intermediate HTML")
    return p.parse_args()


def main():
    check_platform()
    args = parse_args()  # parse before bootstrapping so --help/usage errors are instant
    ensure_venv_and_reexec()

    src = Path(args.input).expanduser().resolve()
    if not src.is_file():
        die(3, f"input not found: {src}")
    if args.css and not Path(args.css).expanduser().is_file():
        die(3, f"--css file not found: {args.css}")
    out = Path(args.output).expanduser().resolve() if args.output else src.with_suffix(".pdf")
    if out == src:
        die(3, "output path equals the input path.")
    if not out.parent.is_dir():
        die(3, f"output directory does not exist: {out.parent}")

    chrome = find_chrome()
    major = chrome_major(chrome)
    if major is not None and major < MIN_CHROME_MAJOR:
        print(f"md_to_pdf: warning: Chrome {major} is older than {MIN_CHROME_MAJOR}; "
              "some keep-together page-break rules will be ignored.", file=sys.stderr)

    doc_html, indent = build_html(src, args)
    with tempfile.TemporaryDirectory(prefix="md_to_pdf.") as tmp:
        work = Path(tmp)
        html_path = work / "doc.html"
        html_path.write_text(doc_html, encoding="utf-8")
        if args.keep_html:
            Path(args.keep_html).expanduser().write_text(doc_html, encoding="utf-8")
        tmp_pdf = work / "out.pdf"
        print_pdf(chrome, html_path, tmp_pdf, work)
        shutil.move(str(tmp_pdf), str(out))  # only replace an existing PDF once a new one exists

    n = page_count(out)
    print(f"wrote {out} ({n} page{'s' if n != 1 else ''}, {out.stat().st_size // 1024} KB, "
          f"list indent {indent})")
    if args.preview:
        prev = Path(args.preview).expanduser().resolve()
        render_preview(out, prev)
        print(f"preview: {prev}/contact.png and {prev}/page-01.png ... page-{n:02d}.png")


if __name__ == "__main__":
    main()
