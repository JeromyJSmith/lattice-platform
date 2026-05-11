import { existsSync } from 'node:fs'

const requiredPaths = [
  'meta/config.yaml',
  'runtime-runs',
  'pixeltable/ingestion-contract.yaml',
  'src/runtime/protocol/agent-event.ts',
  'src/routes/runtime.tsx',
  'src/routes/runs/index.tsx',
  'src/routes/evidence/index.tsx',
  'src/routes/settings/providers.tsx',
]

const missing = requiredPaths.filter((path) => !existsSync(path))

if (missing.length > 0) {
  console.error('Missing required runtime artifacts:')
  for (const path of missing) console.error(`- ${path}`)
  process.exit(1)
}

console.log('Runtime verification passed.')
