import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";

const META_ROOT = "/Volumes/PixelTable/VW_iTwin_Bridge/meta";
const EVAL_DIR = resolve(META_ROOT, "evaluation");
const BUILD_SCRIPT = resolve(
  META_ROOT,
  "scripts/build-visualization-artifacts.py",
);
const DASHBOARD_JSON = resolve(EVAL_DIR, "dashboard-data.json");
const GRAPH_JSON = resolve(EVAL_DIR, "infranodus-entity-graph.json");

const SOURCE_PATHS = [
  resolve(EVAL_DIR, "metrics-latest.json"),
  resolve(EVAL_DIR, "validation-report.json"),
  resolve(EVAL_DIR, "copilot-ratchet-report.json"),
  resolve(EVAL_DIR, "infranodus-gap-analysis.json"),
  resolve(EVAL_DIR, "infranodus-live-summary.json"),
  resolve(META_ROOT, "promotion/readiness.json"),
  resolve(META_ROOT, "infranodus-phase-tool-map.json"),
  resolve(META_ROOT, "runs/iterations.jsonl"),
];

type MetaProofDashboardPayload = {
  dashboard: Record<string, unknown>;
  graph: Record<string, unknown>;
  refreshed_at: string;
};

function newestMtime(paths: string[]): number {
  let latest = 0;
  for (const path of paths) {
    if (!existsSync(path)) {
      continue;
    }
    latest = Math.max(latest, statSync(path).mtimeMs);
  }
  return latest;
}

function maybeRefreshArtifacts() {
  const sourceMtime = newestMtime(SOURCE_PATHS);
  const dashboardMtime = existsSync(DASHBOARD_JSON)
    ? statSync(DASHBOARD_JSON).mtimeMs
    : 0;

  if (dashboardMtime >= sourceMtime && existsSync(GRAPH_JSON)) {
    return;
  }

  execFileSync("python3", [BUILD_SCRIPT], {
    cwd: META_ROOT,
    stdio: "pipe",
  });
}

export async function loadMetaProofDashboard(): Promise<MetaProofDashboardPayload> {
  maybeRefreshArtifacts();

  const dashboard = JSON.parse(readFileSync(DASHBOARD_JSON, "utf8")) as Record<
    string,
    unknown
  >;
  const graph = JSON.parse(readFileSync(GRAPH_JSON, "utf8")) as Record<
    string,
    unknown
  >;

  return {
    dashboard,
    graph,
    refreshed_at: new Date().toISOString(),
  };
}
