#!/usr/bin/env python3
"""Move the oldest CHANGELOG entries into the archive until the file fits its limit.

A changelog is append-only, so it grows past any prose word limit as a function
of project age rather than of poor editing. Rather than raising the limit
forever, this moves the oldest entries — the ones least likely to be read — into
`docs/archive/`, preserving them in order and leaving a pointer behind.

Entries are top-level Markdown bullets ("- " at column zero) under a "### "
heading inside "## [Unreleased]". An entry owns every following indented or
blank line until the next top-level bullet or heading.

Usage:
    tools/changelog_archive.py --dry-run
    tools/changelog_archive.py --max-words 4000
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CHANGELOG = Path("CHANGELOG.md")
DEFAULT_ARCHIVE = Path("docs/archive/CHANGELOG-archive.md")
ALLOWLIST_FILENAME = ".docs_check_allowlist"
# Matches docs_check.py's DEFAULT_MAX_WORDS, so a project with no allowlist gets
# the same answer from both tools.
FALLBACK_MAX_WORDS = 1800

ARCHIVE_PREAMBLE = """---
status: archived
owner: project
purpose: Older `CHANGELOG.md` entries, moved here verbatim so the active changelog stays readable in one sitting.
---

# Changelog Archive

Entries moved out of [../../CHANGELOG.md](../../CHANGELOG.md), oldest first.
Nothing here is edited on the way in — this is the same text, relocated.

Do not load this file for active work unless you need history.
"""


@dataclass
class Section:
    heading: str
    entries: list[str] = field(default_factory=list)


def word_count(text: str) -> int:
    return len(text.split())


def limit_from_allowlist(root: Path, target: Path) -> int:
    """Read the target's DOC002 limit so this tool and docs_check agree."""
    allowlist = root / ALLOWLIST_FILENAME
    if not allowlist.exists():
        return FALLBACK_MAX_WORDS
    for line in allowlist.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        rel_path, _, max_words = line.partition("=")
        if rel_path.strip() == str(target):
            return int(max_words.strip())
    return FALLBACK_MAX_WORDS


def split_sections(lines: list[str]) -> tuple[list[str], list[Section], list[str]]:
    """Return (header lines, sections carrying entries, trailing lines)."""
    header: list[str] = []
    sections: list[Section] = []
    trailing: list[str] = []

    in_unreleased = False
    current: Section | None = None

    for line in lines:
        if line.startswith("## "):
            in_unreleased = line.strip() == "## [Unreleased]"
            if current is not None:
                sections.append(current)
                current = None
            (header if in_unreleased or not sections else trailing).append(line)
            continue

        if in_unreleased and line.startswith("### "):
            if current is not None:
                sections.append(current)
            current = Section(heading=line)
            continue

        if current is not None:
            if line.startswith("- "):
                current.entries.append(line)
            elif current.entries and (line.strip() == "" or line.startswith((" ", "\t"))):
                current.entries[-1] += line
            elif line.strip() == "":
                current.heading += line
            else:
                # Prose after the entries (a closing note) ends the section.
                sections.append(current)
                current = None
                trailing.append(line)
        elif sections:
            trailing.append(line)
        else:
            header.append(line)

    if current is not None:
        sections.append(current)
    return header, sections, trailing


def render(header: list[str], sections: list[Section], trailing: list[str]) -> str:
    """Emit the changelog, dropping any section whose entries were all archived."""
    out = "".join(header)
    for section in sections:
        if not section.entries:
            continue
        out += section.heading + "".join(section.entries)
    return out + "".join(trailing)


def ensure_archive_pointer(text: str, archive: Path) -> str:
    """Add a one-line pointer to the archive, once, just under the title block."""
    pointer = f"Older entries are in [{archive}]({archive}).\n"
    if str(archive) in text:
        return text
    marker = "## [Unreleased]"
    if marker not in text:
        return text
    head, _, tail = text.partition(marker)
    return f"{head}{pointer}\n{marker}{tail}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--changelog", type=Path, default=DEFAULT_CHANGELOG)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument(
        "--max-words",
        type=int,
        default=None,
        help=f"Word budget for the changelog. Defaults to its {ALLOWLIST_FILENAME} entry.",
    )
    parser.add_argument(
        "--headroom",
        type=float,
        default=0.20,
        help="Fraction of the budget to leave free, so the next few entries don't "
        "immediately trip the limit again (default 0.20).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report without writing.")
    args = parser.parse_args(argv)

    changelog_path = args.root / args.changelog
    archive_path = args.root / args.archive
    if not changelog_path.exists():
        print(f"error: {args.changelog} not found", file=sys.stderr)
        return 2

    budget = args.max_words or limit_from_allowlist(args.root, args.changelog)
    target = int(budget * (1.0 - args.headroom))
    text = changelog_path.read_text(encoding="utf-8")
    if word_count(text) <= budget:
        print(f"{args.changelog}: {word_count(text)} words, within {budget}. Nothing to archive.")
        return 0

    header, sections, trailing = split_sections(text.splitlines(keepends=True))
    moved: list[tuple[str, str]] = []

    # Oldest first: earliest section, earliest entry. Archive down to `target`
    # rather than to `budget`, so the next few entries have somewhere to go.
    for section in sections:
        while section.entries and word_count(render(header, sections, trailing)) > target:
            moved.append((section.heading.strip(), section.entries.pop(0)))
        if word_count(render(header, sections, trailing)) <= target:
            break

    if not moved:
        print("error: nothing left to archive; the remainder is not entries.", file=sys.stderr)
        return 1

    new_text = ensure_archive_pointer(render(header, sections, trailing), args.archive)
    print(f"{args.changelog}: {word_count(text)} -> {word_count(new_text)} words (limit {budget})")
    print(f"archiving {len(moved)} entr{'y' if len(moved) == 1 else 'ies'} to {args.archive}")
    if args.dry_run:
        for heading, entry in moved:
            print(f"  [{heading.lstrip('# ').strip()}] {entry.splitlines()[0][:88]}")
        return 0

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    existing = archive_path.read_text(encoding="utf-8") if archive_path.exists() else ARCHIVE_PREAMBLE
    appended = existing.rstrip("\n") + "\n"
    last_heading = None
    for heading, entry in moved:
        if heading != last_heading:
            appended += f"\n{heading}\n\n"
            last_heading = heading
        appended += entry.rstrip("\n") + "\n"
    archive_path.write_text(appended, encoding="utf-8")
    changelog_path.write_text(new_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
