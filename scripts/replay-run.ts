import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const runDir = process.argv[2]
if (!runDir) {
  console.error('Usage: bun run scripts/replay-run.ts <run-dir>')
  process.exit(1)
}

const eventsPath = resolve(runDir, 'events.jsonl')
const lines = readFileSync(eventsPath, 'utf8').trim().split('\n')

for (const line of lines) {
  const event = JSON.parse(line)
  console.log(`${event.createdAt} ${event.type}`)
}
