#!/usr/bin/env bash
set -euo pipefail

# Mirror the Benchy source corpus into LATTICE without importing secrets,
# dependency folders, generated output, or upstream git metadata.

SOURCE="${1:-/tmp/lattice-disler-sources/benchy}"
DEST="${2:-meta/harness/references/benchy}"

if [[ ! -d "$SOURCE" ]]; then
  echo "sync-benchy-reference: source directory not found: $SOURCE" >&2
  exit 2
fi

mkdir -p "$DEST"
rsync -a --delete \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude 'node_modules/' \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude '.DS_Store' \
  --exclude 'dist/' \
  --exclude 'trees/' \
  --exclude 'PROVENANCE.md' \
  "$SOURCE/" "$DEST/"

if find "$DEST" \( -name '.env*' -o -path '*/.git/*' -o -path '*/node_modules/*' -o -path '*/.venv/*' -o -path '*/dist/*' \) | grep -q .; then
  echo "sync-benchy-reference: unsafe files found in mirror" >&2
  exit 1
fi

echo "sync-benchy-reference: mirrored $(find "$DEST" -type f | wc -l | tr -d ' ') files into $DEST"
