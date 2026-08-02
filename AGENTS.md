Goal of this subdirectory = scaffolding for Scribe Coding.

See [SCRIBE_CODING.md](SCRIBE_CODING.md) for the method, where this scaffolding came from, and how to use it. Start a new project with `scripts/init_scribe_coding_project.sh`; check documentation hygiene with `tools/docs_check.py`.

## What This Repo Is (And Isn't)

This directory is the factory, not a stamped project. It intentionally has no `docs/requirements/`, `CURRENT_CONTEXT.md`, or `decisions/` at its own root — those exist only as `.tmpl` files under `templates/`, destined for other projects. Do not treat a file under `templates/` as this repo's own content, and do not "fill in" its placeholders — the placeholders are the point.

`templates-optional/` mirrors `templates/`'s structure but holds opt-in patterns that most projects don't need — `scripts/init_scribe_coding_project.sh` only sweeps `templates/`, so nothing under `templates-optional/` is ever stamped automatically. Adopting one means manually copying its file into the matching path under the target project.

## Placeholder Discipline

`{{PROJECT_NAME}}`, `{{ID_PREFIX}}`, and `{{DATE}}` inside `templates/**/*.tmpl` and `templates-optional/**/*.tmpl` are literal tokens substituted by `scripts/init_scribe_coding_project.sh` (for `templates/`) or by hand when an optional file is copied in. Never replace them with real values inside either tree, and never strip a file's `.tmpl` suffix by hand. A new template file should mirror the target project's relative path exactly and end in `.tmpl`; the init script picks up any `*.tmpl` under `templates/` automatically, so no separate registration is needed.

## Smoke-Test After Editing

After changing anything under `templates/` or `tools/docs_check.py`, verify the round-trip before considering the change done:

```bash
scripts/init_scribe_coding_project.sh --target /tmp/scribe_smoke_test --name "Smoke Test" --prefix ST
python3 tools/docs_check.py --root /tmp/scribe_smoke_test
rm -rf /tmp/scribe_smoke_test
```

`templates-optional/` files aren't stamped by the init script, so the above alone won't exercise them. Verify one by copying it into a stamped target at its matching path before running `docs_check.py`.

## Recording Methodology Changes

When a change here reflects a new pattern rather than a fix, log it with its source in `SCRIBE_CODING.md`'s "Mutable Methodology" section — don't bake a new pattern into a template silently.
