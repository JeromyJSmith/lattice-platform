import { createServerFn } from "@tanstack/react-start";
import { resolveSidecarClient } from "#/runtime/pixeltable/sidecar-client";

export type BenchResult = {
  prompt: string;
  success: boolean;
  latency_ms: number;
  cost_usd?: number;
  score?: number;
  output?: string;
};

export type ModelReport = {
  model: string;
  provider?: string;
  results: BenchResult[];
};

export type BenchmarkReport = {
  benchmark_name: string;
  purpose: string;
  base_prompt?: string;
  prompt_iterations?: unknown[];
  models: ModelReport[];
};

export type BenchmarkReportRecord = {
  artifact: string;
  updated_at: string;
  report: BenchmarkReport;
};

type SidecarBenchmarkReportsResponse = {
  ok: boolean;
  reports: BenchmarkReportRecord[];
};

export const listBenchmarkReports = createServerFn({ method: "GET" }).handler(
  async () => {
    const response = await resolveSidecarClient().listHarnessBenchmarkReports(20);
    if (response.status < 200 || response.status >= 300) {
      throw new Error(
        `sidecar /v1/harness/benchmarks/reports ${response.status}: ${JSON.stringify(response.body)}`,
      );
    }
    return response.body as SidecarBenchmarkReportsResponse;
  },
);
