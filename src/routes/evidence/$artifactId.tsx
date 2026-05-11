import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/evidence/$artifactId')({
  component: ArtifactDetailPage,
})

function ArtifactDetailPage() {
  const { artifactId } = Route.useParams()
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">Artifact: {artifactId}</h1>
      <p className="text-sm mt-2">Artifact metadata, checksums, and source run link.</p>
    </main>
  )
}
