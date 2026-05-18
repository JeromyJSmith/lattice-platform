import { createFileRoute } from "@tanstack/react-router";
import { loadMetaProofDashboard } from "#/server/harness/load-meta-proof-dashboard";

export const Route = createFileRoute("/api/harness/meta-proof-dashboard")({
  server: {
    handlers: {
      GET: async () => {
        const result = await loadMetaProofDashboard();
        return new Response(JSON.stringify(result), {
          headers: {
            "content-type": "application/json",
            "cache-control": "no-store",
          },
        });
      },
    },
  },
});
