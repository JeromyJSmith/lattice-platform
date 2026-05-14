import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/settings/intent")({
  component: IntentSettingsPage,
});

function IntentSettingsPage() {
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">TanStack Intent Skills</h1>
      <p className="text-sm mt-2">
        Run <code>bun run intent:list</code> to refresh package skill discovery
        output.
      </p>
    </main>
  );
}
