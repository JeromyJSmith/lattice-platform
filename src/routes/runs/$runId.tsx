import { createFileRoute, Link } from '@tanstack/react-router'

export const Route = createFileRoute('/runs/$runId')({
  component: RunDetailPage,
})

function RunDetailPage() {
  const { runId } = Route.useParams()
  return (
    <main className="page-wrap px-4 pb-8 pt-14 space-y-2">
      <h1 className="text-2xl font-bold">Run: {runId}</h1>
      <p className="text-sm">Single-run details and event evidence manifest.</p>
      <Link to="/replay/$runId" params={{ runId }} className="underline">
        Open replay timeline
      </Link>
    </main>
  )
}
