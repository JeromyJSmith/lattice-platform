import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/settings/auth')({
  component: AuthSettingsPage,
})

function AuthSettingsPage() {
  return (
    <main className="page-wrap px-4 pb-8 pt-14">
      <h1 className="text-2xl font-bold">Auth Settings</h1>
      <p className="text-sm mt-2">
        Better Auth is installed and reserved as operator-mode boundary.
      </p>
    </main>
  )
}
