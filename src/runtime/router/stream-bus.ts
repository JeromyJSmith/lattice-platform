import type { RuntimeEvent } from "../protocol/agent-event";

type Listener = (event: RuntimeEvent) => void;

const listeners = new Set<Listener>();

export function emitRuntimeEvent(event: RuntimeEvent) {
  for (const listener of listeners) listener(event);
}

export function subscribeRuntimeEvents(listener: Listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
