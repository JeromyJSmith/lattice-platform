import { createFileRoute } from "@tanstack/react-router";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  CircleDashed,
  Play,
  Search,
  XCircle,
} from "lucide-react";
import { type ReactNode, useEffect, useMemo, useState } from "react";
import {
  type CapabilityMatrixPayload,
  type CapabilityRegistry,
  type CapabilityRow,
  listCapabilityMatrix,
} from "#/server/harness/list-capability-matrix";
import { runCapabilityProof } from "#/server/harness/run-codebase-context-proof";

export const Route = createFileRoute("/harness/capabilities")({
  component: HarnessCapabilitiesPage,
});

type RunResult = {
  state: "running" | "passed" | "failed";
  message: string;
  artifact?: string;
};

type CapabilityProofResult = {
  ok: boolean;
  artifact?: string;
};

type CapabilityFilter =
  | "all"
  | "proven"
  | "needs-proof"
  | "failing-blocked"
  | "deferred"
  | "runnable";

const CAPABILITY_FILTERS: Array<{
  id: CapabilityFilter;
  label: string;
}> = [
  { id: "all", label: "All" },
  { id: "proven", label: "Proven" },
  { id: "needs-proof", label: "Needs Proof" },
  { id: "failing-blocked", label: "Failing/Blocked" },
  { id: "deferred", label: "Deferred" },
  { id: "runnable", label: "Runnable" },
];

function HarnessCapabilitiesPage() {
  const [payload, setPayload] = useState<CapabilityMatrixPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<CapabilityFilter>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [runResults, setRunResults] = useState<Record<string, RunResult>>({});

  useEffect(() => {
    let cancelled = false;
    listCapabilityMatrix()
      .then((result) => {
        if (cancelled) return;
        setPayload(result);
        setActiveTool(result.registries[0]?.tool ?? null);
      })
      .catch((caught: unknown) => {
        if (cancelled) return;
        setError(
          caught instanceof Error
            ? caught.message
            : "Failed to load capability matrix.",
        );
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const activeRegistry = useMemo(
    () =>
      payload?.registries.find((registry) => registry.tool === activeTool) ??
      payload?.registries[0],
    [activeTool, payload],
  );

  async function runCapability(capability: CapabilityRow) {
    setRunResults((current) => ({
      ...current,
      [capability.id]: {
        state: "running",
        message: "Running proof through FastAPI sidecar...",
      },
    }));
    try {
      const result = (await runCapabilityProof({
        data: { capabilityId: capability.id },
      })) as CapabilityProofResult;
      setRunResults((current) => ({
        ...current,
        [capability.id]: {
          state: result.ok ? "passed" : "failed",
          message: result.ok ? "Proof passed." : "Proof returned a failure.",
          artifact: result.artifact,
        },
      }));
    } catch (caught) {
      setRunResults((current) => ({
        ...current,
        [capability.id]: {
          state: "failed",
          message:
            caught instanceof Error
              ? caught.message
              : "Capability proof failed.",
        },
      }));
    }
  }

  return (
    <main className="page-wrap px-4 pb-8 pt-14 space-y-5">
      <section className="flex flex-col gap-2">
        <p className="island-kicker m-0">Meta-Harness Pre-Flight</p>
        <h1 className="m-0 text-3xl font-bold">Capability Matrix</h1>
        <p className="m-0 max-w-3xl text-sm text-[var(--sea-ink-soft)]">
          Registry contracts, proof evidence, connected surfaces, and runnable
          diagnostics for each source program and repository.
        </p>
      </section>

      {error ? (
        <section className="rounded-lg border border-[var(--destructive)] bg-[rgba(148,27,27,0.12)] p-4 text-sm">
          {error}
        </section>
      ) : null}

      {payload ? (
        <>
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <MetricTile
              label="Total"
              value={String(payload.summary.total)}
              tone="neutral"
            />
            <MetricTile
              label="Proven"
              value={String(payload.summary.green)}
              tone="green"
            />
            <MetricTile
              label="Needs Proof / Deferred"
              value={String(payload.summary.amber)}
              tone="amber"
            />
            <MetricTile
              label="Fail / Blocked"
              value={String(payload.summary.red)}
              tone="red"
            />
          </section>

          <section className="flex flex-wrap gap-2 pb-1">
            {payload.registries.map((registry) => (
              <button
                key={registry.tool}
                type="button"
                className={`whitespace-nowrap rounded-lg border px-3 py-2 text-sm font-semibold ${
                  registry.tool === activeRegistry?.tool
                    ? "border-[var(--lagoon)] bg-[var(--chip-bg)] text-[var(--sea-ink)]"
                    : "border-[var(--line)] bg-[var(--surface-strong)] text-[var(--sea-ink-soft)]"
                }`}
                onClick={() => setActiveTool(registry.tool)}
              >
                {registry.tool}
              </button>
            ))}
          </section>

          {activeRegistry ? (
            <RegistryPanel
              registry={activeRegistry}
              activeFilter={activeFilter}
              searchQuery={searchQuery}
              runResults={runResults}
              onFilterChange={setActiveFilter}
              onSearchChange={setSearchQuery}
              onRun={runCapability}
            />
          ) : null}
        </>
      ) : (
        <section className="island-shell rounded-lg p-4 text-sm text-[var(--sea-ink-soft)]">
          Loading capability registries...
        </section>
      )}
    </main>
  );
}

function RegistryPanel({
  registry,
  activeFilter,
  searchQuery,
  runResults,
  onFilterChange,
  onSearchChange,
  onRun,
}: {
  registry: CapabilityRegistry;
  activeFilter: CapabilityFilter;
  searchQuery: string;
  runResults: Record<string, RunResult>;
  onFilterChange: (filter: CapabilityFilter) => void;
  onSearchChange: (query: string) => void;
  onRun: (capability: CapabilityRow) => void;
}) {
  const normalizedSearch = searchQuery.trim().toLowerCase();
  const searchedCapabilities = useMemo(
    () =>
      registry.capabilities.filter((capability) =>
        matchesCapabilitySearch(capability, registry.tool, normalizedSearch),
      ),
    [normalizedSearch, registry.capabilities, registry.tool],
  );
  const filterCounts = useMemo(() => {
    return Object.fromEntries(
      CAPABILITY_FILTERS.map((filter) => [
        filter.id,
        searchedCapabilities.filter((capability) =>
          matchesCapabilityFilter(capability, filter.id),
        ).length,
      ]),
    ) as Record<CapabilityFilter, number>;
  }, [searchedCapabilities]);
  const visibleCapabilities = useMemo(
    () =>
      searchedCapabilities.filter((capability) =>
        matchesCapabilityFilter(capability, activeFilter),
      ),
    [activeFilter, searchedCapabilities],
  );

  return (
    <section className="space-y-3">
      <div className="flex flex-col gap-2 border-b border-[var(--line)] pb-3">
        <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <h2 className="m-0 break-words text-xl font-bold">
              {registry.tool}
            </h2>
            <p className="m-0 mt-1 break-all text-sm text-[var(--sea-ink-soft)]">
              {registry.registry_path}
            </p>
          </div>
          <span className="inline-flex w-fit rounded-full border border-[var(--line)] bg-[var(--chip-bg)] px-3 py-1 text-xs font-semibold text-[var(--sea-ink-soft)]">
            {registry.capabilities.length} capabilities
          </span>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-[var(--sea-ink-soft)]">
          {registry.tool_version ? (
            <code className="break-all">version {registry.tool_version}</code>
          ) : null}
          {registry.source_mirror ? (
            <code className="break-all">{registry.source_mirror}</code>
          ) : null}
          {registry.canonical_docs ? (
            <code className="break-all">{registry.canonical_docs}</code>
          ) : null}
        </div>
      </div>

      <div className="island-shell rounded-lg p-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-2">
            {CAPABILITY_FILTERS.map((filter) => (
              <button
                key={filter.id}
                type="button"
                className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold ${
                  activeFilter === filter.id
                    ? "border-[var(--lagoon)] bg-[var(--chip-bg)] text-[var(--sea-ink)]"
                    : "border-[var(--line)] bg-[var(--surface-strong)] text-[var(--sea-ink-soft)]"
                }`}
                onClick={() => onFilterChange(filter.id)}
              >
                <span>{filter.label}</span>
                <span className="rounded-full border border-[var(--line)] bg-[rgba(23,58,64,0.06)] px-1.5 py-0.5 text-[0.68rem]">
                  {filterCounts[filter.id]}
                </span>
              </button>
            ))}
          </div>
          <label className="relative min-w-0 lg:w-80">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--sea-ink-soft)]"
              size={16}
            />
            <input
              type="search"
              value={searchQuery}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="Search id, name, description, tool"
              className="w-full rounded-lg border border-[var(--line)] bg-[var(--surface-strong)] py-2 pl-9 pr-3 text-sm text-[var(--sea-ink)] outline-none ring-0 placeholder:text-[var(--sea-ink-soft)] focus:border-[var(--lagoon)]"
            />
          </label>
        </div>
        <p className="m-0 mt-2 text-xs text-[var(--sea-ink-soft)]">
          Showing {visibleCapabilities.length} of {registry.capabilities.length}
          {normalizedSearch ? " matching" : ""} capabilities.
        </p>
      </div>

      <div className="space-y-2">
        {visibleCapabilities.length ? (
          visibleCapabilities.map((capability) => (
            <CapabilityDisclosure
              key={capability.id}
              capability={capability}
              runResult={runResults[capability.id]}
              onRun={onRun}
            />
          ))
        ) : (
          <div className="rounded-lg border border-[var(--line)] bg-[var(--surface-strong)] p-4 text-sm text-[var(--sea-ink-soft)]">
            No capabilities match the current filter and search.
          </div>
        )}
      </div>
    </section>
  );
}

function CapabilityDisclosure({
  capability,
  runResult,
  onRun,
}: {
  capability: CapabilityRow;
  runResult?: RunResult;
  onRun: (capability: CapabilityRow) => void;
}) {
  return (
    <details
      className={`group rounded-lg border p-3 shadow-sm ${rowToneClass(capability.status.color, capability.status.label)}`}
    >
      <summary className="grid cursor-pointer list-none gap-3 marker:hidden md:grid-cols-[auto_minmax(0,1.4fr)_minmax(0,0.9fr)_minmax(0,1fr)_auto] md:items-center [&::-webkit-details-marker]:hidden">
        <StatusPill
          color={capability.status.color}
          label={capability.status.label}
        />
        <div className="min-w-0">
          <div className="break-words font-semibold">
            {capability.name ?? capability.id}
          </div>
          <div className="mt-1 break-all text-xs text-[var(--sea-ink-soft)]">
            {capability.id}
          </div>
        </div>
        <div className="min-w-0 text-xs">
          <code className="break-words">{capability.surface ?? "unknown"}</code>
          <div className="mt-1 font-semibold uppercase text-[var(--sea-ink-soft)]">
            {capability.state ?? "missing"}
          </div>
        </div>
        <div className="min-w-0 text-xs text-[var(--sea-ink-soft)]">
          <span className="font-semibold text-[var(--sea-ink)]">Serves </span>
          <span className="break-words">
            {capability.serves.length
              ? capability.serves.slice(0, 3).join(", ")
              : "unmapped"}
            {capability.serves.length > 3
              ? ` +${capability.serves.length - 3}`
              : ""}
          </span>
        </div>
        <ChevronDown
          className="self-start justify-self-end transition group-open:rotate-180 md:self-center"
          size={18}
        />
      </summary>

      <div className="mt-4 grid gap-4 border-t border-[var(--line)] pt-4 lg:grid-cols-2 xl:grid-cols-3">
        <DetailBlock title="Contract">
          <PathList
            paths={capability.wired_at}
            empty="No contract wires recorded."
          />
        </DetailBlock>
        <DetailBlock title="Proof Evidence">
          <PathList
            paths={capability.proof_evidence}
            empty="No proof evidence recorded."
          />
        </DetailBlock>
        <DetailBlock title="Serves / Connected To">
          <PillList
            items={capability.serves}
            empty="No served surface mapped."
          />
        </DetailBlock>
        <DetailBlock title="Invoked By">
          <PillList
            items={capability.invoked_by}
            empty="No invocation path recorded."
          />
        </DetailBlock>
        <DetailBlock title="Troubleshooting">
          <p className="m-0 text-xs leading-5 text-[var(--sea-ink-soft)]">
            {capability.status.troubleshooting}
          </p>
          {capability.status.missing_wires.length ? (
            <PathList
              paths={capability.status.missing_wires}
              empty=""
              tone="red"
            />
          ) : null}
          {capability.status.missing_proof.length ? (
            <PathList
              paths={capability.status.missing_proof}
              empty=""
              tone="red"
            />
          ) : null}
        </DetailBlock>
        <DetailBlock title="Action">
          {capability.run_action ? (
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="inline-flex w-fit items-center gap-2 rounded-lg border border-[var(--line)] bg-[var(--lagoon)] px-3 py-2 text-sm font-semibold text-white shadow-sm disabled:cursor-wait disabled:opacity-70"
                  disabled={runResult?.state === "running"}
                  onClick={() => onRun(capability)}
                >
                  <Play size={16} />
                  {runResult?.state === "running"
                    ? "Running..."
                    : capability.run_action.label}
                </button>
                {runResult ? (
                  <StatusPill
                    color={runResultTone(runResult.state)}
                    label={runResult.state}
                  />
                ) : (
                  <span className="rounded-full border border-[var(--line)] bg-[var(--chip-bg)] px-2 py-1 text-xs font-semibold text-[var(--sea-ink-soft)]">
                    Ready
                  </span>
                )}
              </div>
              <div className="flex min-w-0 flex-wrap gap-1 text-xs text-[var(--sea-ink-soft)]">
                <code className="break-all">{capability.run_action.kind}</code>
                <code className="break-all">
                  {capability.run_action.job_id}
                </code>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-dashed border-[var(--line)] bg-[rgba(23,58,64,0.04)] p-3">
              <p className="m-0 text-xs font-semibold text-[var(--sea-ink)]">
                Missing run contract
              </p>
              <p className="m-0 mt-1 text-xs leading-5 text-[var(--sea-ink-soft)]">
                This registry row has no <code>run_action</code>, so the console
                can show evidence but cannot execute a proof job.
              </p>
            </div>
          )}
          {runResult ? (
            <div className="mt-3 space-y-2">
              <p className="m-0 text-xs leading-5 text-[var(--sea-ink-soft)]">
                {runResult.message}
              </p>
              {runResult.artifact ? (
                <code className="block break-all rounded border border-[var(--line)] bg-[rgba(23,58,64,0.08)] px-2 py-1 text-xs">
                  {runResult.artifact}
                </code>
              ) : null}
            </div>
          ) : null}
        </DetailBlock>
      </div>
    </details>
  );
}

function matchesCapabilitySearch(
  capability: CapabilityRow,
  tool: string,
  query: string,
): boolean {
  if (!query) return true;
  return [
    capability.id,
    capability.name,
    capability.description,
    capability.surface,
    tool,
  ]
    .filter(Boolean)
    .some((value) => value?.toLowerCase().includes(query));
}

function matchesCapabilityFilter(
  capability: CapabilityRow,
  filter: CapabilityFilter,
): boolean {
  const statusLabel = capability.status.label.toLowerCase();
  const state = capability.state?.toLowerCase() ?? "";
  if (filter === "all") return true;
  if (filter === "proven") return capability.status.color === "green";
  if (filter === "needs-proof") {
    return capability.status.color === "amber" && statusLabel !== "deferred";
  }
  if (filter === "failing-blocked") {
    return (
      capability.status.color === "red" ||
      statusLabel.includes("fail") ||
      statusLabel.includes("block") ||
      state.includes("fail") ||
      state.includes("block")
    );
  }
  if (filter === "deferred") {
    return statusLabel.includes("deferred") || state.includes("deferred");
  }
  return Boolean(capability.run_action);
}

function runResultTone(state: RunResult["state"]): "green" | "amber" | "red" {
  if (state === "passed") return "green";
  if (state === "running") return "amber";
  return "red";
}

function DetailBlock({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="min-w-0">
      <h3 className="m-0 mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--sea-ink-soft)]">
        {title}
      </h3>
      {children}
    </section>
  );
}

function MetricTile({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "neutral" | "green" | "amber" | "red";
}) {
  const toneClass =
    tone === "green"
      ? "text-[var(--lagoon)]"
      : tone === "amber"
        ? "text-[var(--warning)]"
        : tone === "red"
          ? "text-[var(--destructive)]"
          : "text-[var(--sea-ink)]";
  return (
    <div className="island-shell rounded-lg p-4">
      <p className="m-0 text-xs font-semibold uppercase tracking-wide text-[var(--sea-ink-soft)]">
        {label}
      </p>
      <p className={`m-0 mt-2 text-2xl font-bold ${toneClass}`}>{value}</p>
    </div>
  );
}

function StatusPill({
  color,
  label,
}: {
  color: "green" | "amber" | "red";
  label: string;
}) {
  const Icon =
    color === "green"
      ? CheckCircle2
      : color === "amber"
        ? CircleDashed
        : XCircle;
  const colorClass =
    color === "green"
      ? "border-[var(--lagoon)] text-[var(--lagoon)]"
      : color === "amber"
        ? "border-[var(--warning)] text-[var(--warning)]"
        : "border-[var(--destructive)] text-[var(--destructive)]";
  return (
    <span
      className={`inline-flex w-fit items-center gap-1 rounded-full border px-2 py-1 text-xs font-semibold ${colorClass}`}
    >
      {color === "red" && label === "blocked" ? (
        <AlertTriangle size={13} />
      ) : (
        <Icon size={13} />
      )}
      <span className="break-words">{label}</span>
    </span>
  );
}

function PathList({
  paths,
  empty,
  tone = "neutral",
}: {
  paths: string[];
  empty: string;
  tone?: "neutral" | "red";
}) {
  if (!paths.length) {
    return <span className="text-xs text-[var(--sea-ink-soft)]">{empty}</span>;
  }
  return (
    <div className="flex min-w-0 flex-col gap-1">
      {paths.map((path) => (
        <code
          key={path}
          className={`break-all rounded border border-[var(--line)] bg-[rgba(23,58,64,0.08)] px-2 py-1 text-xs ${
            tone === "red" ? "text-[var(--destructive)]" : ""
          }`}
        >
          {path}
        </code>
      ))}
    </div>
  );
}

function PillList({ items, empty }: { items: string[]; empty: string }) {
  if (!items.length) {
    return <span className="text-xs text-[var(--sea-ink-soft)]">{empty}</span>;
  }
  return (
    <div className="flex min-w-0 flex-wrap gap-1">
      {items.map((item) => (
        <span
          key={item}
          className="min-w-0 break-words rounded-full border border-[var(--line)] bg-[var(--chip-bg)] px-2 py-1 text-xs text-[var(--sea-ink-soft)]"
        >
          {item}
        </span>
      ))}
    </div>
  );
}

function rowToneClass(color: "green" | "amber" | "red", label: string): string {
  if (color === "green") {
    return "border-[rgba(79,184,178,0.45)] bg-[rgba(79,184,178,0.08)]";
  }
  if (color === "amber") {
    return label === "deferred"
      ? "border-[rgba(65,97,102,0.18)] bg-[rgba(65,97,102,0.05)]"
      : "border-[rgba(186,122,25,0.35)] bg-[rgba(186,122,25,0.08)]";
  }
  return "border-[rgba(148,27,27,0.35)] bg-[rgba(148,27,27,0.08)]";
}
