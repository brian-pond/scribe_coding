#!/usr/bin/env bash
# Stamps the Scribe Coding documentation scaffolding (../templates) into a
# target project directory, substituting {{PROJECT_NAME}}, {{ID_PREFIX}},
# and {{DATE}} placeholders.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: init_scribe_coding_project.sh --target DIR --name "Project Name" --prefix PREFIX [--force]

  --target DIR     Directory to create/populate. Created if missing.
  --name NAME      Human-readable project name (fills {{PROJECT_NAME}}).
  --prefix PREFIX  Short uppercase requirement-ID namespace, e.g. ABC (fills {{ID_PREFIX}}).
  --force          Overwrite existing files in DIR instead of skipping them.
  -h, --help       Show this help.

Example:
  init_scribe_coding_project.sh --target ~/projects/widget-tool --name "Widget Tool" --prefix WT
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
templates_dir="$script_dir/../templates"

target=""
name=""
prefix=""
force=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) target="$2"; shift 2 ;;
    --name) name="$2"; shift 2 ;;
    --prefix) prefix="$2"; shift 2 ;;
    --force) force=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$target" || -z "$name" || -z "$prefix" ]]; then
  echo "Missing required argument (--target, --name, and --prefix are all required)." >&2
  usage
  exit 1
fi

if [[ ! -d "$templates_dir" ]]; then
  echo "Templates directory not found: $templates_dir" >&2
  exit 1
fi

today="$(date +%F)"
mkdir -p "$target"

created=()
skipped=()

while IFS= read -r -d '' template_path; do
  rel_path="${template_path#"$templates_dir"/}"
  dest_rel="${rel_path%.tmpl}"
  dest_path="$target/$dest_rel"

  if [[ -e "$dest_path" && $force -eq 0 ]]; then
    skipped+=("$dest_rel")
    continue
  fi

  mkdir -p "$(dirname "$dest_path")"
  sed \
    -e "s#{{PROJECT_NAME}}#$name#g" \
    -e "s#{{ID_PREFIX}}#$prefix#g" \
    -e "s#{{DATE}}#$today#g" \
    "$template_path" > "$dest_path"
  created+=("$dest_rel")
done < <(find "$templates_dir" -type f -name '*.tmpl' -print0)

echo "Created ${#created[@]} file(s) in $target:"
for f in "${created[@]}"; do echo "  $f"; done

if [[ ${#skipped[@]} -gt 0 ]]; then
  echo
  echo "Skipped ${#skipped[@]} existing file(s) (use --force to overwrite):"
  for f in "${skipped[@]}"; do echo "  $f"; done
fi

echo
echo "Next steps:"
echo "  1. Fill in $target/CURRENT_CONTEXT.md and docs/requirements/00-overview.md"
echo "  2. Replace or delete the example rows in 01-functional.md, docs/adr/0001-example-decision.md, decisions/0001-example-decision.md"
echo "  3. Run tools/docs_check.py --root $target as a sanity check"
