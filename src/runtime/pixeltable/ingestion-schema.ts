export interface IngestionSchema {
  contractId: string
  source: string
  target: string
}

export const runtimeIngestionSchema: IngestionSchema = {
  contractId: 'pixeltable.runtime_ledger.v1',
  source: 'runtime-runs',
  target: 'pixeltable',
}
