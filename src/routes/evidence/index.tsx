import { createFileRoute, Link } from '@tanstack/react-router'
import { ArtifactsTable } from '#/tables/artifacts-table'

export const Route = createFileRoute('/evidence/')({
  component: EvidencePage,
})

function EvidencePage() {
  const artifacts = [{ id: 'artifact-placeholder' }]
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold mb-3">Evidence</h1>
      <ArtifactsTable artifacts={artifacts} />
      <p className="mt-4 text-sm">
        <Link to="/evidence/$artifactId" params={{ artifactId: 'artifact-placeholder' }} className="underline">
          View artifact detail
        </Link>
      </p>
    </main>
  )
}
