import { describe, expect, it } from "vitest";

import { buildBenchmarkReport } from "./run-codebase-context-proof";

describe("buildBenchmarkReport", () => {
  it("does not mark review-only verification as live verified", () => {
    const report = buildBenchmarkReport(
      {
        ok: true,
        latency_ms: 123,
        artifact: "meta/harness/docs/sessions/test-proof.json",
        verification: {
          status: "review_required",
          message: "Human review required.",
          returncode: 0,
        },
      },
      "codebase-context-ripgrep",
      "meta/harness/docs/sessions/test-proof.json",
    );

    expect(report.provenance.trust).toBe("uploaded_unverified");
    expect(report.verification.status).toBe("unverified");
    expect(report.verification.message).toContain("review-only");
    expect(report.models[0]?.results[0]?.score).toBeNull();
  });

  it("marks explicit passed verification as live verified", () => {
    const report = buildBenchmarkReport(
      {
        ok: true,
        latency_ms: 123,
        artifact: "meta/harness/docs/sessions/test-proof.json",
        verification: {
          status: "passed",
          message: "Verifier returned zero.",
          returncode: 0,
        },
      },
      "codebase-context-ripgrep",
      "meta/harness/docs/sessions/test-proof.json",
    );

    expect(report.provenance.trust).toBe("live_verified");
    expect(report.verification.status).toBe("passed");
    expect(report.models[0]?.results[1]?.score).toBeNull();
  });

  it("downgrades passed verification when the proof artifact path mismatches", () => {
    const report = buildBenchmarkReport(
      {
        ok: true,
        latency_ms: 123,
        artifact: "meta/harness/docs/sessions/other-proof.json",
        verification: {
          status: "passed",
          message: "Verifier returned zero.",
          returncode: 0,
        },
      },
      "codebase-context-ripgrep",
      "meta/harness/docs/sessions/test-proof.json",
    );

    expect(report.provenance.trust).toBe("uploaded_unverified");
    expect(report.verification.status).toBe("unverified");
    expect(report.verification.message).toContain("artifact path");
  });

  it("downgrades passed verification when the verifier returncode is missing", () => {
    const report = buildBenchmarkReport(
      {
        ok: true,
        latency_ms: 123,
        artifact: "meta/harness/docs/sessions/test-proof.json",
        verification: {
          status: "passed",
          message: "Verifier returned zero.",
        },
      },
      "codebase-context-ripgrep",
      "meta/harness/docs/sessions/test-proof.json",
    );

    expect(report.provenance.trust).toBe("uploaded_unverified");
    expect(report.verification.status).toBe("unverified");
  });
});
