import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/settings/providers")({
  component: ProvidersSettingsPage,
});

function ProvidersSettingsPage() {
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">Provider Settings</h1>
      <p className="text-sm mt-2">
        OpenRouter is configured via server environment variables and never
        exposed to browser code.
      </p>
    </main>
  );
}
