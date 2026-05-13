import { createServerFn } from "@tanstack/react-start";
import { resolveSidecarClient } from "#/runtime/pixeltable/sidecar-client";

type SidecarRunBody = {
  ok?: boolean;
  capability_id?: string;
  job_id?: string;
  latency_ms?: number;
  artifact?: string;
  stdout?: string;
  stderr?: string;
  verification?: {
    status?: string;
    message?: string;
    returncode?: number;
    stdout?: string;
    stderr?: string;
  };
};

type BenchmarkReport = {
  benchmark_name: string;
  purpose: string;
  base_prompt: string;
  prompt_iterations: Array<Record<string, unknown>>;
  models: Array<{
    model: string;
    provider: string;
    results: Array<{
      prompt: string;
      success: boolean;
      latency_ms: number;
      cost_usd: number;
      score: number;
      output?: string;
      failure_mode?: string | null;
    }>;
  }>;
};

const GOLDEN_PATH_TASK =
  "Identify files relevant to adding or changing a FastAPI sidecar route for single-file harness agents and benchmark reports.";

const RUNNABLE_CAPABILITY_IDS = new Set([
  "codebase-context-ripgrep",
  "python-docstring-rule",
]);

function timestampSlug(): string {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function taskLabel(capabilityId: string): string {
  if (capabilityId === "python-docstring-rule") {
    return "Run the Python docstring rule verifier against changed and new Python files.";
  }
  return GOLDEN_PATH_TASK;
}

function modelLabel(capabilityId: string): string {
  if (capabilityId === "python-docstring-rule") {
    return "deterministic-python-docstring-check";
  }
  return "deterministic-keyword-ripgrep";
}

function buildBenchmarkReport(
  body: SidecarRunBody,
  capabilityId: string,
): BenchmarkReport {
  const success = body.ok === true;
  const verifierPassed =
    body.verification?.status === "passed" ||
    body.verification?.returncode === 0;
  return {
    benchmark_name: `${capabilityId} live browser run`,
    purpose:
      "Run a registered harness capability through TanStack, FastAPI, and an allowlisted verifier while the operator watches the console.",
    base_prompt: taskLabel(capabilityId),
    prompt_iterations: [
      {
        capability: capabilityId,
        expected: "sidecar execution succeeds and verifier returns zero",
      },
    ],
    models: [
      {
        model: modelLabel(capabilityId),
        provider: "tanstack-server-fn-fastapi-uv",
        results: [
          {
            prompt: "FastAPI sidecar registered job run",
            success,
            latency_ms: body.latency_ms ?? 0,
            cost_usd: 0,
            score: success ? 1 : 0,
            output: body.artifact,
            failure_mode: success ? null : body.stderr || "sidecar run failed",
          },
          {
            prompt: "Verifier returned zero",
            success: verifierPassed,
            latency_ms: 0,
            cost_usd: 0,
            score: verifierPassed ? 1 : 0,
            output: body.verification?.stdout,
            failure_mode: verifierPassed
              ? null
              : body.verification?.stderr || "verifier failed",
          },
        ],
      },
    ],
  };
}

export const runCodebaseContextProof = createServerFn({
  method: "POST",
}).handler(async () => {
  return runCapabilityById("codebase-context-ripgrep");
});

export const runCapabilityProof = createServerFn({
  method: "POST",
})
  .inputValidator((data: { capabilityId: string }) => data)
  .handler(async ({ data }) => {
    return runCapabilityById(data.capabilityId);
  });

async function runCapabilityById(capabilityId: string) {
  if (!RUNNABLE_CAPABILITY_IDS.has(capabilityId)) {
    throw new Error(`No runnable proof is registered for ${capabilityId}.`);
  }

  const client = resolveSidecarClient();
  const output = `meta/harness/docs/sessions/${timestampSlug()}-${capabilityId}-browser-run.json`;
  const response = await client.runHarnessCapability({
    capability_id: capabilityId,
    repo_root: ".",
    output,
    timeout_seconds: 60,
  });

  if (response.status < 200 || response.status >= 300) {
    throw new Error(
      `sidecar /v1/harness/capabilities/runs ${response.status}: ${JSON.stringify(response.body)}`,
    );
  }

  const body = response.body as SidecarRunBody;
  return {
    ok: body.ok === true,
    capability_id: body.capability_id ?? capabilityId,
    artifact: body.artifact ?? output,
    stdout: body.stdout ?? "",
    stderr: body.stderr ?? "",
    verification: body.verification ?? {},
    report: buildBenchmarkReport(body, capabilityId),
  };
}
