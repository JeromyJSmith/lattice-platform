import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/agents/$agentId')({
  component: AgentDetailPage,
})

function AgentDetailPage() {
  const { agentId } = Route.useParams()
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">Agent: {agentId}</h1>
      <p className="text-sm mt-2">Runtime adapter health and routing status view.</p>
    </main>
  )
}
