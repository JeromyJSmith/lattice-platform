#!/usr/bin/env bash
# LATTICE mandatory pre-commit docs-sync check.
# Mirrors .github/workflows/docs-sync-check.yml so violations are caught locally.
#
# Install:
#   ln -sf ../../scripts/pre-commit-docs-check.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

echo "🔍 LATTICE pre-commit: running docs-sync check..."

fail=0

# ---- 1. Migration count ----
ACTUAL=$(find pixeltable/migrations -maxdepth 1 -name '0*.py' -not -name '__init__.py' 2>/dev/null | wc -l | tr -d ' ')
LAST_NUM=$(printf "%04d" "$ACTUAL")

if [ "$ACTUAL" -gt 0 ]; then
  if ! grep -qE "Migration trail.*0001[–-]" meta/SCHEMA.md 2>/dev/null; then
    echo "❌ meta/SCHEMA.md missing 'Migration trail: 0001-...' header"
    echo "   Fix: declare the migration trail in meta/SCHEMA.md (you have $ACTUAL migrations)"
    fail=1
  fi
  if ! grep -q "$LAST_NUM" meta/ARCHITECTURE.md 2>/dev/null; then
    echo "❌ meta/ARCHITECTURE.md does not reference migration $LAST_NUM"
    echo "   Fix: update the 'Last verified' line and section 6 to reference migration $LAST_NUM"
    fail=1
  fi
fi

# ---- 2. Table count consistency ----
SCHEMA_COUNT=$(grep -oE '\*\*[0-9]+ tables?\*\*' meta/SCHEMA.md 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo 0)
ARCH_COUNT=$(grep -oE '\*\*[0-9]+ tables?\*\*' meta/ARCHITECTURE.md 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo 0)
if [ "$SCHEMA_COUNT" != "0" ] && [ "$ARCH_COUNT" != "0" ] && [ "$SCHEMA_COUNT" != "$ARCH_COUNT" ]; then
  echo "❌ Table count drift: SCHEMA.md=$SCHEMA_COUNT, ARCHITECTURE.md=$ARCH_COUNT"
  echo "   Fix: make both files declare the same table count"
  fail=1
fi

# ---- 3. Endpoint count consistency ----
ROUTER_COUNT=$(grep -rhE '^@router\.(get|post|put|delete|patch)' pixeltable/service/routes/ 2>/dev/null | wc -l | tr -d ' ')
APP_COUNT=$(grep -E '^@app\.(get|post|put|delete|patch)' pixeltable/service/main.py 2>/dev/null | wc -l | tr -d ' ')
TOTAL_EP=$((ROUTER_COUNT + APP_COUNT))
API_COUNT=$(grep -oE '\*\*[0-9]+ endpoints?\*\*' meta/API.md 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo 0)
if [ "$API_COUNT" != "0" ] && [ "$API_COUNT" != "$TOTAL_EP" ]; then
  echo "❌ Endpoint count drift: code=$TOTAL_EP, meta/API.md=$API_COUNT"
  echo "   Fix: update meta/API.md and meta/ARCHITECTURE.md to declare $TOTAL_EP endpoints"
  fail=1
fi

# ---- 4. Root CLAUDE.md mandatory rules ----
ROOT_CLAUDE="../CLAUDE.md"
[ -f "$ROOT_CLAUDE" ] || ROOT_CLAUDE="CLAUDE.md"
if [ -f "$ROOT_CLAUDE" ]; then
  for needle in "pxt.String" "write-once" "pixeltable/migrations/" "create_dir"; do
    if ! grep -q "$needle" "$ROOT_CLAUDE"; then
      echo "❌ Root CLAUDE.md missing mandatory rule reference: '$needle'"
      fail=1
    fi
  done
fi

# ---- 5. FEATURE_BACKLOG sections ----
for section in "GEOREF SYSTEM" "REALITY CAPTURE" "DIGITAL TWIN MIRROR" "PLANT ASSET" "LOCAL AI"; do
  if ! grep -qi "$section" meta/FEATURE_BACKLOG.md 2>/dev/null; then
    echo "❌ meta/FEATURE_BACKLOG.md missing required section: '$section'"
    fail=1
  fi
done

# ---- 6. No forbidden strings in staged files ----
STAGED=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
if [ -n "$STAGED" ]; then
  # Allowlist: files that legitimately reference forbidden patterns as
  # anti-pattern documentation, agent guardrails, or string-literal enums.
  # Union of both sides of the merge (kept in sync with docs-sync-check.yml).
  ALLOWLIST_REGEX='^(meta/|\.github/|scripts/pre-commit-docs-check\.sh|scripts/audit-dead-dna\.sh|scripts/score-.*\.sh|.*CLAUDE\.md|.*AGENTS\.md|.*README\.md|.*INSTALL\.md|.*CONTRIBUTING\.md|.*CHANGELOG\.md|.*HANDOFF\.md|codex\.md|cloudflare-agent\.md|\.cursorrules|\.cursor/|\.agents/|\.codex/|.*/GOAL\.md|.*/MEMORY\.md|\.claude/|pixeltable/migrations/|ddc/converters/|analysis/capabilities/|analysis/infranodus/|analysis/gaps/|analysis/desires/)'
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    case "$f" in
      *.lock|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.parquet|*.glb|*.gltf|*.las|*.laz|*.ifc) continue ;;
    esac
    if echo "$f" | grep -qE "$ALLOWLIST_REGEX"; then
      continue
    fi
    for needle in '[Rr]evit' '[Mm]icro[Ss]tation' 'dgnconverter' 'rvtconverter' '@itwin/core-backend' 'SnapshotDb' 'pxt\.Geometry' 'pixeltable/service/migrations'; do
      # Lines tagged `allow-forbidden` are intentional anti-pattern references.
      MATCH=$(grep -nE "$needle" "$f" 2>/dev/null | grep -v 'allow-forbidden' | head -2 || true)
      if [ -n "$MATCH" ]; then
        echo "❌ Forbidden string '$needle' in $f:"
        echo "$MATCH"
        echo "   (Append \`# allow-forbidden\` to the line if this is intentional anti-pattern doc.)"
        fail=1
      fi
    done
    case "$f" in
      *.ts|*.tsx)
        if grep -nE '^import\s+Anthropic' "$f" >/dev/null 2>&1; then
          echo "❌ Bare 'import Anthropic' in $f — use @tanstack/ai adapters instead"
          fail=1
        fi
        ;;
    esac
  done <<EOF
$STAGED
EOF
fi

# ---- 7. Capability registry Zero Dead DNA audit ----
if [ -f scripts/audit-dead-dna.sh ]; then
  if ! bash scripts/audit-dead-dna.sh; then
    fail=1
  fi
else
  echo "❌ scripts/audit-dead-dna.sh is missing"
  fail=1
fi

# ---- 8. Python docstring audit ----
if [ -f scripts/check-python-docstrings.py ]; then
  if ! uv run python scripts/check-python-docstrings.py; then
    fail=1
  fi
else
  echo "❌ scripts/check-python-docstrings.py is missing"
  fail=1
fi

# ---- 9. Agent frontmatter (.claude/agents/*.md) ----
AGENT_DIR="$REPO_ROOT/.claude/agents"
if [ -d "$AGENT_DIR" ]; then
  while IFS= read -r -d '' f; do
    if ! grep -q '^name:' "$f"; then
      echo "❌ $f: missing 'name:' in YAML frontmatter"
      fail=1
    fi
    if ! grep -q '^description:' "$f"; then
      echo "❌ $f: missing 'description:' in YAML frontmatter"
      fail=1
    fi
  done < <(find "$AGENT_DIR" -maxdepth 1 -name '*.md' -print0 2>/dev/null)
fi

# ---- 10. Lattice skill frontmatter (.claude/skills/lattice-*/SKILL.md) ----
SKILLS_DIR="$REPO_ROOT/.claude/skills"
if [ -d "$SKILLS_DIR" ]; then
  while IFS= read -r -d '' f; do
    if ! grep -q '^description:' "$f"; then
      echo "❌ $f: missing 'description:' in YAML frontmatter"
      fail=1
    fi
  done < <(find "$SKILLS_DIR" -path '*/lattice-*/SKILL.md' -print0 2>/dev/null)
fi

# ---- 11. Section GOAL.md structure ----
SECTION_DIRS="pixeltable pixeltable/service src georef genai vw-plugin ddc meta/harness"
for dir in $SECTION_DIRS; do
  goal="$REPO_ROOT/$dir/GOAL.md"
  if [ ! -f "$goal" ]; then
    echo "❌ Missing $dir/GOAL.md (required for every section directory)"
    fail=1
    continue
  fi
  for h2 in "## Fitness Function" "## Improvement Loop" "## Action Catalog" "## Operating Mode"; do
    if ! grep -qF "$h2" "$goal"; then
      echo "❌ $dir/GOAL.md: missing required section '$h2'"
      fail=1
    fi
  done
done

# ---- 12. Section MEMORY.md structure ----
for dir in $SECTION_DIRS; do
  mem="$REPO_ROOT/$dir/MEMORY.md"
  if [ ! -f "$mem" ]; then
    echo "❌ Missing $dir/MEMORY.md (required for every section directory)"
    fail=1
    continue
  fi
  for h2 in "## Open Decisions" "## Failed Experiments" "## Session Handoff Notes"; do
    if ! grep -qF "$h2" "$mem"; then
      echo "❌ $dir/MEMORY.md: missing required section '$h2'"
      fail=1
    fi
  done
done


if [ "$fail" -eq 1 ]; then
  echo ""
  echo "❌ LATTICE docs-sync check failed — see messages above."
  echo "   Local rules mirror .github/workflows/docs-sync-check.yml — CI will block the PR otherwise."
  exit 1
fi

echo "✅ docs-sync check passed — safe to commit"
