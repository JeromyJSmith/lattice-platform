import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useStore } from "@tanstack/react-store";
import { useEffect, useMemo, useState } from "react";
import { AgentUI } from "#/ai/agent-ui";
import { TaskSubmitForm } from "#/forms/task-submit-form";
import { useStreamEvents } from "#/hooks/use-stream-events";
import { useOperatorHotkeys } from "#/hotkeys/operator-hotkeys";
import { runsQueryOptions } from "#/queries/runtime-queries";
import { dispatchRun } from "#/server/runtime/dispatch-run";
import { runtimeStore } from "#/stores/runtime-store";
import { streamStore } from "#/stores/stream-store";
import { RunsTable } from "#/tables/runs-table";
import { EventTimeline } from "#/virtual/event-timeline";

export const Route = createFileRoute("/runtime")({
  loader: ({ context }) =>
    context.queryClient.ensureQueryData(runsQueryOptions),
  component: RuntimePage,
});

function RuntimePage() {
  const runtime = useStore(runtimeStore);
  const stream = useStore(streamStore);
  const queryClient = useQueryClient();
  const [timeline, setTimeline] = useState<string[]>([]);

  useOperatorHotkeys({
    onToggleSidebar: () =>
      runtimeStore.setState((state) => ({ ...state, activeRunId: null })),
    onFocusRuntime: () =>
      setTimeline((prev) => [...prev, "hotkey: focus runtime"]),
  });

  const runs = useQuery({
    ...runsQueryOptions,
    refetchInterval: runtime.activeRunId ? 1500 : false,
    refetchIntervalInBackground: true,
  });
  const rows = runs.data ?? [];

  const deltas = useStreamEvents(runtime.activeRunId ?? null);

  const activeRunStatus = useMemo(
    () => rows.find((r) => r.run_id === runtime.activeRunId)?.status ?? null,
    [rows, runtime.activeRunId],
  );

  // Flip the global streaming flag based on the active run's status.
  useEffect(() => {
    const streaming =
      activeRunStatus === "pending" || activeRunStatus === "running";
    streamStore.setState((s) =>
      s.isStreaming === streaming ? s : { ...s, isStreaming: streaming },
    );
  }, [activeRunStatus]);

  const items = useMemo(() => {
    const deltaLines = deltas.map((e) => `[seq ${e.seq}] ${e.delta_text}`);
    return [...timeline, ...deltaLines];
  }, [timeline, deltas]);

  return (
    <main className="page-wrap px-4 pb-8 pt-14 space-y-4">
      <h1 className="text-3xl font-bold">Runtime Operator Console</h1>
      <p className="text-sm opacity-80">
        Agent: {runtime.selectedAgent} | Active run:{" "}
        {runtime.activeRunId ?? "none"} | Status: {activeRunStatus ?? "—"} |
        Streaming: {String(stream.isStreaming)} | DB rows:{" "}
        {runs.isLoading ? "…" : rows.length}
      </p>

      <TaskSubmitForm
        onSubmit={async (task) => {
          if (!task.trim()) return;
          const result = await dispatchRun({
            data: { task, threadId: runtime.activeThreadId ?? "thread-local" },
          });
          runtimeStore.setState((state) => ({
            ...state,
            activeRunId: result.runId,
          }));
          setTimeline((prev) => [
            ...prev,
            `run ${result.runId} dispatched (pending)`,
          ]);
          await queryClient.invalidateQueries({
            queryKey: ["runtime", "runs"],
          });
        }}
      />

      <RunsTable
        runs={rows}
        activeRunId={runtime.activeRunId}
        onRowClick={(row) => {
          runtimeStore.setState((state) => ({
            ...state,
            activeRunId: row.run_id,
          }));
        }}
      />
      <EventTimeline items={items} />
      <AgentUI />
    </main>
  );
}
