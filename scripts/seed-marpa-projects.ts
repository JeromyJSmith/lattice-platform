#!/usr/bin/env bun
/**
 * Seed `lattice/bridge/marpa_projects` from a CSV or JSON file.
 *
 * Usage:
 *   bun scripts/seed-marpa-projects.ts <path-to-projects.csv|.json>
 *
 * CSV columns / JSON fields (all required unless marked optional):
 *   project_id, name, address, lat, lon, status, phase,
 *   project_manager, start_date, end_date (optional), ifc_path (optional)
 *
 * Tracked in meta/FEATURE_BACKLOG.md § CESIUM GLOBE → "Seed script".
 */
import { resolveSidecarClient } from "../src/runtime/pixeltable/sidecar-client";

const SOURCE = process.argv[2];
if (!SOURCE) {
  console.error(
    "usage: bun scripts/seed-marpa-projects.ts <projects.csv|projects.json>",
  );
  process.exit(1);
}

console.error("STUB: seed-marpa-projects.ts");
console.error(
  "  Tracked in meta/FEATURE_BACKLOG.md § CESIUM GLOBE → Seed script.",
);
console.error("  Acceptance criteria are on the matching GitHub issue.");
console.error("");
console.error("  Implementation outline:");
console.error(
  "  1. Detect format by extension (.csv -> parse rows, .json -> parse array)",
);
console.error("  2. Validate every row has the required fields");
console.error(
  "  3. POST batched rows to /v1/ingest/marpa-projects via resolveSidecarClient()",
);
console.error("  4. Print created/skipped counts");

// Reference the import so tsc/biome don't complain about an unused symbol.
void resolveSidecarClient;

process.exit(2);
