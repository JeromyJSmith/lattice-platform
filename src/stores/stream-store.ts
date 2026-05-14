import { Store } from "@tanstack/store";

export const streamStore = new Store({
  isStreaming: false,
  lastEventText: "",
});
