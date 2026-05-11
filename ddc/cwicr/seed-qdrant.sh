#!/usr/bin/env bash
# Idempotent loader for the CWICR cost database into local Qdrant.
#
# Prereqs: see INSTALL.md (OrbStack + Docker + Qdrant running on :6333)
#
# Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "CWICR cost search".

set -euo pipefail

QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
COLLECTION="${COLLECTION:-cwicr}"
RELEASE_URL="${CWICR_RELEASE_URL:-https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases/latest/download/cwicr-data.tar.gz}"

echo "STUB: seed-qdrant.sh"
echo "  Tracked on GitHub issue. Sketch:"
echo "  1. Probe ${QDRANT_URL}/collections — fail fast if Qdrant isn't running"
echo "  2. PUT ${QDRANT_URL}/collections/${COLLECTION} with vector size 768, cosine distance"
echo "  3. Download ${RELEASE_URL} into a temp dir"
echo "  4. Iterate the 55,719 items; encode (description + region + unit) via sentence-transformers"
echo "  5. POST in batches of 256 to ${QDRANT_URL}/collections/${COLLECTION}/points"
echo "  6. Verify count: curl ${QDRANT_URL}/collections/${COLLECTION} | jq '.result.points_count'"
exit 2
