export interface RuntimeArtifact {
  id: string;
  runId: string;
  threadId: string;
  path: string;
  sha256: string;
  mimeType?: string;
  createdAt: string;
}
