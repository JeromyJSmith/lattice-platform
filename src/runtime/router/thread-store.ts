import { Store } from "@tanstack/store";

export interface RuntimeThreadState {
  activeThreadId: string | null;
  selectedAgent: "claude-code" | "pi" | "hermes" | "openrouter";
}

export const threadStore = new Store<RuntimeThreadState>({
  activeThreadId: null,
  selectedAgent: "claude-code",
});
