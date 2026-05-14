export interface RuntimeOutcome {
  id: string;
  runId: string;
  summary: string;
  status: "completed" | "failed";
  createdAt: string;
}
