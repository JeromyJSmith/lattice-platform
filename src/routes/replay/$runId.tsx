import { createFileRoute } from '@tanstack/react-router'
import { EventTimeline } from '#/virtual/event-timeline'

export const Route = createFileRoute('/replay/$runId')({
  component: ReplayPage,
})

function ReplayPage() {
  const { runId } = Route.useParams()
  return (
    <main className="page-wrap px-4 pb-8 pt-14 space-y-3">
      <h1 className="text-2xl font-bold">Replay: {runId}</h1>
      <EventTimeline
        items={[
          'thread.created',
          'message.created',
          'run.started',
          'stream.delta',
          'run.completed',
        ]}
      />
    </main>
  )
}
