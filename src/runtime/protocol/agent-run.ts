import type { AgentId } from './agent-event'

export interface AgentRun {
  id: string
  threadId: string
  agentId: AgentId
  status: 'pending' | 'running' | 'completed' | 'failed'
  createdAt: string
  updatedAt: string
}
