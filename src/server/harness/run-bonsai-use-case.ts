import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { createServerFn } from "@tanstack/react-start";
import { resolveSidecarClient } from "#/runtime/pixeltable/sidecar-client";

const execFileAsync = promisify(execFile);

const BONSAI_4B_MODEL = "prism-ml/Ternary-Bonsai-4B-mlx-2bit";

export type BonsaiUseCaseScenario = {
  id: string;
  label: string;
  description: string;
  region: string;
  top: number;
  quantity: number;
  quantityUnit: string;
};

export const bonsaiUseCaseScenarios: BonsaiUseCaseScenario[] = [
  {
    id: "juniper-creeping-thyme",
    label: "Juniper Ave: Creeping thyme planting estimate",
    description: "creeping dwarf creeping thyme plants groundcover",
    region: "US",
    top: 5,
    quantity: 1200,
    quantityUnit: "m2",
  },
  {
    id: "juniper-concrete-slab",
    label: "Juniper Ave: Reinforced slab estimate",
    description: "reinforced concrete slab on grade with vapor barrier",
    region: "US",
    top: 3,
    quantity: 1200,
    quantityUnit: "m2",
  },
  {
    id: "juniper-drainage",
    label: "Juniper Ave: Perforated drainage estimate",
    description: "perforated drainage pipe installation site edge",
    region: "US",
    top: 3,
    quantity: 250,
    quantityUnit: "m",
  },
];

type CostSearchRow = {
  item_id: string;
  name: string;
  unit: string;
  unit_cost: number;
  unit_currency: string;
  unit_cost_region: string;
  score: number;
};

type CostSearchResponse = {
  ok: boolean;
  description: string;
  region: string;
  top: number;
  rows: CostSearchRow[];
};

type BonsaiUseCaseResult = {
  ok: boolean;
  scenario: BonsaiUseCaseScenario;
  verification: {
    status: "passed" | "failed";
    message: string;
  };
  confidence: {
    topScore: number;
    signal: "high" | "medium" | "low";
  };
  estimate: {
    quantity: number;
    quantityUnit: string;
    candidateItem: string;
    candidateUnit: string;
    unitCost: number;
    currency: string;
    totalCost: number;
    unitMatch: boolean;
  } | null;
  rows: CostSearchRow[];
  note: string;
  model: string;
  command: string;
  rawOutput: string;
};

const MIN_RELIABLE_SCORE = 0.55;

function classifyConfidence(topScore: number): "high" | "medium" | "low" {
  if (topScore >= 0.55) return "high";
  if (topScore >= 0.25) return "medium";
  return "low";
}

function cleanModelOutput(stdout: string): string {
  const trimmed = stdout.trim();
  if (!trimmed) return trimmed;
  return trimmed
    .split("\n")
    .filter((line) => !line.startsWith("Prompt: ") && !line.startsWith("Generation: ") && !line.startsWith("Peak memory: "))
    .join("\n")
    .trim();
}

export const runBonsaiUseCase = createServerFn({ method: "POST" })
  .inputValidator((data: { scenarioId: string }) => data)
  .handler(async ({ data }): Promise<BonsaiUseCaseResult> => {
    const scenario = bonsaiUseCaseScenarios.find((candidate) => candidate.id === data.scenarioId);
    if (!scenario) {
      throw new Error(`Unknown scenario: ${data.scenarioId}`);
    }

    const sidecar = resolveSidecarClient();
    const costResponse = await sidecar.runErpCostSearch({
      description: scenario.description,
      region: scenario.region,
      top: scenario.top,
    });
    if (costResponse.status < 200 || costResponse.status >= 300) {
      throw new Error(
        `sidecar /v1/erp/cost-search ${costResponse.status}: ${JSON.stringify(costResponse.body)}`,
      );
    }
    const payload = costResponse.body as CostSearchResponse;
    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    const best = rows[0] ?? null;
    const topScore = best?.score ?? 0;
    const confidence = {
      topScore,
      signal: classifyConfidence(topScore),
    };
    const unitMatches = best?.unit === scenario.quantityUnit;
    const hasReliableMatch = best !== null && topScore >= MIN_RELIABLE_SCORE && unitMatches;

    const estimate =
      !hasReliableMatch || best === null
        ? null
        : {
            quantity: scenario.quantity,
            quantityUnit: scenario.quantityUnit,
            candidateItem: best.name,
            candidateUnit: best.unit,
            unitCost: best.unit_cost,
            currency: best.unit_currency,
            totalCost: Number((scenario.quantity * best.unit_cost).toFixed(2)),
            unitMatch: best.unit === scenario.quantityUnit,
          };

    if (!hasReliableMatch) {
      const failureMessage =
        best === null
          ? `No CWICR rows returned for scenario ${scenario.label}.`
          : `Top candidate "${best.name}" scored ${topScore.toFixed(3)} with unit ${best.unit}; threshold is ${MIN_RELIABLE_SCORE.toFixed(2)} and expected unit is ${scenario.quantityUnit}.`;
      const note = [
        `- No reliable CWICR match for ${scenario.label}.`,
        `- Estimate suppressed. Do not use this run for BOQ or operator proof.`,
        best === null
          ? "- Retrieval returned zero rows."
          : `- Top candidate was "${best.name}" (${best.unit_cost} ${best.unit_currency}/${best.unit}) with score ${topScore.toFixed(3)}.`,
        `- Next step: refine the query or map this scenario to a validated plant-cost taxonomy before asking Bonsai for a decision note.`,
      ].join("\n");
      return {
        ok: false,
        scenario,
        verification: {
          status: "failed",
          message: failureMessage,
        },
        confidence,
        estimate: null,
        rows,
        note,
        model: BONSAI_4B_MODEL,
        command: "suppressed: no Bonsai invocation because retrieval confidence was below threshold",
        rawOutput: "",
      };
    }

    const prompt = [
      "You are producing an operator note for VW_iTwin_Bridge Juniper Avenue planning.",
      `Scenario: ${scenario.label}`,
      `Input query: ${scenario.description}`,
      `Region: ${scenario.region}`,
      `Quantity: ${scenario.quantity} ${scenario.quantityUnit}`,
      "",
      "CWICR cost-search JSON:",
      JSON.stringify(payload),
      "",
      "Return exactly 4 concise bullets:",
      "1) best match and why",
      `2) budget estimate for ${scenario.quantity} ${scenario.quantityUnit}`,
      "3) confidence/risk note based on score quality",
      "4) one next data check before BOQ sync",
    ].join("\n");

    const args = [
      "meta/harness/bin/llm",
      `--backend=mlx-lm:${BONSAI_4B_MODEL}`,
      "--timeout=120",
      prompt,
    ];
    const { stdout, stderr } = await execFileAsync("python3", args, {
      cwd: process.cwd(),
      maxBuffer: 1024 * 1024 * 4,
    });
    const output = stderr ? `${stdout}\n${stderr}` : stdout;

    return {
      ok: true,
      scenario,
      verification: {
        status: "passed",
        message: `Reliable CWICR match found above score threshold ${MIN_RELIABLE_SCORE.toFixed(2)}.`,
      },
      confidence,
      estimate,
      rows,
      note: cleanModelOutput(output),
      model: BONSAI_4B_MODEL,
      command: `python3 ${args.join(" ")}`,
      rawOutput: output,
    };
  });
