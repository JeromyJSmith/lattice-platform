import { describe, expect, it } from 'vitest'

import { SidecarClient } from './sidecar-client'

describe('SidecarClient', () => {
  it('defaults to UDS mode with /tmp/vwbridge-pxt.sock', () => {
    const prevUrl = process.env.PIXELTABLE_SERVICE_URL
    const prevSock = process.env.PIXELTABLE_SOCK
    delete process.env.PIXELTABLE_SERVICE_URL
    delete process.env.PIXELTABLE_SOCK
    try {
      const c = new SidecarClient()
      expect(c.mode).toBe('uds')
      expect(c.socketPath).toBe('/tmp/vwbridge-pxt.sock')
    } finally {
      if (prevUrl) process.env.PIXELTABLE_SERVICE_URL = prevUrl
      if (prevSock) process.env.PIXELTABLE_SOCK = prevSock
    }
  })

  it('switches to TCP mode when PIXELTABLE_SERVICE_URL is set', () => {
    const c = new SidecarClient({ baseUrl: 'http://127.0.0.1:8123' })
    expect(c.mode).toBe('tcp')
    expect(c.baseUrl).toBe('http://127.0.0.1:8123')
  })

  it('respects explicit socketPath option', () => {
    const c = new SidecarClient({ socketPath: '/var/run/custom.sock' })
    expect(c.mode).toBe('uds')
    expect(c.socketPath).toBe('/var/run/custom.sock')
  })

  it('passes token in TCP mode', () => {
    const c = new SidecarClient({
      baseUrl: 'http://127.0.0.1:8123',
      token: 'unit-test-token',
    })
    expect(c.mode).toBe('tcp')
    expect(c.token).toBe('unit-test-token')
  })

  it('uses default 30s timeout', () => {
    const c = new SidecarClient()
    expect(c.timeoutMs).toBe(30_000)
  })

  it('honours custom timeout override', () => {
    const c = new SidecarClient({ timeoutMs: 1234 })
    expect(c.timeoutMs).toBe(1234)
  })
})
