---
status: authoritative
owner: scribe-coding
purpose: Explains Brian's Scribe Coding methodology and what this directory's scaffolding contains.
---

# Scribe Coding

Source: https://datahenge.com/blog/document-driven-ai-development/

Scribe Coding is Brian's documentation-driven approach to AI-assisted software development. A project writes and maintains durable context — requirements, decisions, technical notes — before relying on an AI agent to implement, configure, or substantially revise the system.

## Core Principles

1. Write durable project context before implementation.
2. Use focused requirements, technical, and decision documents instead of one large undifferentiated notes file.
3. Treat requirements and decisions as implementation inputs, not after-the-fact paperwork.
4. Preserve traceability with stable requirement IDs.
5. Ask when requirements are missing, ambiguous, or contradictory — never infer from unstated preference.
6. Keep documentation current when behavior, decisions, scope, or structure changes.
7. Control documentation sprawl through clear ownership, status headers, indexes, and archive discipline.
8. Separate requirements authority (what's needed) from implementation inventory (what currently exists in code), so requirements documents don't become their own stale code-status trackers.
9. Documentation entropy is expected, not a failure. Review and clean up a project's documentation structure periodically, not just when it feels broken — see `docs/technical/01-documentation-conventions.md` (owner doc) for the review-session and multi-pass discipline this requires.

## Origin Of This Scaffolding

This scaffolding was not designed top-down from the blog post. It was reverse-engineered by reading Brian's projects that already practice Scribe Coding, each of which converged on similar patterns independently:

| Project | What it contributed |
|---|---|
| `~/projects/python/btu_v2` | Earliest mature instance: numbered requirements + technical trees, a documentation-authority map with per-topic ownership and reading orders. |
| `~/projects/python/cofferdam` | Small solo library. Tight ground-rules doc, `BR-<AREA>-NNN` citation discipline, a "definition of done" checklist, an ADR-per-decision index. |
| `~/projects/python/dbconform` | Minimal viable version: just 00-overview / 01-functional / 02-non-functional plus a CHANGELOG. Proof that the pattern scales down. |
| `~/projects/job_aggregator` | Personal tool; numbered requirements + technical docs, conventions pushed into `.cursor/rules/` instead of a plain README. |
| `~/erpnext_projects/datahenge-cairn` | Dual identifier system (`BR-*` requirements vs `ADR-*` decisions) and an explicit, test-enforced rule that internal IDs never reach user-facing text. |
| `~/clients/lifescientific/erpnext_launch` (`workspace/`) | The most refined instance, built under real deadline pressure. Added the `workspace/` vs `deliverables/` boundary, workspace-local vs external requirement-ID namespaces, and — critically — split "what's needed" from "what currently exists in code" into a dedicated implementation index after topic docs kept describing intent instead of reality. |
| `~/clients/lifescientific/erpnext_launch/data-migration-etl` | Sibling ETL subproject. Added `CURRENT_CONTEXT.md` as a session router, `OPEN_DECISIONS.md` as a literal pending-approval queue (so "ask, don't assume" has a durable home instead of living only in chat), and a `docs_check.py` documentation-hygiene linter. |

## What's In This Directory

- `SCRIBE_CODING.md` — this file.
- `templates/` — the documentation tree to stamp into a new project.
- `scripts/init_scribe_coding_project.sh` — copies `templates/` into a target directory, substituting project name, requirement-ID prefix, and today's date.
- `tools/docs_check.py` — a generalized documentation-hygiene linter (broken links, doc sprawl, decision-index drift, leaked local paths). Run it against a project's docs tree.

## Using This Scaffolding

```bash
scripts/init_scribe_coding_project.sh --target /path/to/new/project --name "Project Name" --prefix ABC
```

Then, in the new project:

1. Fill in `CURRENT_CONTEXT.md` and `docs/requirements/00-overview.md`.
2. Delete the example rows in `docs/requirements/01-functional.md`, `docs/adr/0001-example-decision.md`, and `decisions/0001-example-decision.md` once real content replaces them.
3. Run `tools/docs_check.py --root /path/to/new/project` (copy or symlink the tool in) as a first-pass sanity check.

## Constant Patterns (present in every project reviewed)

| Pattern | Why it kept recurring |
|---|---|
| Numbered `docs/requirements/NN-*.md` + `README.md` index + `CHANGELOG.md` | Lets an agent load only the relevant slice instead of one giant file. |
| Stable `<PREFIX>-<AREA>-NNN` requirement IDs, cited in docstrings/tests/commits, never in user-facing text | Traceability from requirement → code → test without leaking internal scaffolding to end users. |
| `docs/technical/` separate from `docs/requirements/` | WHAT (requirements) vs HOW (implementation) — prevents technical detail from drowning out business intent. |
| A documentation-authority map with reading orders | Single owner per topic; stops parallel, drifting summaries of the same rule. |
| ADRs for consequential decisions, lighter decision records for everything else | Not every decision earns a full alternatives-considered writeup. |
| Status header (`exploratory`/`authoritative`/`archived`/`deliverable`) on every doc | Tells a reader — human or AI — how much authority to assign a file at a glance. |
| An explicit open-questions mechanism | Converts "ask, don't assume" from an instruction into a trackable, durable artifact. |
| Archive discipline: "don't load for active work unless history is needed" | Keeps agent context from being drowned by superseded material that still needs to exist somewhere. |

## Patterns To Adopt Only When The Project Needs Them

These showed up in specific projects, not all of them — pull them in deliberately rather than by default.

| Pattern | Source | Adopt when |
|---|---|---|
| `workspace/` vs `deliverables/` boundary | lifescientific | The project has a private working area and a separate audience-facing publication boundary (e.g. client consulting). |
| Workspace-local requirement IDs vs external/team IDs with a mapping table | lifescientific | You must start design/development before a broader team's requirements baseline is stable. |
| `CURRENT_CONTEXT.md` session router | data-migration-etl | The project has enough moving parts that "where do I even start reading" is itself a recurring question. |
| `OPEN_DECISIONS.md` literal queue | data-migration-etl | Decisions need explicit sign-off before implementation proceeds, and that approval must be reconstructable later, not just remembered from chat. |
| `docs_check.py` hygiene linter | data-migration-etl | Documentation volume is high enough that broken links and word-count sprawl become a real risk. |
| Fit-gap / design-discussions / source-extraction trees | lifescientific | The project involves evaluating a platform's fit against requirements (ERP implementations, vendor selection). |

## Mutable Methodology

Scribe Coding is a working baseline, not a fixed template. Refine it when repeated friction, ambiguity, or documentation drift reveals a better pattern — the lifescientific implementation-index split is a direct example of this happening mid-project. When a Scribe Coding improvement is discovered on a specific project, record it there first; only bring the reusable, non-client-specific idea back into this directory.
