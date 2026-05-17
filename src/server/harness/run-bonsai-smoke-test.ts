import { createServerFn } from "@tanstack/react-start";
import { resolveSidecarClient } from "#/runtime/pixeltable/sidecar-client";

type BonsaiSmokeResult = {
  ok: boolean;
  model: string;
  expected: string;
  latency_ms: number;
  returncode: number;
  stdout: string;
  stderr: string;
  verification: {
    status: "passed" | "failed";
    message: string;
  };
  command: string;
};

export const runBonsaiSmokeTest = createServerFn({ method: "POST" }).handler(
  async () => {
    const response = await resolveSidecarClient().runHarnessModelSmokeTest({
      model: "prism-ml/Ternary-Bonsai-4B-mlx-2bit",
      timeout_seconds: 90,
    });
    if (response.status < 200 || response.status >= 300) {
      throw new Error(
        `sidecar /v1/harness/models/smoke ${response.status}: ${JSON.stringify(response.body)}`,
      );
    }
    return response.body as BonsaiSmokeResult;
  },
);
