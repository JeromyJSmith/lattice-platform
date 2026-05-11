import { chooseAgent } from './routing-policy'

export function routeTaskToAgent(input: { message: string }) {
  const agent = chooseAgent(input.message)
  return {
    agent,
    reason: `routed by policy for message "${input.message.slice(0, 64)}"`,
  }
}
