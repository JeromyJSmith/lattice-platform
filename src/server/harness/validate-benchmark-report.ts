import { createServerFn } from "@tanstack/react-start";
import { resolveSidecarClient } from "#/runtime/pixeltable/sidecar-client";

type BenchmarkReport = {
  benchmark_name: string;
  purpose?: string;
  base_prompt?: string;
  prompt_iterations?: Array<Record<string, string>>;
  provenance: {
    source: "sample" | "uploaded" | "sidecar_live_run" | "sidecar_import";
    trust:
      | "synthetic"
      | "uploaded_unverified"
      | "live_verified"
      | "live_failed";
    label: string;
    artifact?: string;
    verified_at?: string;
  };
  verification: {
    status: "unverified" | "passed" | "failed";
    message: string;
  };
  models: Array<{
    model: string;
    provider?: string;
    results: Array<{
      prompt: string;
      success: boolean;
      latency_ms: number;
      cost_usd?: number;
      score?: number;
      output?: string;
      failure_mode?: string | null;
    }>;
  }>;
};

type BenchmarkValidationResult = {
  ok: boolean;
  benchmark_name: string;
  model_count: number;
  run_count: number;
  report: BenchmarkReport;
  provenance: BenchmarkReport["provenance"];
  verification: BenchmarkReport["verification"];
};

export const validateBenchmarkReport = createServerFn({
  method: "POST",
})
  .inputValidator((data: { report: BenchmarkReport }) => data)
  .handler(async ({ data }) => {
    const client = resolveSidecarClient();
    const response = await client.validateHarnessBenchmarkReport({
      report: data.report,
    });

    if (response.status < 200 || response.status >= 300) {
      throw new Error(
        `sidecar /v1/harness/benchmarks/reports/validate ${response.status}: ${JSON.stringify(response.body)}`,
      );
    }

    return response.body as BenchmarkValidationResult;
  });
