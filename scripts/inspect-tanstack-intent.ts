import { spawnSync } from 'node:child_process'

const out = spawnSync('npx', ['@tanstack/intent@latest', 'list'], {
  stdio: 'inherit',
})

process.exit(out.status ?? 1)
