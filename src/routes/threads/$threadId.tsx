import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/threads/$threadId')({
  component: ThreadDetailPage,
})

function ThreadDetailPage() {
  const { threadId } = Route.useParams()
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">Thread: {threadId}</h1>
      <p className="text-sm mt-2">Live message stream and evidence timeline surface.</p>
    </main>
  )
}
