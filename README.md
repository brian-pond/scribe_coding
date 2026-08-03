# Scribe Coding

Scaffolding for **Scribe Coding** — a documentation-driven approach to AI-assisted software development. The core idea: a project writes and maintains durable context (requirements, decisions, technical notes) *before* relying on an AI agent to implement, configure, or substantially revise it, rather than treating documentation as after-the-fact paperwork.

Full writeup: https://datahenge.com/blog/document-driven-ai-development/

This repo is the factory, not a stamped project — it holds the templates and tooling used to bootstrap a new project's documentation tree, not a filled-in example of one.

## Quick Start

Generate the default scaffolding into a new or existing project directory:

```bash
scripts/init_scribe_coding_project.sh --target /path/to/project --name "Project Name" --prefix ABC
```

This copies the `templates/` tree into `--target`, substituting the project name, requirement-ID prefix, and today's date into each file. See the script's `--help` for details, and [SCRIBE_CODING.md](SCRIBE_CODING.md) for the full methodology, the projects it was reverse-engineered from, and how to use the result once stamped.

## What's Here

- [SCRIBE_CODING.md](SCRIBE_CODING.md) — the methodology, its origins, and constant vs. opt-in patterns.
- `templates/` — the documentation tree stamped into a new project by default.
- `templates-optional/` — additional patterns adopted by hand, only when a project needs them.
- `scripts/init_scribe_coding_project.sh` — the scaffolding generator described above.
- `tools/docs_check.py` — a documentation-hygiene linter (broken links, sprawl, stale references) to run against a stamped project's docs tree.
- [AGENTS.md](AGENTS.md) — working rules for anyone (human or AI) modifying this repo itself, including placeholder discipline and the smoke test to run after template changes.
