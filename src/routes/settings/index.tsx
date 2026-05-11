import { createFileRoute, Link } from '@tanstack/react-router'

export const Route = createFileRoute('/settings/')({
  component: SettingsIndexPage,
})

function SettingsIndexPage() {
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold mb-3">Settings</h1>
      <ul className="list-disc pl-6 space-y-1">
        <li><Link to="/settings/providers">Providers</Link></li>
        <li><Link to="/settings/auth">Auth</Link></li>
        <li><Link to="/settings/pixeltable">Pixeltable</Link></li>
        <li><Link to="/settings/db">TanStack DB</Link></li>
        <li><Link to="/settings/intent">Intent</Link></li>
      </ul>
    </main>
  )
}
