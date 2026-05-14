import { createFileRoute } from "@tanstack/react-router";
import { getPixeltableIngestionStatus } from "#/runtime/pixeltable/pixeltable-client";

export const Route = createFileRoute("/settings/pixeltable")({
  component: PixeltableSettingsPage,
});

function PixeltableSettingsPage() {
  const status = getPixeltableIngestionStatus();
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">Pixeltable Ingestion Boundary</h1>
      <pre className="mt-3 rounded border p-3 text-xs overflow-x-auto">
        {JSON.stringify(status, null, 2)}
      </pre>
    </main>
  );
}
