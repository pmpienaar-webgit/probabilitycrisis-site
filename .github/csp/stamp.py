#!/usr/bin/env python3
"""
.github/csp/stamp.py — Content-Security-Policy stamp for probabilitycrisis.com

WHY THIS EXISTS
  GitHub Pages cannot send response headers, so the site's CSP travels as a
  <meta http-equiv="Content-Security-Policy"> tag in each page's <head>.
  Every inline <script> block is allowed by its SHA-256 hash; nothing else
  may run. The policy also says connect-src 'none' — the browser itself
  refuses any network call from the page, which turns "nothing leaves this
  page" from a promise into a mechanism.

  A hash is only valid for the exact script text. Change one byte inside any
  <script> block and the browser blocks that block silently (the page breaks
  with a console error, not a visible warning). So:

THE RITUAL
  1. Edit any page.
  2. Run:  python .github/csp/stamp.py
     The tool recomputes every page's script hashes and rewrites (or
     inserts) the CSP meta tag. Output per page: STAMPED / CURRENT / SKIP.
  3. Before pushing, run:  python .github/csp/stamp.py --check
     Exit 0 = every page's meta matches its scripts. Exit 1 = STALE pages
     are listed; run step 2 again.
  4. After pushing, the live-drive recomputes the hashes from the served
     bytes (the watcher does this) — a mismatch there means the bytes on
     disk and the bytes served differ, which is a line-ending problem.

LINE ENDINGS
  The HTML parser normalises CR LF to LF before it hashes a script, so this
  tool hashes LF-normalised script text. Files may be stored with either
  ending; the hash is the same.

POLICY (the single source of truth is POLICY below — edit it here, then
re-stamp all pages)
  default-src 'none'        nothing is allowed unless named below
  script-src  <hashes>      only the inline blocks present at stamp time
  style-src   'unsafe-inline'   the pages style themselves inline by design
  img-src     'self' data:  the favicon and any CSS image are data: URIs
  font-src    data:         the fonts are embedded base64
  connect-src 'none'        no fetch / XHR / beacon / WebSocket — ever
  everything else 'none'; base-uri 'none'; form-action 'none'
  (frame-ancestors is deliberately absent: browsers ignore it in a meta tag
  and log a warning; clickjacking protection needs a real header.)

USAGE
  python .github/csp/stamp.py             stamp all pages in PAGES
  python .github/csp/stamp.py --check     verify only, exit 1 if any stale
  python .github/csp/stamp.py a.html ...  stamp / check only the named pages
"""

import argparse
import base64
import hashlib
import re
import sys
from pathlib import Path

PAGES = [
    "index.html",
    "index.af.html",
    "index.zh.html",
    "keystone-read.html",
    "keystone-read.af.html",
    "keystone-read.zh.html",
]

POLICY = (
    "default-src 'none'; "
    "script-src {hashes}; "
    "style-src 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src data:; "
    "connect-src 'none'; "
    "object-src 'none'; "
    "frame-src 'none'; "
    "media-src 'none'; "
    "worker-src 'none'; "
    "manifest-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'"
)

SCRIPT_RE = re.compile(r"<script(\s[^>]*)?>(.*?)</script>", re.S | re.I)
TYPE_RE = re.compile(r"""\btype\s*=\s*["']?([^"'\s>]+)""", re.I)
# Only blocks the browser EXECUTES are subject to script-src. A data block such as
# application/ld+json is never checked, so hashing it would grant nothing.
JS_TYPES = {"text/javascript", "application/javascript", "module",
            "text/ecmascript", "application/ecmascript"}
META_RE = re.compile(
    r'<meta http-equiv="Content-Security-Policy" content="[^"]*">(?:\r?\n)?', re.I
)
ANCHOR_RE = re.compile(r'<meta name="viewport"[^>]*>(?:\r?\n)?', re.I)


def script_hashes(html: str) -> list[str]:
    """Return the ordered, de-duplicated 'sha256-…' tokens for every
    non-empty inline <script> block, hashed over LF-normalised text."""
    tokens: list[str] = []
    for match in SCRIPT_RE.finditer(html):
        attrs = match.group(1) or ""
        type_match = TYPE_RE.search(attrs)
        if type_match and type_match.group(1).lower() not in JS_TYPES:
            continue  # data block (e.g. application/ld+json): not executed, not hashed
        body = match.group(2).replace("\r\n", "\n").replace("\r", "\n")
        if not body.strip():
            continue
        digest = hashlib.sha256(body.encode("utf-8")).digest()
        token = "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"
        if token not in tokens:
            tokens.append(token)
    return tokens


def build_meta(tokens: list[str]) -> str:
    return (
        '<meta http-equiv="Content-Security-Policy" content="'
        + POLICY.format(hashes=" ".join(tokens))
        + '">'
    )


def process(path: Path, check_only: bool) -> bool:
    with open(path, encoding="utf-8", newline="") as fh:  # keep endings as-is (works on 3.10+)
        raw = fh.read()
    newline = "\r\n" if "\r\n" in raw else "\n"
    tokens = script_hashes(raw)
    if not tokens:
        print(f"SKIP    {path.name} (no inline scripts)")
        return True

    wanted = build_meta(tokens)
    existing = META_RE.search(raw)
    if existing and existing.group(0).rstrip("\r\n") == wanted:
        print(f"CURRENT {path.name} ({len(tokens)} hashes)")
        return True

    if check_only:
        state = "meta differs from scripts" if existing else "no CSP meta present"
        print(f"STALE   {path.name} ({state}) — run: python .github/csp/stamp.py")
        return False

    if existing:
        updated = raw[: existing.start()] + wanted + newline + raw[existing.end():]
    else:
        anchor = ANCHOR_RE.search(raw)
        if not anchor:
            print(f"ERROR   {path.name}: no <meta name=\"viewport\"> to anchor on", file=sys.stderr)
            return False
        updated = raw[: anchor.end()] + wanted + newline + raw[anchor.end():]

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(updated)
    print(f"STAMPED {path.name} ({len(tokens)} hashes)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Stamp or check the CSP meta tag on each page.")
    parser.add_argument("--check", action="store_true", help="verify only; exit 1 if any page is stale")
    parser.add_argument("pages", nargs="*", help="page files to process (default: the PAGES list)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    names = args.pages or PAGES
    ok = True
    for name in names:
        path = (repo_root / name) if not Path(name).is_absolute() else Path(name)
        if not path.is_file():
            print(f"ERROR   {name}: not found", file=sys.stderr)
            ok = False
            continue
        ok = process(path, args.check) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
