import { createFileRoute } from '@tanstack/react-router'
import { getRuntimeCollections } from '#/db/runtime-collections'

export const Route = createFileRoute('/settings/db')({
  component: DbSettingsPage,
})

function DbSettingsPage() {
  const collections = getRuntimeCollections()
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">TanStack DB Status</h1>
      <p className="text-sm mt-2">
        Local collection size: {collections.runCollection.state.length}
      </p>
    </main>
  )
}
