import type { AgentId } from '../protocol/agent-event'

export function chooseAgent(message: string): AgentId {
  const lower = message.toLowerCase()
  if (lower.includes('provider') || lower.includes('model')) return 'openrouter'
  if (lower.includes('script') || lower.includes('cli')) return 'claude-code'
  if (lower.includes('pipeline') || lower.includes('batch')) return 'pi'
  return 'hermes'
}
