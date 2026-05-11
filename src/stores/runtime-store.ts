import { Store } from '@tanstack/store'

export interface RuntimeStoreState {
  activeRunId: string | null
  activeThreadId: string | null
  selectedAgent: 'claude-code' | 'pi' | 'hermes' | 'openrouter'
}

export const runtimeStore = new Store<RuntimeStoreState>({
  activeRunId: null,
  activeThreadId: null,
  selectedAgent: 'claude-code',
})
