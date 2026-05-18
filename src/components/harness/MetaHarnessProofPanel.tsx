import { AlertTriangle, GitBranch, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

type ScorePoint = {
  label: string;
  cycle: number;
  phase: string;
  total_score: number;
  outcome_score: number;
  instrument_score: number;
};

type ComponentRow = {
  name: string;
  family: "outcome" | "instrument";
  score: number;
  details?: Record<string, unknown>;
};

type GateCoverageRow = {
  gate_id: string;
  required_count: number;
  supporting_count: number;
};

type ClusterRow = {
  label: string;
  cluster_id: number | null;
  size_pct: number;
  influence_pct: number;
};

type ProofDashboardPayload = {
  dashboard: {
    current_score: {
      total_score: number;
      outcome_score: number;
      instrument_score: number;
      weakest_component?: string;
    };
    score_timeline: ScorePoint[];
    component_rows: ComponentRow[];
    gate_coverage: GateCoverageRow[];
    cluster_rows: ClusterRow[];
    infranodus_live_summary?: {
      statistics?: {
        nodeCount?: number;
        edgeCount?: number;
        clusterCount?: number;
        modularity?: number;
        diversity_score?: string;
      };
      mainConcepts?: string[];
      conceptualGateways?: string[];
      topRelations?: string[];
    };
    readiness?: {
      status?: string;
      blockers?: string[];
    };
    validation_summary?: {
      overall_status?: string;
      checks?: Array<{ name: string; status: string }>;
    };
    warnings?: string[];
    iteration_summary?: {
      real_count?: number;
      legacy_count?: number;
    };
  };
  graph: {
    nodes: Array<Record<string, unknown>>;
    links: Array<Record<string, unknown>>;
  };
  refreshed_at: string;
};

type EChartsModule = typeof import("echarts");
type ForceGraphFactory = typeof import("3d-force-graph")["default"];

async function fetchProofDashboard(): Promise<ProofDashboardPayload> {
  const response = await fetch("/api/harness/meta-proof-dashboard", {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`meta proof dashboard request failed: ${response.status}`);
  }
  return (await response.json()) as ProofDashboardPayload;
}

export function MetaHarnessProofPanel() {
  const [payload, setPayload] = useState<ProofDashboardPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const trendRef = useRef<HTMLDivElement | null>(null);
  const componentRef = useRef<HTMLDivElement | null>(null);
  const gateRef = useRef<HTMLDivElement | null>(null);
  const clusterRef = useRef<HTMLDivElement | null>(null);
  const graphRef = useRef<HTMLDivElement | null>(null);

  const summary = useMemo(() => payload?.dashboard, [payload]);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const next = await fetchProofDashboard();
        if (!active) {
          return;
        }
        setPayload(next);
        setError(null);
      } catch (nextError) {
        if (!active) {
          return;
        }
        setError(
          nextError instanceof Error
            ? nextError.message
            : "Failed to load meta proof dashboard.",
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    void load();
    const interval = window.setInterval(load, 5000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    if (!payload) {
      return;
    }

    let disposed = false;
    let cleanup = () => {};

    const mount = async () => {
      const echarts = (await import("echarts")) as EChartsModule;
      const ForceGraph3D = (await import("3d-force-graph"))
        .default as ForceGraphFactory;

      if (
        disposed ||
        !trendRef.current ||
        !componentRef.current ||
        !gateRef.current ||
        !clusterRef.current ||
        !graphRef.current
      ) {
        return;
      }

      const trendChart = echarts.init(trendRef.current);
      const componentChart = echarts.init(componentRef.current);
      const gateChart = echarts.init(gateRef.current);
      const clusterChart = echarts.init(clusterRef.current);

      const dashboard = payload.dashboard;

      trendChart.setOption({
        tooltip: { trigger: "axis" },
        legend: { top: 8 },
        grid: { left: 40, right: 16, top: 52, bottom: 28 },
        xAxis: {
          type: "category",
          data: dashboard.score_timeline.map((item) => item.label),
        },
        yAxis: { type: "value", min: 0, max: 100 },
        series: [
          {
            name: "Total",
            type: "line",
            smooth: true,
            symbolSize: 9,
            areaStyle: { opacity: 0.12 },
            data: dashboard.score_timeline.map((item) => item.total_score),
            markLine: {
              data: [{ yAxis: 95, label: { formatter: "promotion target" } }],
            },
          },
          {
            name: "Outcome",
            type: "line",
            smooth: true,
            symbolSize: 7,
            data: dashboard.score_timeline.map((item) => item.outcome_score),
          },
          {
            name: "Instrument",
            type: "line",
            smooth: true,
            symbolSize: 7,
            data: dashboard.score_timeline.map((item) => item.instrument_score),
          },
        ],
      });

      componentChart.setOption({
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        grid: { left: 130, right: 16, top: 18, bottom: 24 },
        xAxis: { type: "value", min: 0 },
        yAxis: {
          type: "category",
          data: dashboard.component_rows.map((row) => row.name),
        },
        series: [
          {
            type: "bar",
            data: dashboard.component_rows.map((row) => ({
              value: row.score,
              itemStyle: {
                color:
                  row.family === "outcome"
                    ? "var(--color-chart-1)"
                    : "var(--color-chart-2)",
              },
            })),
            label: { show: true, position: "right" },
          },
        ],
      });

      gateChart.setOption({
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        legend: { top: 8 },
        grid: { left: 40, right: 16, top: 48, bottom: 58 },
        xAxis: {
          type: "category",
          axisLabel: { rotate: 25 },
          data: dashboard.gate_coverage.map((row) => row.gate_id),
        },
        yAxis: { type: "value" },
        series: [
          {
            name: "Required",
            type: "bar",
            data: dashboard.gate_coverage.map((row) => row.required_count),
          },
          {
            name: "Supporting",
            type: "bar",
            data: dashboard.gate_coverage.map((row) => row.supporting_count),
          },
        ],
      });

      clusterChart.setOption({
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        legend: { top: 8 },
        grid: { left: 40, right: 16, top: 48, bottom: 72 },
        xAxis: {
          type: "category",
          axisLabel: { rotate: 25 },
          data: dashboard.cluster_rows.map((row) => row.label),
        },
        yAxis: { type: "value", max: 100 },
        series: [
          {
            name: "Cluster Size %",
            type: "bar",
            data: dashboard.cluster_rows.map((row) => row.size_pct),
          },
          {
            name: "Influence %",
            type: "bar",
            data: dashboard.cluster_rows.map((row) => row.influence_pct),
          },
        ],
      });

      graphRef.current.innerHTML = "";
      const fg = ForceGraph3D()(graphRef.current)
        .backgroundColor("#08111c")
        .graphData(payload.graph)
        .nodeAutoColorBy("group")
        .nodeColor((node: Record<string, unknown>) =>
          String(node.color || "#94a3b8"),
        )
        .nodeVal((node: Record<string, unknown>) => Number(node.val || 6))
        .nodeLabel((node: Record<string, unknown>) => {
          const meta = node.meta as Record<string, unknown> | undefined;
          const details = meta
            ? Object.entries(meta)
                .map(([key, value]) => `${key}: ${String(value)}`)
                .join("<br>")
            : "";
          return `<div style="padding:8px 10px"><strong>${String(node.name || node.id)}</strong><br>${String(node.group || "")}${details ? `<br>${details}` : ""}</div>`;
        })
        .linkColor((link: Record<string, unknown>) =>
          String(link.color || "#94a3b8"),
        )
        .linkWidth((link: Record<string, unknown>) => Number(link.width || 1))
        .linkOpacity(0.45)
        .linkDirectionalParticles((link: Record<string, unknown>) =>
          link.relation === "content_gap" || link.relation === "blocked_by"
            ? 3
            : 0,
        )
        .linkDirectionalArrowLength((link: Record<string, unknown>) =>
          link.relation === "content_gap" ? 6 : 3,
        )
        .linkDirectionalArrowRelPos(0.92)
        .onNodeClick((node: Record<string, unknown>) => {
          const x = Number(node.x || 0);
          const y = Number(node.y || 0);
          const z = Number(node.z || 0);
          const distance = 120;
          const distRatio = 1 + distance / Math.hypot(x || 1, y || 1, z || 1);
          fg.cameraPosition(
            { x: x * distRatio, y: y * distRatio, z: z * distRatio },
            { x, y, z },
            1200,
          );
        });

      const handleResize = () => {
        trendChart.resize();
        componentChart.resize();
        gateChart.resize();
        clusterChart.resize();
      };

      window.addEventListener("resize", handleResize);
      cleanup = () => {
        window.removeEventListener("resize", handleResize);
        trendChart.dispose();
        componentChart.dispose();
        gateChart.dispose();
        clusterChart.dispose();
        fg.pauseAnimation();
        if (graphRef.current) {
          graphRef.current.innerHTML = "";
        }
      };
    };

    void mount();

    return () => {
      disposed = true;
      cleanup();
    };
  }, [payload]);

  if (loading && !payload) {
    return (
      <section className="island-shell rounded-lg p-4">
        <p className="m-0 text-sm text-[var(--sea-ink-soft)]">
          Loading live Meta-Harness proof dashboard...
        </p>
      </section>
    );
  }

  if (error && !payload) {
    return (
      <section className="island-shell rounded-lg border border-[rgba(183,28,28,0.22)] p-4">
        <div className="flex items-start gap-2 text-[rgb(183,28,28)]">
          <AlertTriangle size={18} className="mt-0.5" />
          <div>
            <h2 className="m-0 text-base font-bold">
              Meta-Harness proof dashboard unavailable
            </h2>
            <p className="m-0 mt-1 text-sm">{error}</p>
          </div>
        </div>
      </section>
    );
  }

  if (!summary || !payload) {
    return null;
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="island-kicker m-0">Live Parent Wrapper</p>
          <h2 className="m-0 text-2xl font-bold">
            Meta-Harness Proof Dashboard
          </h2>
          <p className="mt-1 text-sm text-[var(--sea-ink-soft)]">
            Benchmarks plus the live improvement loop, InfraNodus entity graph,
            cluster strength, and promotion blockers from the parent wrapper.
          </p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-[var(--surface-strong)] px-3 py-1.5 text-xs font-semibold text-[var(--sea-ink-soft)]">
          <RefreshCw size={14} />
          Refreshes every 5s ·{" "}
          {new Date(payload.refreshed_at).toLocaleTimeString()}
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-5">
        <MetricTile
          label="Total score"
          value={summary.current_score.total_score.toFixed(2)}
        />
        <MetricTile
          label="Outcome"
          value={summary.current_score.outcome_score.toFixed(2)}
        />
        <MetricTile
          label="Instrument"
          value={summary.current_score.instrument_score.toFixed(2)}
        />
        <MetricTile
          label="Real cycles"
          value={String(summary.iteration_summary?.real_count ?? 0)}
        />
        <MetricTile
          label="Promotion"
          value={summary.readiness?.status ?? "unknown"}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="grid gap-4">
          <ChartCard title="Improvement Loop">
            <div ref={trendRef} className="h-[320px] w-full" />
          </ChartCard>
          <div className="grid gap-4 lg:grid-cols-2">
            <ChartCard title="Component Breakdown">
              <div ref={componentRef} className="h-[320px] w-full" />
            </ChartCard>
            <ChartCard title="Lifecycle Tool Coverage">
              <div ref={gateRef} className="h-[320px] w-full" />
            </ChartCard>
          </div>
          <ChartCard title="InfraNodus Cluster Strength">
            <div ref={clusterRef} className="h-[320px] w-full" />
          </ChartCard>
        </div>

        <ChartCard title="InfraNodus Entity Graph">
          <div
            ref={graphRef}
            className="h-[760px] w-full overflow-hidden rounded-lg"
          />
        </ChartCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <InfoCard title="Promotion Blockers">
          <ul className="space-y-2 pl-5 text-sm text-[var(--sea-ink-soft)]">
            {(summary.readiness?.blockers ?? []).map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        </InfoCard>
        <InfoCard title="InfraNodus Live Summary">
          <div className="space-y-2 text-sm text-[var(--sea-ink-soft)]">
            <p className="m-0">
              {summary.infranodus_live_summary?.statistics?.nodeCount ?? 0}{" "}
              nodes ·{" "}
              {summary.infranodus_live_summary?.statistics?.edgeCount ?? 0}{" "}
              edges ·{" "}
              {summary.infranodus_live_summary?.statistics?.clusterCount ?? 0}{" "}
              clusters
            </p>
            <p className="m-0">
              Diversity:{" "}
              {summary.infranodus_live_summary?.statistics?.diversity_score ??
                "n/a"}{" "}
              · Modularity:{" "}
              {summary.infranodus_live_summary?.statistics?.modularity ?? "n/a"}
            </p>
            <p className="m-0">
              Main concepts:{" "}
              {(summary.infranodus_live_summary?.mainConcepts ?? []).join(", ")}
            </p>
            <p className="m-0">
              Gateways:{" "}
              {(summary.infranodus_live_summary?.conceptualGateways ?? []).join(
                ", ",
              )}
            </p>
          </div>
        </InfoCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <InfoCard title="Validation Checks">
          <div className="space-y-2 text-sm text-[var(--sea-ink-soft)]">
            {(summary.validation_summary?.checks ?? []).map((check) => (
              <div
                key={check.name}
                className="flex items-center justify-between rounded-md border border-[var(--line)] px-3 py-2"
              >
                <span>{check.name}</span>
                <span className="font-semibold">{check.status}</span>
              </div>
            ))}
          </div>
        </InfoCard>
        <InfoCard title="Proven Source Stack">
          <ul className="space-y-2 pl-5 text-sm text-[var(--sea-ink-soft)]">
            <li>
              Apache ECharts for line, grouped bar, and dynamic-update chart
              patterns.
            </li>
            <li>
              3d-force-graph for click-to-focus, directional arrows, and
              stressed-link particles.
            </li>
            <li>
              InfraNodus live MCP output for clusters, gaps, gateways, and
              concept relationships.
            </li>
          </ul>
        </InfoCard>
      </div>

      {(summary.warnings ?? []).length > 0 ? (
        <div className="rounded-lg border border-[rgba(191,87,0,0.22)] bg-[rgba(191,87,0,0.08)] px-4 py-3 text-sm text-[rgb(140,72,0)]">
          {summary.warnings.join(" ")}
        </div>
      ) : null}
    </section>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="island-shell rounded-lg p-4">
      <p className="m-0 text-xs font-semibold uppercase tracking-wide text-[var(--sea-ink-soft)]">
        {label}
      </p>
      <p className="m-0 mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="island-shell rounded-lg p-4">
      <div className="mb-3 flex items-center gap-2">
        <GitBranch size={18} />
        <h3 className="m-0 text-lg font-bold">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function InfoCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="island-shell rounded-lg p-4">
      <h3 className="m-0 text-lg font-bold">{title}</h3>
      <div className="mt-3">{children}</div>
    </div>
  );
}
