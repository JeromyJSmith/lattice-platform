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

type CapabilityProofResult = {
  ok: boolean;
  sidecar_ok: boolean;
  capability_id: string;
  artifact: string;
  stdout: string;
  stderr: string;
  verification: NonNullable<SidecarRunBody["verification"]>;
  report: BenchmarkReport;
};

type BenchmarkReport = {
  benchmark_name: string;
  purpose: string;
  base_prompt: string;
  prompt_iterations: Array<Record<string, string>>;
  provenance: {
    source:
      | "sample"
      | "uploaded"
      | "sidecar_live_run"
      | "sidecar_import";
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
    provider: string;
    results: Array<{
      prompt: string;
      success: boolean;
      latency_ms: number;
      cost_usd: number;
      score: number | null;
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

export function buildBenchmarkReport(
  body: SidecarRunBody,
  capabilityId: string,
  expectedArtifact?: string,
): BenchmarkReport {
  const success = body.ok === true;
  const returnedCapabilityId =
    typeof body.capability_id === "string" && body.capability_id.length > 0
      ? body.capability_id
      : undefined;
  const artifact =
    typeof body.artifact === "string" && body.artifact.length > 0
      ? body.artifact
      : undefined;
  const verificationStatus = body.verification?.status;
  const verifierReturnedZero = body.verification?.returncode === 0;
  const capabilityMatchesRequested = returnedCapabilityId === capabilityId;
  const artifactMatchesRequested =
    typeof expectedArtifact !== "string" || artifact === expectedArtifact;
  const verifierPassed =
    verificationStatus === "passed" &&
    verifierReturnedZero &&
    capabilityMatchesRequested &&
    typeof artifact === "string" &&
    artifactMatchesRequested;
  const verifierReviewOnly =
    verificationStatus === "review_required" ||
    verificationStatus === "unverified" ||
    (verificationStatus === "passed" && !verifierPassed);
  const capabilityIdentityGap =
    verificationStatus === "passed" && !capabilityMatchesRequested;
  const artifactIdentityGap =
    verificationStatus === "passed" && !artifactMatchesRequested;
  const trust =
    success && verifierPassed
      ? "live_verified"
      : verifierReviewOnly
        ? "uploaded_unverified"
        : "live_failed";
  const reportVerificationStatus =
    success && verifierPassed
      ? "passed"
      : verifierReviewOnly
        ? "unverified"
        : "failed";
  return {
    benchmark_name: `${capabilityId} live browser run`,
    purpose:
      "Run a registered harness capability through TanStack, FastAPI, and an allowlisted verifier while the operator watches the console.",
    base_prompt: taskLabel(capabilityId),
    prompt_iterations: [
      {
        capability: capabilityId,
        expected:
          "sidecar execution succeeds, verifier returns zero, and both the returned capability id and proof artifact match the requested browser run",
      },
    ],
    provenance: {
      source: "sidecar_live_run",
      trust,
      label:
        trust === "live_verified"
          ? "Live verified sidecar proof"
          : trust === "uploaded_unverified"
            ? "Live sidecar run requires review"
            : "Live failed sidecar proof",
      artifact,
      verified_at: new Date().toISOString(),
    },
    verification: {
      status: reportVerificationStatus,
      message:
        success && verifierPassed
          ? "Sidecar execution and verifier both passed."
          : capabilityIdentityGap && artifactIdentityGap
            ? "Sidecar execution completed, but both the returned capability id and proof artifact path did not match the requested browser run."
          : capabilityIdentityGap
            ? "Sidecar execution completed, but the returned capability id did not match the requested capability."
          : artifactIdentityGap
            ? "Sidecar execution completed, but the proof artifact path did not match the requested browser run output."
          : verifierReviewOnly
            ? "Sidecar execution completed, but verification is review-only or unverified."
          : "Sidecar execution or verifier failed.",
    },
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
            score: null,
            output: artifact,
            failure_mode: success ? null : body.stderr || "sidecar run failed",
          },
          {
            prompt: "Verifier returned zero",
            success: verifierPassed,
            latency_ms: 0,
            cost_usd: 0,
            score: null,
            output: body.verification?.stdout,
            failure_mode: verifierPassed
              ? null
              : capabilityIdentityGap
                ? "returned capability id mismatched requested capability"
                : artifactIdentityGap
                  ? "proof artifact path mismatched requested browser run output"
                  : body.verification?.stderr || "verifier failed",
          },
        ],
      },
    ],
  };
}

export function buildCapabilityProofResult(
  body: SidecarRunBody,
  capabilityId: string,
  expectedArtifact?: string,
): CapabilityProofResult {
  const report = buildBenchmarkReport(body, capabilityId, expectedArtifact);
  return {
    ok: report.verification.status === "passed",
    sidecar_ok: body.ok === true,
    capability_id: body.capability_id ?? capabilityId,
    artifact: body.artifact ?? expectedArtifact ?? "",
    stdout: body.stdout ?? "",
    stderr: body.stderr ?? "",
    verification: body.verification ?? {},
    report,
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
  return buildCapabilityProofResult(body, capabilityId, output);
}
