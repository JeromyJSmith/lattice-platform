import { describe, expect, it } from "vitest";

import { SidecarClient } from "./sidecar-client";

describe("SidecarClient", () => {
  it("defaults to UDS mode with /tmp/vwbridge-pxt.sock", () => {
    const prevUrl = process.env.PIXELTABLE_SERVICE_URL;
    const prevSock = process.env.PIXELTABLE_SOCK;
    delete process.env.PIXELTABLE_SERVICE_URL;
    delete process.env.PIXELTABLE_SOCK;
    try {
      const c = new SidecarClient();
      expect(c.mode).toBe("uds");
      expect(c.socketPath).toBe("/tmp/vwbridge-pxt.sock");
    } finally {
      if (prevUrl) process.env.PIXELTABLE_SERVICE_URL = prevUrl;
      if (prevSock) process.env.PIXELTABLE_SOCK = prevSock;
    }
  });

  it("switches to TCP mode when PIXELTABLE_SERVICE_URL is set", () => {
    const c = new SidecarClient({ baseUrl: "http://127.0.0.1:8123" });
    expect(c.mode).toBe("tcp");
    expect(c.baseUrl).toBe("http://127.0.0.1:8123");
  });

  it("respects explicit socketPath option", () => {
    const prevUrl = process.env.PIXELTABLE_SERVICE_URL;
    delete process.env.PIXELTABLE_SERVICE_URL;
    try {
      const c = new SidecarClient({ socketPath: "/var/run/custom.sock" });
      expect(c.mode).toBe("uds");
      expect(c.socketPath).toBe("/var/run/custom.sock");
    } finally {
      if (prevUrl) process.env.PIXELTABLE_SERVICE_URL = prevUrl;
    }
  });

  it("passes token in TCP mode", () => {
    const c = new SidecarClient({
      baseUrl: "http://127.0.0.1:8123",
      token: "unit-test-token",
    });
    expect(c.mode).toBe("tcp");
    expect(c.token).toBe("unit-test-token");
  });

  it("uses default 30s timeout", () => {
    const prevUrl = process.env.PIXELTABLE_SERVICE_URL;
    delete process.env.PIXELTABLE_SERVICE_URL;
    try {
      const c = new SidecarClient();
      expect(c.timeoutMs).toBe(30_000);
    } finally {
      if (prevUrl) process.env.PIXELTABLE_SERVICE_URL = prevUrl;
    }
  });

  it("honours custom timeout override", () => {
    const c = new SidecarClient({ timeoutMs: 1234 });
    expect(c.timeoutMs).toBe(1234);
  });

  it("exposes harness endpoint convenience methods", async () => {
    const c = new SidecarClient();
    const calls: Array<{ method: string; path: string; body?: unknown }> = [];
    c.get = async (path) => {
      calls.push({ method: "GET", path });
      return { status: 200, body: {}, idempotencyKey: "" };
    };
    c.post = async (path, body) => {
      calls.push({ method: "POST", path, body });
      return { status: 200, body: {}, idempotencyKey: "test" };
    };

    await c.listSingleFileAgents();
    await c.runSingleFileAgent({
      job_id: "codebase-context-ripgrep",
      task: "task",
    });
    await c.runHarnessCapability({
      capability_id: "codebase-context-ripgrep",
    });
    await c.getCapabilityMatrix();
    await c.getHarnessBenchmarkSampleReport();
    await c.validateHarnessBenchmarkReport({
      report: { benchmark_name: "x", models: [] },
    });

    expect(calls.map((call) => `${call.method} ${call.path}`)).toEqual([
      "GET /v1/harness/single-file-agents/catalog",
      "POST /v1/harness/single-file-agents/runs",
      "POST /v1/harness/capabilities/runs",
      "GET /v1/harness/capabilities/matrix",
      "GET /v1/harness/benchmarks/sample-report",
      "POST /v1/harness/benchmarks/reports/validate",
    ]);
  });
});
