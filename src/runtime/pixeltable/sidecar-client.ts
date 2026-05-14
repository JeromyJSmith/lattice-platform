/**
 * sidecar-client.ts
 *
 * Thin Bun/Node-compatible HTTP client for the Python FastAPI sidecar.
 * Speaks over a UNIX domain socket by default (zero network surface area)
 * and falls back to TCP when PIXELTABLE_SERVICE_URL is an http(s):// URL.
 *
 * Auth model:
 *   - UNIX socket: implicit (filesystem ACLs are the boundary).
 *   - TCP:         X-Bridge-Token header from PIXELTABLE_BRIDGE_TOKEN.
 *
 * Idempotency:
 *   - Every POST gets an Idempotency-Key (caller-supplied or sha256 of body).
 *   - Sidecar caches {key -> body_sha256} for 24h, replays return cached body.
 */

import { createHash } from "node:crypto";
import {
  type ClientRequest,
  type RequestOptions as HttpRequestOptions,
  request as httpRequest,
  type IncomingMessage,
} from "node:http";
import { request as httpsRequest } from "node:https";

export interface SidecarClientOptions {
  /** UNIX socket path. Default: /tmp/vwbridge-pxt.sock */
  socketPath?: string;
  /** TCP base URL (http://host:port). Used when set, overrides socketPath. */
  baseUrl?: string;
  /** Bridge token sent as X-Bridge-Token (TCP mode only). */
  token?: string;
  /** Per-request timeout in ms. Default: 30_000. */
  timeoutMs?: number;
}

export interface SidecarResponse<T = unknown> {
  status: number;
  body: T;
  idempotencyKey: string;
}

export interface SingleFileAgentRunRequest {
  job_id: string;
  task: string;
  repo_root?: string;
  output?: string;
  expect_paths?: string[];
  timeout_seconds?: number;
}

export interface HarnessCapabilityRunRequest {
  capability_id: string;
  task?: string;
  repo_root?: string;
  output?: string;
  expect_paths?: string[];
  timeout_seconds?: number;
}

export class SidecarClient {
  readonly mode: "uds" | "tcp";
  readonly socketPath?: string;
  readonly baseUrl?: string;
  readonly token?: string;
  readonly timeoutMs: number;

  constructor(opts: SidecarClientOptions = {}) {
    const env =
      typeof process !== "undefined" ? process.env : ({} as NodeJS.ProcessEnv);
    // Explicit socketPath always wins — don't let PIXELTABLE_SERVICE_URL override a direct UDS request.
    const explicitTcp = opts.socketPath
      ? null
      : (opts.baseUrl ?? env.PIXELTABLE_SERVICE_URL);
    if (explicitTcp && /^https?:\/\//i.test(explicitTcp)) {
      this.mode = "tcp";
      this.baseUrl = explicitTcp.replace(/\/+$/, "");
      this.token = opts.token ?? env.PIXELTABLE_BRIDGE_TOKEN ?? undefined;
    } else {
      this.mode = "uds";
      this.socketPath =
        opts.socketPath ?? env.PIXELTABLE_SOCK ?? "/tmp/vwbridge-pxt.sock";
    }
    this.timeoutMs = opts.timeoutMs ?? 30_000;
  }

  /** Convenience: ingest a list of TS RuntimeEvents via /v1/runtime/events. */
  async ingestRuntimeEvents(
    events: unknown[],
    idempotencyKey?: string,
  ): Promise<SidecarResponse> {
    return this.post("/v1/runtime/events", { events }, idempotencyKey);
  }

  /** Convenience: ingest a Vectorworks sidecar payload. */
  async ingestVectorworksSidecar(
    payload: Record<string, unknown>,
    idempotencyKey?: string,
  ): Promise<SidecarResponse> {
    return this.post("/v1/vw/sidecars", payload, idempotencyKey);
  }

  /** Convenience: record a draw/validate/promote/reject event. */
  async recordPromotion(
    payload: Record<string, unknown>,
    idempotencyKey?: string,
  ): Promise<SidecarResponse> {
    return this.post("/v1/evidence/promotions", payload, idempotencyKey);
  }

  /** Convenience: list registered single-file harness agents. */
  async listSingleFileAgents(): Promise<SidecarResponse> {
    return this.get("/v1/harness/single-file-agents/catalog");
  }

  /** Convenience: run one registered single-file harness agent. */
  async runSingleFileAgent(
    payload: SingleFileAgentRunRequest,
    idempotencyKey?: string,
  ): Promise<SidecarResponse> {
    return this.post(
      "/v1/harness/single-file-agents/runs",
      payload,
      idempotencyKey,
    );
  }

  /** Convenience: run one allowlisted harness capability. */
  async runHarnessCapability(
    payload: HarnessCapabilityRunRequest,
    idempotencyKey?: string,
  ): Promise<SidecarResponse> {
    return this.post("/v1/harness/capabilities/runs", payload, idempotencyKey);
  }

  /** Convenience: fetch the sample Benchy-compatible benchmark report. */
  async getHarnessBenchmarkSampleReport(): Promise<SidecarResponse> {
    return this.get("/v1/harness/benchmarks/sample-report");
  }

  /** Convenience: read all capability registries as a diagnostic matrix. */
  async getCapabilityMatrix(): Promise<SidecarResponse> {
    return this.get("/v1/harness/capabilities/matrix");
  }

  /** Convenience: validate a Benchy-compatible benchmark report. */
  async validateHarnessBenchmarkReport(
    payload: Record<string, unknown>,
    idempotencyKey?: string,
  ): Promise<SidecarResponse> {
    return this.post(
      "/v1/harness/benchmarks/reports/validate",
      payload,
      idempotencyKey,
    );
  }

  /** Convenience: GET /healthz. */
  async healthz(): Promise<SidecarResponse> {
    return this.get("/healthz");
  }

  // -------------------------------------------------------------------------

  async post<T = unknown>(
    path: string,
    body: unknown,
    idempotencyKey?: string,
  ): Promise<SidecarResponse<T>> {
    const json = JSON.stringify(body ?? {});
    const key = idempotencyKey ?? SidecarClient.sha256Hex(json);
    return this._request<T>("POST", path, json, key);
  }

  async get<T = unknown>(path: string): Promise<SidecarResponse<T>> {
    return this._request<T>("GET", path, null, "");
  }

  // -------------------------------------------------------------------------

  private async _request<T>(
    method: string,
    path: string,
    body: string | null,
    idempotencyKey: string,
  ): Promise<SidecarResponse<T>> {
    const headers: Record<string, string> = {
      Accept: "application/json",
    };
    if (body !== null) {
      headers["Content-Type"] = "application/json";
      headers["Content-Length"] = String(Buffer.byteLength(body));
    }
    if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;
    if (this.mode === "tcp" && this.token)
      headers["X-Bridge-Token"] = this.token;

    const reqOptions: HttpRequestOptions = {
      method,
      path,
      headers,
      timeout: this.timeoutMs,
    };
    const buildRequest = (): ClientRequest => {
      if (this.mode === "uds") {
        reqOptions.socketPath = this.socketPath;
        reqOptions.host = "localhost";
        return httpRequest(reqOptions);
      }
      const url = new URL(path, this.baseUrl);
      reqOptions.host = url.hostname;
      reqOptions.port = url.port || (url.protocol === "https:" ? 443 : 80);
      reqOptions.path = url.pathname + url.search;
      return url.protocol === "https:"
        ? httpsRequest(reqOptions)
        : httpRequest(reqOptions);
    };
    const request: ClientRequest = buildRequest();

    return new Promise<SidecarResponse<T>>((resolve, reject) => {
      const chunks: Buffer[] = [];
      request.on("response", (res: IncomingMessage) => {
        res.on("data", (c: Buffer | string) => chunks.push(Buffer.from(c)));
        res.on("end", () => {
          const raw = Buffer.concat(chunks).toString("utf8");
          let parsed: unknown;
          try {
            parsed = raw ? JSON.parse(raw) : null;
          } catch {
            parsed = { error: "non-json-response", raw };
          }
          resolve({
            status: res.statusCode ?? 0,
            body: parsed as T,
            idempotencyKey,
          });
        });
      });
      request.on("timeout", () => {
        request.destroy(
          new Error(
            `sidecar request ${method} ${path} timed out after ${this.timeoutMs}ms`,
          ),
        );
      });
      request.on("error", (err: Error) => reject(err));
      if (body !== null) request.write(body);
      request.end();
    });
  }

  private static sha256Hex(s: string): string {
    return createHash("sha256").update(s).digest("hex");
  }
}

let _sidecarClientSingleton: SidecarClient | null = null;

function getOrCreateSidecarClientSingleton(): SidecarClient {
  if (_sidecarClientSingleton === null) {
    _sidecarClientSingleton = new SidecarClient();
  }
  return _sidecarClientSingleton;
}

export const resolveSidecarClient = (): SidecarClient =>
  getOrCreateSidecarClientSingleton();
