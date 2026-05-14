import { throttle } from "@tanstack/pacer";

export const throttledStreamUpdate = throttle((fn: () => void) => fn(), {
  wait: 100,
});
