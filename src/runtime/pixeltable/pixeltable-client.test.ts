import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("pixeltable-client browser safety", () => {
  it("does not import sidecar-client (Node-only transport)", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/runtime/pixeltable/pixeltable-client.ts"),
      "utf8",
    );
    expect(source).not.toContain("sidecar-client");
  });
});
