import type { AgentId } from "./agent-event";

export interface AgentMessage {
  id: string;
  threadId: string;
  sourceAgent: AgentId;
  targetAgent: AgentId;
  content: string;
  createdAt: string;
}
