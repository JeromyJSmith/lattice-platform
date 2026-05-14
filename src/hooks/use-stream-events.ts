import { useEffect, useState } from "react";
import type { StreamEventRow } from "#/server/runtime/list-stream-events";

/**
 * Subscribe to the sidecar's SSE stream for `runId`. Returns the accumulated
 * deltas in seq order. Re-subscribes when `runId` changes; closes the
 * EventSource on unmount and on every re-subscribe.
 *
 * The sidecar replays historical events on connect, so this hook never needs
 * a separate "initial fetch" — the first message(s) over the socket are the
 * full history, then live deltas follow.
 */
export function useStreamEvents(runId: string | null): StreamEventRow[] {
  const [events, setEvents] = useState<StreamEventRow[]>([]);

  useEffect(() => {
    setEvents([]);
    if (!runId) return;

    const base =
      (
        import.meta as ImportMeta & {
          env: { VITE_PIXELTABLE_SERVICE_URL?: string };
        }
      ).env?.VITE_PIXELTABLE_SERVICE_URL ?? "http://127.0.0.1:7770";
    const url = `${base}/v1/runtime/stream-events/sse?run_id=${encodeURIComponent(runId)}`;
    const es = new EventSource(url);
    const seen = new Set<string>();

    es.addEventListener("delta", (e) => {
      try {
        const row = JSON.parse((e as MessageEvent).data) as StreamEventRow;
        if (row.event_id && seen.has(row.event_id)) return;
        if (row.event_id) seen.add(row.event_id);
        setEvents((prev) => {
          const next = [...prev, row];
          next.sort((a, b) => a.seq - b.seq);
          return next;
        });
      } catch {
        // malformed event — drop
      }
    });

    es.addEventListener("end", () => {
      es.close();
    });

    es.onerror = () => {
      // EventSource auto-reconnects with exponential backoff; let it.
    };

    return () => {
      es.close();
    };
  }, [runId]);

  return events;
}
