import { createFileRoute } from "@tanstack/react-router";
import { streamEvents } from "#/server/runtime/stream-events";

export const Route = createFileRoute("/api/runtime/stream-events")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const runId = new URL(request.url).searchParams.get("runId") ?? "";
        const result = await streamEvents({ data: { runId } });
        return Response.json(result);
      },
    },
  },
});
