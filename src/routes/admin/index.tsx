import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import {
  type CapabilityMatrixPayload,
  type CapabilityRegistry,
  type CapabilityRow,
  listCapabilityMatrix,
} from "#/server/harness/list-capability-matrix";

export const Route = createFileRoute("/admin/")({
  component: AdminPage,
});

const statusClassName: Record<"green" | "amber" | "red", string> = {
  green:
    "border-emerald-300/60 bg-emerald-500/10 text-emerald-700 dark:text-emerald-200",
  amber:
    "border-amber-300/60 bg-amber-500/10 text-amber-700 dark:text-amber-200",
  red: "border-rose-300/60 bg-rose-500/10 text-rose-700 dark:text-rose-200",
};

function AdminPage() {
  const [payload, setPayload] = useState<CapabilityMatrixPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listCapabilityMatrix()
      .then((result) => {
        if (cancelled) return;
        setPayload(result);
      })
      .catch((caught: unknown) => {
        if (cancelled) return;
        setError(
          caught instanceof Error
            ? caught.message
            : "Failed to load DDC capability registry.",
        );
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const registry = useMemo<CapabilityRegistry | null>(
    () => payload?.registries.find((entry) => entry.tool === "ddc") ?? null,
    [payload],
  );
  const capabilities = registry?.capabilities ?? [];
  const summary = useMemo(() => summarizeCapabilities(capabilities), [capabilities]);
  const surfaces = useMemo(() => collectSurfaces(capabilities), [capabilities]);

  return (
    <main className="page-wrap space-y-6 px-4 pb-8 pt-14">
      <section className="island-shell rounded-[2rem] px-6 py-8 sm:px-8">
        <p className="island-kicker mb-3">DDC capability harvest</p>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl space-y-3">
            <h1 className="display-title text-4xl font-bold tracking-tight text-[var(--sea-ink)] sm:text-5xl">
              Full DDC capability matrix
            </h1>
            <p className="text-sm leading-7 text-[var(--sea-ink-soft)] sm:text-base">
              This page renders the live DDC registry contract directly from the
              backend capability matrix so operator status, dependencies, and
              proof links stay aligned with the source of truth.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <SummaryCard
              label="Capabilities"
              value={String(summary.capabilityCount)}
            />
            <SummaryCard
              label="Registry surfaces"
              value={String(summary.surfaceCount)}
            />
            <SummaryCard
              label="Registry green"
              value={String(summary.greenCount)}
            />
            <SummaryCard
              label="Amber / red"
              value={`${summary.amberCount} / ${summary.redCount}`}
            />
          </div>
        </div>
      </section>

      {error ? (
        <section className="rounded-lg border border-[var(--destructive)] bg-[rgba(148,27,27,0.12)] p-4 text-sm">
          {error}
        </section>
      ) : null}

      {!registry && !error ? (
        <section className="island-shell rounded-lg p-4 text-sm text-[var(--sea-ink-soft)]">
          Loading DDC capability registry...
        </section>
      ) : null}

      {registry ? (
        <>
          <section className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
            <article className="island-shell rounded-2xl p-5 xl:col-span-2">
              <p className="island-kicker mb-2">Registry source</p>
              <h2 className="text-lg font-semibold text-[var(--sea-ink)]">
                {registry.tool}
              </h2>
              <p className="mt-3 text-sm text-[var(--sea-ink-soft)]">
                Canonical docs and source paths are rendered from the live
                registry payload instead of a separate frontend shadow file.
              </p>
              <code className="mt-4 block whitespace-normal break-all text-xs">
                {registry.registry_path}
              </code>
              {registry.canonical_docs ? (
                <code className="mt-2 block whitespace-normal break-all text-xs">
                  {registry.canonical_docs}
                </code>
              ) : null}
            </article>

            {surfaces.map((surface) => (
              <article key={surface.id} className="island-shell rounded-2xl p-5">
                <p className="island-kicker mb-2">surface</p>
                <h2 className="text-lg font-semibold text-[var(--sea-ink)]">
                  {surface.label}
                </h2>
                <p className="mt-3 text-sm text-[var(--sea-ink-soft)]">
                  {surface.count} {surface.count === 1 ? "capability" : "capabilities"}
                </p>
              </article>
            ))}
          </section>

          <section className="island-shell overflow-hidden rounded-[2rem]">
            <div className="border-b border-[var(--line)] px-6 py-4">
              <p className="island-kicker mb-1">Capability matrix</p>
              <h2 className="text-2xl font-semibold text-[var(--sea-ink)]">
                Registry-backed operator view
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse text-left text-sm">
                <thead className="bg-white/40">
                  <tr>
                    {[
                      "Capability",
                      "Registry status",
                      "Surface",
                      "Description",
                      "Dependencies",
                      "Proof",
                      "Wired at",
                    ].map((heading) => (
                      <th
                        key={heading}
                        className="px-4 py-3 font-semibold text-[var(--sea-ink)]"
                      >
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {capabilities.map((capability) => {
                    const declaredColor = capability.declared_status_color ?? capability.status.color;
                    return (
                      <tr
                        key={capability.id}
                        className="border-t border-[var(--line)] align-top"
                      >
                        <td className="px-4 py-3">
                          <div className="font-semibold text-[var(--sea-ink)]">
                            {capability.name ?? capability.id}
                          </div>
                          <div className="mt-1 text-xs text-[var(--sea-ink-soft)]">
                            {capability.id}
                          </div>
                          {capability.project_target ? (
                            <div className="mt-2 text-xs text-[var(--sea-ink-soft)]">
                              Target: {capability.project_target}
                            </div>
                          ) : null}
                          {capability.proof_lineage?.length ? (
                            <div className="mt-1 text-xs text-[var(--sea-ink-soft)]">
                              Lineage: {capability.proof_lineage.join(" | ")}
                            </div>
                          ) : null}
                          {capability.follow_on ? (
                            <div className="mt-2 text-xs text-[var(--sea-ink-soft)]">
                              Follow on: {capability.follow_on}
                            </div>
                          ) : null}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${statusClassName[declaredColor]}`}
                          >
                            {declaredColor}
                          </span>
                          <div className="mt-2 text-xs text-[var(--sea-ink-soft)]">
                            Diagnostic: {capability.status.label}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-[var(--sea-ink-soft)]">
                          {formatSurface(capability.surface)}
                        </td>
                        <td className="px-4 py-3 text-[var(--sea-ink-soft)]">
                          {capability.description}
                        </td>
                        <td className="px-4 py-3 text-[var(--sea-ink-soft)]">
                          <DependencyList
                            label="Supported by"
                            values={capability.supported_by}
                          />
                          <DependencyList
                            label="Blocked by"
                            values={capability.blocking_capabilities}
                          />
                        </td>
                        <td className="px-4 py-3 text-[var(--sea-ink-soft)]">
                          {capability.proof_evidence.length ? (
                            <div className="space-y-1">
                              {capability.proof_evidence.map((path) => (
                                <code
                                  key={path}
                                  className="block whitespace-normal break-all text-xs"
                                >
                                  {path}
                                </code>
                              ))}
                            </div>
                          ) : (
                            <span className="text-xs">No proof artifact recorded.</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="space-y-1">
                            {capability.wired_at.map((path) => (
                              <code
                                key={path}
                                className="block whitespace-normal break-all text-xs text-[var(--sea-ink-soft)]"
                              >
                                {path}
                              </code>
                            ))}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}

function collectSurfaces(capabilities: CapabilityRow[]) {
  return Array.from(
    capabilities.reduce(
      (map, capability) =>
        map.set(capability.surface ?? "unspecified", {
          id: capability.surface ?? "unspecified",
          label: formatSurface(capability.surface),
          count: (map.get(capability.surface ?? "unspecified")?.count ?? 0) + 1,
        }),
      new Map<string, { id: string; label: string; count: number }>(),
    ).values(),
  ).sort((left, right) => right.count - left.count || left.label.localeCompare(right.label));
}

function summarizeCapabilities(capabilities: CapabilityRow[]) {
  return capabilities.reduce(
    (summary, capability) => {
      const color = capability.declared_status_color ?? capability.status.color;
      summary.capabilityCount += 1;
      if (color === "green") summary.greenCount += 1;
      if (color === "amber") summary.amberCount += 1;
      if (color === "red") summary.redCount += 1;
      summary.surfaceIds.add(capability.surface ?? "unspecified");
      summary.surfaceCount = summary.surfaceIds.size;
      return summary;
    },
    {
      capabilityCount: 0,
      surfaceCount: 0,
      greenCount: 0,
      amberCount: 0,
      redCount: 0,
      surfaceIds: new Set<string>(),
    },
  );
}

function formatSurface(surface?: string) {
  if (!surface) return "Unspecified";
  return surface.replace(/[_-]/g, " ");
}

function DependencyList({
  label,
  values,
}: {
  label: string;
  values?: string[];
}) {
  if (!values?.length) return null;
  return (
    <div className="mb-2">
      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--sea-ink-soft)]">
        {label}
      </div>
      <div className="mt-1 flex flex-wrap gap-1">
        {values.map((value) => (
          <code
            key={`${label}-${value}`}
            className="rounded-full border border-[var(--line)] bg-white/35 px-2 py-1 text-xs"
          >
            {value}
          </code>
        ))}
      </div>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[var(--line)] bg-white/35 px-4 py-3 text-left">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--sea-ink-soft)]">
        {label}
      </div>
      <div className="mt-2 text-2xl font-bold text-[var(--sea-ink)]">
        {value}
      </div>
    </div>
  );
}
