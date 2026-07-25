#!/usr/bin/env python3
"""
.github/i18n/check.py — translation drift-check for probabilitycrisis.com

THE RITUAL (i18n charter, section D):
  index.html is the canonical English source, forever. Every translation
  (index.zh.html, index.af.html, ...) is a DERIVED ARTIFACT that records,
  in .github/i18n/manifest.json, the exact commit hash of index.html it
  was translated FROM (the "base" hash).

  Run this before any site work:

      python .github/i18n/check.py

  For each translation entry in the manifest, this script compares the
  recorded "base" hash against the source file's current HEAD commit
  (git log -1 --format=%H -- <source>) and prints one of:

    CURRENT <file>
        The recorded base still matches HEAD for the source. Nothing to do.

    STALE <file> (source moved: <base>..<head> — translate the diff: ...)
        The source has moved on since the translation was last synced.

    STALE <file> (unstamped — stamp base hash at ship)
        The manifest entry still carries the "STAMP-AT-SHIP" placeholder;
        no real base hash has ever been recorded for this translation.

  To resolve a STALE entry:
    1. git diff <base>..HEAD -- index.html
    2. Translate ONLY the delta shown by that diff into the corresponding
       language file. Do not re-translate untouched sections.
    3. Patch the translation file.
    4. Bump "base" in manifest.json to the new HEAD hash for index.html
       (git log -1 --format=%H -- index.html), and update "updated" to
       today's date.

  Exit code: 1 if any entry is STALE, 0 only when every translation is
  CURRENT with its source. (Infrastructure failures — git missing, a
  malformed manifest, missing files — exit 2 with a loud stderr message,
  distinct from the STALE signal.)

Usage:
    python check.py [--manifest PATH]

    --manifest PATH   Use an alternate manifest.json instead of the one
                       next to this script (.github/i18n/manifest.json).
                       Exists so the drift logic can be exercised against
                       a scratch manifest in tests.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

PLACEHOLDER = "STAMP-AT-SHIP"


def fail(message: str, code: int = 2) -> None:
    """Print a clear, loud error to stderr and exit non-zero."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def git_head_hash(repo_root: Path, relative_source: str) -> str:
    """Return the full commit hash of the last commit that touched
    `relative_source` (a path relative to repo_root), per
    `git log -1 --format=%H -- <source>` run with cwd=repo_root."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", relative_source],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        fail(
            "git not found on PATH. Install git (or add it to PATH) and "
            "re-run this check."
        )
        raise  # unreachable, keeps type-checkers happy

    if result.returncode != 0:
        fail(
            f"'git log' failed for '{relative_source}' (exit {result.returncode}): "
            f"{result.stderr.strip() or 'no stderr output'}"
        )

    head = result.stdout.strip()
    if not head:
        fail(
            f"'git log' returned no history for '{relative_source}'. "
            f"Is the file tracked and committed in this repo?"
        )
    return head


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.is_file():
        fail(f"manifest not found at '{manifest_path}'.")

    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"could not read manifest '{manifest_path}': {exc}")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"manifest '{manifest_path}' is not valid JSON: {exc}")

    if not isinstance(data, dict) or not data:
        fail(f"manifest '{manifest_path}' must be a non-empty JSON object.")

    for translated_file, entry in data.items():
        if not isinstance(entry, dict):
            fail(f"manifest entry '{translated_file}' must be a JSON object.")
        for key in ("source", "base", "updated"):
            if key not in entry:
                fail(
                    f"manifest entry '{translated_file}' is missing required "
                    f"key '{key}'."
                )

    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Translation drift-check against the canonical English source."
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default=None,
        help=(
            "Path to an alternate manifest.json (default: manifest.json "
            "next to this script). Useful for testing."
        ),
    )
    args = parser.parse_args()

    # Script lives at .github/i18n/check.py — two levels up is the repo root.
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    manifest_path = (
        Path(args.manifest).resolve() if args.manifest else script_dir / "manifest.json"
    )

    manifest = load_manifest(manifest_path)

    any_stale = False

    for translated_file, entry in manifest.items():
        source = entry["source"]
        base = entry["base"]

        source_path = repo_root / source
        if not source_path.is_file():
            fail(
                f"source file '{source}' (for '{translated_file}') not found "
                f"at '{source_path}'."
            )

        if base == PLACEHOLDER:
            any_stale = True
            print(f"STALE {translated_file} (unstamped — stamp base hash at ship)")
            continue

        head = git_head_hash(repo_root, source)

        if head == base:
            print(f"CURRENT {translated_file}")
        else:
            any_stale = True
            print(
                f"STALE {translated_file} (source moved: {base[:7]}..{head[:7]} "
                f"— translate the diff: git diff {base}..HEAD -- {source})"
            )

    return 1 if any_stale else 0


if __name__ == "__main__":
    sys.exit(main())
