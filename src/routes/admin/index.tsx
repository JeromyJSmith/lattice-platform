import { createFileRoute } from "@tanstack/react-router";
import {
  ddcCapabilities,
  ddcCapabilityArtifactPath,
  ddcExclusions,
  ddcPipelineStages,
  ddcSummary,
  ddcSurfaces,
} from "#/data/ddc-capability-matrix";

export const Route = createFileRoute("/admin/")({
  component: AdminPage,
});

const priorityClassName: Record<string, string> = {
  high: "border-rose-300/60 bg-rose-500/10 text-rose-700 dark:text-rose-200",
  medium:
    "border-amber-300/60 bg-amber-500/10 text-amber-700 dark:text-amber-200",
  low: "border-emerald-300/60 bg-emerald-500/10 text-emerald-700 dark:text-emerald-200",
};

const statusClassName: Record<string, string> = {
  green:
    "border-emerald-300/60 bg-emerald-500/10 text-emerald-700 dark:text-emerald-200",
  amber:
    "border-amber-300/60 bg-amber-500/10 text-amber-700 dark:text-amber-200",
  red: "border-rose-300/60 bg-rose-500/10 text-rose-700 dark:text-rose-200",
};

function AdminPage() {
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
              This page maps every planned DataDrivenConstruction capability to
              its local LATTICE home, runtime target, current implementation
              state, delivery wave, and validation signal.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <SummaryCard
              label="Capabilities"
              value={String(ddcSummary.capabilityCount)}
            />
            <SummaryCard
              label="Integration surfaces"
              value={String(ddcSummary.surfaceCount)}
            />
            <SummaryCard
              label="Green now"
              value={String(ddcSummary.greenCount)}
            />
            <SummaryCard
              label="Amber / red"
              value={`${ddcSummary.amberCount} / ${ddcSummary.redCount}`}
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
        {ddcSurfaces.map((surface) => (
          <article key={surface.id} className="island-shell rounded-2xl p-5">
            <p className="island-kicker mb-2">{surface.classification}</p>
            <h2 className="text-lg font-semibold text-[var(--sea-ink)]">
              {surface.name}
            </h2>
            <p className="mt-3 text-sm text-[var(--sea-ink-soft)]">
              Adoption mode:{" "}
              <span className="font-semibold text-[var(--sea-ink)]">
                {surface.adoptionMode}
              </span>
            </p>
            <code className="mt-4 block whitespace-normal break-all text-xs">
              {surface.localHome}
            </code>
          </article>
        ))}
      </section>

      <section className="island-shell overflow-hidden rounded-[2rem]">
        <div className="border-b border-[var(--line)] px-6 py-4">
          <p className="island-kicker mb-1">Capability matrix</p>
          <h2 className="text-2xl font-semibold text-[var(--sea-ink)]">
            Mapped scope and delivery order
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-left text-sm">
            <thead className="bg-white/40">
              <tr>
                {[
                  "Capability",
                  "Status",
                  "Priority",
                  "Wave",
                  "Current state",
                  "Gap",
                  "Validation",
                  "Local home",
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
              {ddcCapabilities.map((capability) => (
                <tr
                  key={capability.id}
                  className="border-t border-[var(--line)] align-top"
                >
                  <td className="px-4 py-3">
                    <div className="font-semibold text-[var(--sea-ink)]">
                      {capability.capability}
                    </div>
                    <div className="mt-1 text-xs text-[var(--sea-ink-soft)]">
                      {capability.targetSurface}
                    </div>
                    {capability.projectTarget ? (
                      <div className="mt-2 text-xs text-[var(--sea-ink-soft)]">
                        Target: {capability.projectTarget}
                      </div>
                    ) : null}
                    {capability.proofLineage ? (
                      <div className="mt-1 text-xs text-[var(--sea-ink-soft)]">
                        Lineage: {capability.proofLineage}
                      </div>
                    ) : null}
                    {capability.supportedBy?.length ? (
                      <div className="mt-1 text-xs text-[var(--sea-ink-soft)]">
                        Helping now: {capability.supportedBy.join(", ")}
                      </div>
                    ) : null}
                    {capability.blockedBy?.length ? (
                      <div className="mt-1 text-xs text-[var(--sea-ink-soft)]">
                        Blocking now: {capability.blockedBy.join(", ")}
                      </div>
                    ) : null}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${statusClassName[capability.status]}`}
                    >
                      {capability.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${priorityClassName[capability.priority]}`}
                    >
                      {capability.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-[var(--sea-ink)]">
                    {capability.wave}
                  </td>
                  <td className="px-4 py-3 text-[var(--sea-ink-soft)]">
                    {capability.currentState}
                  </td>
                  <td className="px-4 py-3 text-[var(--sea-ink-soft)]">
                    {capability.gap}
                  </td>
                  <td className="px-4 py-3 text-[var(--sea-ink-soft)]">
                    {capability.validation}
                  </td>
                  <td className="px-4 py-3">
                    <code className="whitespace-normal break-all text-xs">
                      {capability.localHome}
                    </code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.5fr_1fr]">
        <article className="island-shell rounded-[2rem] p-6">
          <p className="island-kicker mb-2">Execution pipeline</p>
          <h2 className="text-2xl font-semibold text-[var(--sea-ink)]">
            Wave-by-wave integration path
          </h2>
          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            {ddcPipelineStages.map((stage) => (
              <div
                key={stage.id}
                className="rounded-2xl border border-[var(--line)] bg-white/30 p-4"
              >
                <h3 className="text-lg font-semibold text-[var(--sea-ink)]">
                  {stage.id}: {stage.name}
                </h3>
                <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-[var(--sea-ink-soft)]">
                  {stage.capabilityIds.map((capabilityId) => {
                    const capability = ddcCapabilities.find(
                      (entry) => entry.id === capabilityId,
                    );
                    if (!capability) return null;
                    return <li key={capability.id}>{capability.capability}</li>;
                  })}
                </ul>
              </div>
            ))}
          </div>
        </article>

        <article className="island-shell rounded-[2rem] p-6">
          <p className="island-kicker mb-2">Guardrails</p>
          <h2 className="text-2xl font-semibold text-[var(--sea-ink)]">
            Explicit exclusions
          </h2>
          <ul className="mt-4 list-disc space-y-3 pl-5 text-sm leading-7 text-[var(--sea-ink-soft)]">
            {ddcExclusions.map((exclusion) => (
              <li key={exclusion}>{exclusion}</li>
            ))}
          </ul>
          <p className="mt-5 text-xs text-[var(--sea-ink-soft)]">
            Canonical structured artifact:{" "}
            <code>{ddcCapabilityArtifactPath}</code>
          </p>
          <p className="mt-2 text-xs text-[var(--sea-ink-soft)]">
            Green = verifier-backed or operational now. Amber = partially wired
            and useful but still blocking the end-to-end path. Red = planned or
            dependency-missing.
          </p>
        </article>
      </section>
    </main>
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
