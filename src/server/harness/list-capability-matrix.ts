import { createServerFn } from "@tanstack/react-start";
import { resolveSidecarClient } from "#/runtime/pixeltable/sidecar-client";

export type CapabilityStatus = {
  label: string;
  color: "green" | "amber" | "red";
  missing_wires: string[];
  missing_proof: string[];
  proof_verification?: {
    statuses: Array<{ path: string; status: string }>;
    passed: string[];
    review_required: string[];
    failed: string[];
    unreadable: string[];
  };
  troubleshooting: string;
};

export type CapabilityRunAction = {
  kind: string;
  job_id: string;
  label: string;
};

export type CapabilityRow = {
  id: string;
  name?: string;
  surface?: string;
  state?: string;
  description?: string;
  wired_at: string[];
  invoked_by: string[];
  serves: string[];
  proof_evidence: string[];
  run_action?: CapabilityRunAction | null;
  status: CapabilityStatus;
};

export type CapabilityRegistry = {
  tool: string;
  tool_version?: string;
  canonical_docs?: string;
  source_mirror?: string;
  registry_path: string;
  capabilities: CapabilityRow[];
};

export type CapabilityMatrixPayload = {
  ok: boolean;
  summary: {
    green: number;
    amber: number;
    red: number;
    total: number;
  };
  registries: CapabilityRegistry[];
};

export const listCapabilityMatrix = createServerFn({ method: "GET" }).handler(
  async () => {
    const response = await resolveSidecarClient().getCapabilityMatrix();
    if (response.status < 200 || response.status >= 300) {
      throw new Error(
        `sidecar /v1/harness/capabilities/matrix ${response.status}: ${JSON.stringify(response.body)}`,
      );
    }
    return response.body as CapabilityMatrixPayload;
  },
);
