import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { runsQueryOptions } from "#/queries/runtime-queries";
import { RunsTable } from "#/tables/runs-table";

export const Route = createFileRoute("/runs/")({
  component: RunsPage,
});

function RunsPage() {
  const runs = useQuery(runsQueryOptions);
  const rows = (runs.data ?? []).map((id) => ({ id }));
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold mb-3">Run History</h1>
      <RunsTable runs={rows} />
    </main>
  );
}
