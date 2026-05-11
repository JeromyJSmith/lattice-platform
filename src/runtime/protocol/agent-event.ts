export type AgentId =
  | 'claude-code'
  | 'pi'
  | 'hermes'
  | 'openrouter'
  | 'router'
  | 'user'

export type RuntimeEvent =
  | {
      type: 'thread.created'
      eventId: string
      threadId: string
      createdAt: string
    }
  | {
      type: 'message.created'
      eventId: string
      threadId: string
      messageId: string
      sourceAgent: AgentId
      targetAgent: AgentId
      content: string
      createdAt: string
    }
  | {
      type: 'run.started'
      eventId: string
      threadId: string
      runId: string
      agentId: AgentId
      createdAt: string
    }
  | {
      type: 'stream.delta'
      eventId: string
      threadId: string
      runId: string
      seq: number
      text: string
      createdAt: string
    }
  | {
      type: 'tool.started' | 'tool.completed'
      eventId: string
      threadId: string
      runId: string
      toolName: string
      payload?: unknown
      createdAt: string
    }
  | {
      type: 'artifact.created'
      eventId: string
      threadId: string
      runId: string
      path: string
      sha256: string
      mimeType?: string
      createdAt: string
    }
  | {
      type: 'run.completed'
      eventId: string
      threadId: string
      runId: string
      outcomeId: string
      createdAt: string
    }
  | {
      type: 'run.failed'
      eventId: string
      threadId: string
      runId: string
      error: string
      createdAt: string
    }
