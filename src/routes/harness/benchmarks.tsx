import { createFileRoute } from "@tanstack/react-router";
import { FileText, Play, RefreshCw, Upload, Zap } from "lucide-react";
import { useMemo, useState } from "react";
import { MetaHarnessProofPanel } from "#/components/harness/MetaHarnessProofPanel";
import { runCodebaseContextProof } from "#/server/harness/run-codebase-context-proof";
import { validateBenchmarkReport } from "#/server/harness/validate-benchmark-report";

export const Route = createFileRoute("/harness/benchmarks")({
  component: HarnessBenchmarksPage,
});

type BenchResult = {
  prompt: string;
  success: boolean;
  latency_ms: number;
  cost_usd?: number;
  score?: number;
  output?: string;
};

type ModelReport = {
  model: string;
  provider?: string;
  results: BenchResult[];
};

type BenchmarkReport = {
  benchmark_name: string;
  purpose: string;
  base_prompt?: string;
  prompt_iterations?: Array<Record<string, string>>;
  provenance: {
    source: "sample" | "uploaded" | "sidecar_live_run" | "sidecar_import";
    trust:
      | "synthetic"
      | "uploaded_unverified"
      | "live_verified"
      | "live_failed";
    label: string;
    artifact?: string;
    verified_at?: string;
  };
  verification: {
    status: "unverified" | "passed" | "failed";
    message: string;
  };
  models: ModelReport[];
};

type CodebaseContextProofResult = {
  ok: boolean;
  sidecar_ok: boolean;
  artifact?: string;
  report: BenchmarkReport;
};

const SAMPLE_REPORT: BenchmarkReport = {
  benchmark_name: "Meta-Harness proof-run gate",
  purpose:
    "Compare candidate models on one LATTICE capability proof task before registry promotion.",
  base_prompt:
    "Given a capability candidate, produce a verifier-ready proof report with invocation, expected outcome, evidence path, and promotion decision.",
  prompt_iterations: [
    {
      capability: "benchy-console-report",
      expected: "proof_run_required_before_registry_promotion",
    },
  ],
  provenance: {
    source: "sample",
    trust: "synthetic",
    label: "Synthetic sample report",
  },
  verification: {
    status: "unverified",
    message: "Sample data only. Do not treat this report as live proof.",
  },
  models: [
    {
      model: "qwen3:14b",
      provider: "ollama",
      results: [
        {
          prompt: "registry gate",
          success: true,
          latency_ms: 9400,
          cost_usd: 0,
          score: 0.72,
        },
        {
          prompt: "evidence shape",
          success: true,
          latency_ms: 8700,
          cost_usd: 0,
          score: 0.78,
        },
        {
          prompt: "failure taxonomy",
          success: false,
          latency_ms: 10100,
          cost_usd: 0,
          score: 0.41,
        },
      ],
    },
    {
      model: "claude-sonnet",
      provider: "claude-cli",
      results: [
        {
          prompt: "registry gate",
          success: true,
          latency_ms: 5200,
          cost_usd: 0.012,
          score: 0.9,
        },
        {
          prompt: "evidence shape",
          success: true,
          latency_ms: 6100,
          cost_usd: 0.014,
          score: 0.88,
        },
        {
          prompt: "failure taxonomy",
          success: true,
          latency_ms: 5800,
          cost_usd: 0.013,
          score: 0.86,
        },
      ],
    },
    {
      model: "gpt-oss:20b",
      provider: "ollama",
      results: [
        {
          prompt: "registry gate",
          success: true,
          latency_ms: 7100,
          cost_usd: 0,
          score: 0.81,
        },
        {
          prompt: "evidence shape",
          success: false,
          latency_ms: 6800,
          cost_usd: 0,
          score: 0.5,
        },
        {
          prompt: "failure taxonomy",
          success: true,
          latency_ms: 7600,
          cost_usd: 0,
          score: 0.74,
        },
      ],
    },
  ],
};

function HarnessBenchmarksPage() {
  const [report, setReport] = useState<BenchmarkReport>(SAMPLE_REPORT);
  const [playbackStep, setPlaybackStep] = useState<number | null>(null);
  const [runStatus, setRunStatus] = useState<{
    state: "idle" | "running" | "passed" | "failed";
    message: string;
    artifact?: string;
  }>({ state: "idle", message: "Ready to run Golden Path 001." });
  const summary = useMemo(() => summarizeReport(report), [report]);
  const maxLatency = Math.max(
    1,
    ...report.models.flatMap((model) =>
      model.results.map((result) => result.latency_ms),
    ),
  );
  const stepCount = Math.max(
    0,
    ...report.models.map((model) => model.results.length),
  );
  const activeStep = playbackStep ?? stepCount;

  return (
    <main className="page-wrap px-4 pb-8 pt-14 space-y-5">
      <section className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="island-kicker m-0">Meta-Harness Evaluation</p>
          <h1 className="m-0 text-3xl font-bold">Benchmarks Console</h1>
          <p className="mt-2 max-w-3xl text-sm text-[var(--sea-ink-soft)]">
            Benchy-style live reports for capability proof runs, model-fit
            tests, and harness ratchets.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-[var(--line)] bg-[var(--surface-strong)] px-3 py-2 text-sm font-semibold shadow-sm">
            <Upload size={16} />
            Load JSON
            <input
              className="sr-only"
              type="file"
              accept="application/json,.json"
              onChange={(event) => {
                const file = event.currentTarget.files?.[0];
                if (file) {
                  void readReportFile(file, setReport, setRunStatus);
                }
                event.currentTarget.value = "";
              }}
            />
          </label>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg border border-[var(--line)] bg-[var(--lagoon)] px-3 py-2 text-sm font-semibold text-white shadow-sm disabled:cursor-wait disabled:opacity-70"
            disabled={runStatus.state === "running"}
            onClick={async () => {
              setRunStatus({
                state: "running",
                message: "Running registered FastAPI sidecar job...",
              });
              try {
                const result =
                  (await runCodebaseContextProof()) as CodebaseContextProofResult;
                const proofPassed =
                  result.report.verification.status === "passed";
                setReport(result.report);
                setPlaybackStep(null);
                setRunStatus({
                  state: proofPassed ? "passed" : "failed",
                  message: result.report.verification.message,
                  artifact: result.artifact,
                });
              } catch (error) {
                setRunStatus({
                  state: "failed",
                  message:
                    error instanceof Error
                      ? error.message
                      : "Golden Path 001 failed.",
                });
              }
            }}
          >
            <Play size={16} />
            Run Proof
          </button>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg border border-[var(--line)] bg-[var(--surface-strong)] px-3 py-2 text-sm font-semibold shadow-sm"
            onClick={() =>
              setPlaybackStep((current) =>
                current === null ? 0 : Math.min(stepCount, current + 1),
              )
            }
          >
            <Play size={16} />
            Step
          </button>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg border border-[var(--line)] bg-[var(--surface-strong)] px-3 py-2 text-sm font-semibold shadow-sm"
            onClick={() => {
              setReport(SAMPLE_REPORT);
              setPlaybackStep(null);
              setRunStatus({
                state: "idle",
                message: "Showing the synthetic sample report. Not live proof.",
              });
            }}
          >
            <RefreshCw size={16} />
            Reset
          </button>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-4">
        <MetricTile label="Models" value={String(summary.modelCount)} />
        <MetricTile label="Runs" value={String(summary.runCount)} />
        <MetricTile
          label="Pass rate"
          value={`${Math.round(summary.passRate * 100)}%`}
        />
        <MetricTile label="Best score" value={summary.bestScore.toFixed(2)} />
      </section>

      <section className="island-shell rounded-lg p-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="m-0 text-lg font-bold">Live Harness Run</h2>
            <p className="m-0 mt-1 text-sm text-[var(--sea-ink-soft)]">
              {runStatus.message}
            </p>
          </div>
          <span className="inline-flex w-fit items-center rounded-full border border-[var(--line)] bg-[var(--chip-bg)] px-3 py-1 text-xs font-semibold uppercase text-[var(--sea-ink-soft)]">
            {runStatus.state}
          </span>
        </div>
        {runStatus.artifact ? (
          <code className="mt-3 block rounded-lg border border-[var(--line)] bg-[rgba(23,58,64,0.08)] p-3 text-xs">
            {runStatus.artifact}
          </code>
        ) : null}
      </section>

      <section className="island-shell rounded-lg p-4">
        <div className="flex flex-col gap-2 border-b border-[var(--line)] pb-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 className="m-0 text-xl font-bold">{report.benchmark_name}</h2>
            <p className="m-0 mt-1 text-sm text-[var(--sea-ink-soft)]">
              {report.purpose}
            </p>
            <p className="m-0 mt-2 text-xs font-semibold uppercase tracking-wide text-[var(--sea-ink-soft)]">
              {report.provenance.label} · {report.verification.message}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase ${
                report.provenance.trust === "live_verified"
                  ? "border-[rgba(46,125,50,0.25)] bg-[rgba(46,125,50,0.12)] text-[rgb(46,125,50)]"
                  : report.provenance.trust === "live_failed"
                    ? "border-[rgba(183,28,28,0.25)] bg-[rgba(183,28,28,0.12)] text-[rgb(183,28,28)]"
                    : "border-[rgba(191,87,0,0.25)] bg-[rgba(191,87,0,0.12)] text-[rgb(140,72,0)]"
              }`}
            >
              {report.provenance.trust.replaceAll("_", " ")}
            </span>
            <div className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-[var(--chip-bg)] px-3 py-1 text-xs font-semibold text-[var(--sea-ink-soft)]">
              <Zap size={14} />
              Step {Math.min(activeStep, stepCount)} / {stepCount}
            </div>
          </div>
        </div>

        <div className="mt-4 space-y-4">
          {report.models.map((model) => (
            <ModelRow
              key={`${model.provider ?? "model"}:${model.model}`}
              model={model}
              maxLatency={maxLatency}
              activeStep={activeStep}
            />
          ))}
        </div>
      </section>

      <MetaHarnessProofPanel />

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="island-shell rounded-lg p-4">
          <div className="mb-3 flex items-center gap-2">
            <FileText size={18} />
            <h2 className="m-0 text-lg font-bold">Prompt Contract</h2>
          </div>
          <pre className="max-h-80 overflow-auto rounded-lg border border-[var(--line)] bg-[rgba(23,58,64,0.08)] p-3 text-sm whitespace-pre-wrap">
            {report.base_prompt ?? "No base prompt recorded."}
          </pre>
        </div>
        <div className="island-shell rounded-lg p-4">
          <h2 className="m-0 text-lg font-bold">Promotion Gate</h2>
          <ul className="mt-3 space-y-2 pl-5 text-sm text-[var(--sea-ink-soft)]">
            <li>Capability starts at zero until one proof run passes.</li>
            <li>
              Report evidence must include invocation, outcome, verifier, and
              artifact path.
            </li>
            <li>
              Registry promotion happens only after the manifest points to that
              evidence.
            </li>
            <li>
              Future Python runner should write the same report shape to
              Pixeltable.
            </li>
          </ul>
        </div>
      </section>
    </main>
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

function ModelRow({
  model,
  maxLatency,
  activeStep,
}: {
  model: ModelReport;
  maxLatency: number;
  activeStep: number;
}) {
  const visibleResults = model.results.slice(0, activeStep);
  const passCount = visibleResults.filter((result) => result.success).length;
  const avgScore =
    visibleResults.length === 0
      ? 0
      : visibleResults.reduce(
          (sum, result) => sum + (result.score ?? (result.success ? 1 : 0)),
          0,
        ) / visibleResults.length;

  return (
    <div className="rounded-lg border border-[var(--line)] bg-[rgba(255,255,255,0.36)] p-3">
      <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="m-0 text-base font-bold">{model.model}</h3>
          <p className="m-0 text-xs text-[var(--sea-ink-soft)]">
            {model.provider ?? "provider unknown"}
          </p>
        </div>
        <div className="text-sm font-semibold">
          {passCount}/{visibleResults.length || model.results.length} passed ·{" "}
          {avgScore.toFixed(2)}
        </div>
      </div>
      <div className="grid gap-2">
        {model.results.map((result, index) => {
          const shown = index < activeStep;
          const width = Math.max(
            7,
            Math.round((result.latency_ms / maxLatency) * 100),
          );
          const resultKey = `${model.model}:${result.prompt}:${result.latency_ms}:${result.success}`;
          return (
            <div
              key={resultKey}
              className="grid grid-cols-[minmax(8rem,14rem)_1fr_4.5rem] items-center gap-3 text-sm"
            >
              <span className="truncate text-[var(--sea-ink-soft)]">
                {result.prompt}
              </span>
              <div className="h-7 rounded-md border border-[var(--line)] bg-[rgba(23,58,64,0.08)]">
                {shown ? (
                  <div
                    className={`h-full rounded-md ${result.success ? "bg-[var(--lagoon)]" : "bg-[var(--destructive)]"}`}
                    style={{ width: `${width}%` }}
                  />
                ) : null}
              </div>
              <span className="text-right font-semibold">
                {shown ? `${(result.latency_ms / 1000).toFixed(1)}s` : "queued"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

async function readReportFile(
  file: File,
  setReport: (report: BenchmarkReport) => void,
  setRunStatus: (status: {
    state: "idle" | "running" | "passed" | "failed";
    message: string;
    artifact?: string;
  }) => void,
) {
  const text = await file.text();
  const parsed = JSON.parse(text) as BenchmarkReport;
  const result = (await validateBenchmarkReport({
    data: { report: parsed },
  })) as {
    report: BenchmarkReport;
    verification?: {
      status?: "unverified" | "passed" | "failed";
      message?: string;
    };
  };
  setReport(result.report as BenchmarkReport);
  setRunStatus({
    state:
      result.verification?.status === "passed"
        ? "passed"
        : result.verification?.status === "failed"
          ? "failed"
          : "idle",
    message:
      typeof result.verification?.message === "string"
        ? result.verification.message
        : "Uploaded report loaded as unverified evidence.",
  });
}

function summarizeReport(report: BenchmarkReport) {
  const results = report.models.flatMap((model) => model.results);
  const passCount = results.filter((result) => result.success).length;
  const scored = results.map(
    (result) => result.score ?? (result.success ? 1 : 0),
  );
  return {
    modelCount: report.models.length,
    runCount: results.length,
    passRate: results.length === 0 ? 0 : passCount / results.length,
    bestScore: scored.length === 0 ? 0 : Math.max(...scored),
  };
}
