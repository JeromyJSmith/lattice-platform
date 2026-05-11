#!/usr/bin/env bun
/**
 * Capture a PNG of every route in the LATTICE operator console.
 *
 * Usage: bun scripts/screenshot-all-routes.ts
 *
 * Pre-flight:
 *   - Sidecar must respond 200 at http://127.0.0.1:7770/healthz
 *   - Dev server must respond 200 at http://localhost:3000
 *
 * Output: meta/screenshots/<route>.png + a markdown summary path printed at end.
 */
import { chromium, type Page } from 'playwright'
import { mkdir, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const SIDECAR = 'http://127.0.0.1:7770'
const FRONTEND = 'http://localhost:3000'
const OUT_DIR = resolve(import.meta.dir, '..', 'meta', 'screenshots')

type Shot = {
  name: string
  url: string
  description: string
  scrollToBottom?: boolean
  waitMs?: number
}

const SHOTS: Shot[] = [
  { name: 'home',              url: '/',         description: 'Landing page (TanStack Start template, branded as LATTICE)' },
  { name: 'runtime',           url: '/runtime',  description: 'Operator console — runs table + active stream' },
  { name: 'runtime-timeline',  url: '/runtime',  description: 'Operator console scrolled to EventTimeline + AgentUI panel', scrollToBottom: true },
  { name: 'runs',              url: '/runs',     description: 'Runs index (placeholder route)' },
  { name: 'agents',            url: '/agents',   description: 'Agents index (route not yet scaffolded — should 404)' },
  { name: 'threads',           url: '/threads',  description: 'Threads index (placeholder route)' },
  { name: 'evidence',          url: '/evidence', description: 'Evidence ledger (placeholder route)' },
  { name: 'replay',            url: '/replay',   description: 'Run replay (placeholder route)' },
  { name: 'settings',          url: '/settings', description: 'Settings (placeholder route)' },
]

async function preflight(): Promise<void> {
  const probes = [
    { name: 'sidecar /healthz', url: `${SIDECAR}/healthz` },
    { name: 'frontend root',    url: `${FRONTEND}/` },
  ]
  for (const p of probes) {
    const r = await fetch(p.url).catch((e) => ({ ok: false, status: 0, _err: String(e) } as any))
    if (!('ok' in r) || !r.ok) {
      console.error(`✗ preflight failed: ${p.name} @ ${p.url} (status ${('status' in r) ? r.status : '?'})`)
      console.error(`  hint: start the sidecar with 'make sidecar-up-tcp' and the dev server with 'bun run dev'`)
      process.exit(1)
    }
    console.log(`✓ ${p.name}`)
  }
}

async function shot(page: Page, s: Shot): Promise<{ ok: boolean; path: string; status: number }> {
  const url = `${FRONTEND}${s.url}`
  const path = resolve(OUT_DIR, `${s.name}.png`)
  let status = 0
  try {
    // 'networkidle' hangs because the operator console keeps an EventSource
    // open indefinitely. 'domcontentloaded' + a fixed delay below is enough
    // for SSR-prefetched routes to be screenshot-ready.
    const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 })
    status = resp?.status() ?? 0
  } catch (e) {
    console.error(`  navigation error: ${e}`)
  }
  await page.waitForTimeout(s.waitMs ?? 2000)
  if (s.scrollToBottom) {
    await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' as ScrollBehavior }))
    await page.waitForTimeout(800)
  }
  await page.screenshot({ path, fullPage: false })
  console.log(`  ${status === 200 ? '✓' : '⚠'} ${s.name.padEnd(20)} HTTP ${status}  -> ${path}`)
  return { ok: status === 200, path, status }
}

async function main(): Promise<void> {
  await preflight()
  await mkdir(OUT_DIR, { recursive: true })

  const browser = await chromium.launch()
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const page = await ctx.newPage()

  // Best-effort: deal with cookie banners and lazy hydration consistently.
  await page.addInitScript(() => {
    localStorage.setItem('theme', 'dark')
  })

  const results: Array<{ name: string; description: string; ok: boolean; status: number }> = []
  for (const s of SHOTS) {
    const r = await shot(page, s)
    results.push({ name: s.name, description: s.description, ok: r.ok, status: r.status })
  }

  await browser.close()

  // Emit a machine-readable summary so the markdown writer can run after.
  const summary = resolve(OUT_DIR, '_summary.json')
  await writeFile(summary, JSON.stringify({ generatedAt: new Date().toISOString(), shots: SHOTS, results }, null, 2))
  console.log(`\nsummary written to ${summary}`)
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
