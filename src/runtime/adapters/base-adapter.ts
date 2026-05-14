import type { RuntimeEvent } from "../protocol/agent-event";

export interface RuntimeAdapter {
  id: string;
  run(input: {
    threadId: string;
    prompt: string;
  }): AsyncGenerator<RuntimeEvent>;
}
